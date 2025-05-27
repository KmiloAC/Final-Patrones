# app.py

import logging
from flask import Flask, render_template, request, redirect, url_for
from typing import List # Importar List

# Importar el controlador y las clases necesarias de models
from controller.controller import PedidoController
from models.chain import ItemConfiteria, EstadoPedido # Importar ItemConfiteria y EstadoPedido
from models.iterator import AsientosCollection  # Añadir esta importación

# Configurar logging (para ver los mensajes de los manejadores y el controlador)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # Logger para el módulo app.py

app = Flask(__name__)
# Nota: Para una aplicación real, el secret_key es necesario para sesiones,
# pero para este ejemplo académico simple, no usaremos sesiones complejas.
# app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'

# Instancia del controlador. Para este ejemplo académico, mantenemos una instancia global.
# En una app más compleja, esto se manejaría por usuario o sesión.
controller = PedidoController()

# Reemplazar la lista ALL_SEATS con la colección de asientos
asientos_collection = AsientosCollection()
ALL_SEATS = []
iterator = asientos_collection.crear_iterator_por_fila()
while iterator.has_next():
    ALL_SEATS.append(iterator.next())

@app.route('/historial')
def ver_historial():
    """Muestra el historial de compras"""
    historial_pedidos = getattr(controller, 'historial_pedidos', [])
    return render_template(
        'historial.html',
        historial_pedidos=historial_pedidos,
        EstadoPedido=EstadoPedido
    )

@app.route('/finish_process')
def finish_process():
    """Ruta para terminar el proceso y volver al inicio"""
    if controller.pedido_actual and controller.pedido_actual.estado == EstadoPedido.COMPLETADO:
        if not hasattr(controller, 'historial_pedidos'):
            controller.historial_pedidos = []
        controller.historial_pedidos.append(controller.pedido_actual)
    
    try:
        controller.reiniciar()
    except Exception as e:
        logger.error(f"Error al reiniciar el controlador: {e}")
    
    return redirect(url_for('index'))

@app.route('/')
def index():
    """Renderiza la página principal siempre comenzando en selección de asientos"""
    # Siempre empezamos en selección a menos que se especifique otra sección
    active_section = request.args.get('active_section', 'seleccion')
    
    estado_asientos = controller.obtener_estado_asientos()
    asientos_seleccionados_ids = estado_asientos.get("asientos", [])
    
    # Obtener historial solo para saber si mostramos el botón
    historial_pedidos = getattr(controller, 'historial_pedidos', [])
    
    return render_template(
        'index.html',
        all_seats=ALL_SEATS,
        selected_seats=asientos_seleccionados_ids,
        sold_seats=asientos_collection.asientos_vendidos,
        historial_pedidos=historial_pedidos,  # Solo para mostrar/ocultar botón
        active_section=active_section,
        pedido_info=controller.pedido_actual if controller.pedido_actual else None,
        error_message=request.args.get('error', None),
        success_message=request.args.get('message', None)  # Añadido para mensajes de éxito
    )

@app.route('/select/<string:asiento_id>')
def select_seat(asiento_id):
    """Ruta para seleccionar un asiento."""
    # Verificar si el asiento ya está vendido
    if asientos_collection.esta_vendido(asiento_id):
        return redirect(url_for('index', error="Este asiento ya está vendido", active_section='seleccion'))
    
    estado_actual = controller.obtener_estado_asientos()
    asientos_seleccionados = estado_actual.get("asientos", [])
    
    if len(asientos_seleccionados) >= 10 and asiento_id not in asientos_seleccionados:
        return redirect(url_for('index', error="No puedes seleccionar más de 10 asientos"))
    
    asientos_collection.marcar_asiento_ocupado(asiento_id)
    controller.seleccionar_asiento(asiento_id)
    return redirect(url_for('index', active_section='seleccion'))

@app.route('/deselect/<string:asiento_id>')
def deselect_seat(asiento_id):
    """Ruta para deseleccionar un asiento."""
    asientos_collection.desmarcar_asiento_ocupado(asiento_id)  # Desmarcar como ocupado
    controller.deseleccionar_asiento(asiento_id)
    return redirect(url_for('index')) # Redirige de vuelta a la página principal

@app.route('/undo')
def undo():
    """Ruta para deshacer la última acción de selección/deselección."""
    controller.deshacer()
    return redirect(url_for('index'))

@app.route('/redo')
def redo():
    """Ruta para rehacer la última acción deshecha."""
    controller.rehacer()
    return redirect(url_for('index'))

@app.route('/process_order', methods=['POST'])
def process_order():
    """Ruta para iniciar el procesamiento del pedido a través de la cadena."""
    metodo_pago = request.form.get('metodo_pago', 'efectivo')
    cupon = request.form.get('cupon')
    add_confiteria = request.form.get('add_confiteria') == 'yes' # Check if checkbox is checked

    # Crear items de confitería si se seleccionó (ejemplo simple)
    items_confiteria: List[ItemConfiteria] = []
    if add_confiteria:
        # Ejemplo: 2 Palomitas grandes a 5.00 cada una
        items_confiteria.append(ItemConfiteria("Palomitas Grandes", 2, 5.00))
        logger.info("Añadiendo items de confitería de ejemplo.")


    logger.info(f"Recibida solicitud para procesar pedido con método {metodo_pago}, cupón {cupon}, confitería: {add_confiteria}")

    # Iniciar el proceso de pedido usando el controlador (que llama a la cadena)
    processed_pedido = controller.iniciar_proceso_pedido(
        metodo_pago=metodo_pago,
        items_confiteria=items_confiteria,
        cupon=cupon
    )

    # Marcar los asientos como vendidos después de procesar el pedido exitosamente
    if processed_pedido and processed_pedido.estado == EstadoPedido.COMPLETADO:
        estado_actual = controller.obtener_estado_asientos()
        asientos_seleccionados = estado_actual.get("asientos", [])
        asientos_collection.confirmar_venta_asientos(asientos_seleccionados)
    
    # El resultado del procesamiento ya está en controller.pedido_actual
    # Redirigimos a la página principal mostrando la sección de confirmación
    return redirect(url_for('index', active_section='confirmacion'))

@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    """Ruta para cancelar el pedido actual."""
    controller.cancelar_pedido()
    return redirect(url_for('index'))

@app.route('/refund_order', methods=['POST'])
def refund_order():
    """Ruta para solicitar reembolso para el pedido actual o desde historial"""
    try:
        pedido_id = request.form.get('pedido_id')  # Obtener ID del pedido si viene del historial
        
        if controller.solicitar_reembolso(pedido_id):
            # Si el reembolso fue exitoso, liberar los asientos
            if controller.pedido_actual.items_boletas:  # Verificar si hay asientos para liberar
                asientos_a_liberar = [item.asiento_id for item in controller.pedido_actual.items_boletas]
                asientos_collection.desmarcar_asientos_vendidos(asientos_a_liberar)
            
            if pedido_id:
                return redirect(url_for('ver_historial', message="Reembolso procesado exitosamente"))
            return redirect(url_for('index', message="Reembolso procesado exitosamente"))
        else:
            error_msg = (controller.pedido_actual.mensaje_error 
                        if controller.pedido_actual 
                        else "No se pudo procesar el reembolso")
            if pedido_id:
                return redirect(url_for('ver_historial', error=error_msg))
            return redirect(url_for('index', error=error_msg))
    except Exception as e:
        logger.error(f"Error al procesar reembolso: {str(e)}")
        if pedido_id:
            return redirect(url_for('ver_historial', error="Error inesperado al procesar el reembolso"))
        return redirect(url_for('index', error="Error inesperado al procesar el reembolso"))

@app.route('/next_section/<string:section>')
def next_section(section):
    """Ruta para cambiar entre secciones"""
    estado_actual = controller.obtener_estado_asientos()
    asientos_seleccionados = estado_actual.get("asientos", [])
    
    if section == 'pago' and not asientos_seleccionados:
        return redirect(url_for('index', error="Debes seleccionar al menos un asiento", active_section='seleccion'))
    
    # Validar que no se pueda ir a confirmación directamente
    if section == 'confirmacion':
        return redirect(url_for('index', active_section='pago'))
    
    return redirect(url_for('index', active_section=section))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)