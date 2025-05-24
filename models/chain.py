# models/chain.py (Inicio del archivo)

import abc
import logging
from enum import Enum
from typing import List, Any # Usamos Any para simplificar ItemBoleta/Confiteria en este ejemplo

# Configuramos un logger para este módulo.
logger = logging.getLogger(__name__)

# --- Clases Placeholder para Items del Pedido ---
# Estas clases representan los elementos que componen un pedido (boletas, confitería).
# Son usadas por la clase Pedido y los manejadores.
class EstadoPedido(Enum):
    PENDIENTE = "PENDIENTE"
    VALIDANDO = "VALIDANDO"
    CALCULANDO_PRECIOS = "CALCULANDO_PRECIOS"
    APLICANDO_DESCUENTOS = "APLICANDO_DESCUENTOS"
    PROCESANDO_PAGO = "PROCESANDO_PAGO"
    PAGADO = "PAGADO"
    COMPLETADO = "COMPLETADO"
    FALLIDO = "FALLIDO"
    CANCELADO = "CANCELADO"
    REEMBOLSO_SOLICITADO = "REEMBOLSO_SOLICITADO"
    REEMBOLSO_PROCESADO = "REEMBOLSO_PROCESADO"
    REEMBOLSO_RECHAZADO = "REEMBOLSO_RECHAZADO"
class ItemBoleta:
    def __init__(self, asiento_id: str, precio: float = 10000.0): # Precio por defecto para ejemplo
        self.asiento_id = asiento_id
        self.precio = precio # Precio individual de la boleta

    def __str__(self):
        return f"Boleta(Asiento: {self.asiento_id}, Precio: {self.precio:.2f})"

class ItemConfiteria:
    def __init__(self, nombre: str, cantidad: int, precio_unitario: float):
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.precio = precio_unitario * cantidad # Precio total del item

    def __str__(self):
        return f"Confiteria(Nombre: {self.nombre}, Cantidad: {self.cantidad}, Subtotal: {self.precio:.2f})"


# --- Objeto Solicitud (Pedido) ---
# ... (el resto de tu clase Pedido existente) ...

class Pedido:
    def __init__(self, id: str, items_boletas: List[ItemBoleta], items_confiteria: List[ItemConfiteria], metodo_pago: str, cupon_aplicado: str = None):
        # ... (tu código __init__ existente) ...
        self.id = id
        self.items_boletas = items_boletas # Datos de las boletas (lista de ItemBoleta)
        self.items_confiteria = items_confiteria # Datos de la confitería (lista de ItemConfiteria)
        self.metodo_pago = metodo_pago
        self.cupon_aplicado = cupon_aplicado

        # Atributos que serán llenados por los manejadores
        self.subtotal = 0.0
        self.descuento_aplicado = 0.0
        self.impuestos = 0.0
        self.total_final = 0.0 # Este será actualizado por la cadena

        self.estado = EstadoPedido.PENDIENTE
        self.mensaje_error = None

    def set_estado(self, estado: EstadoPedido):
        logger.info(f"Pedido {self.id}: Cambiando estado a {estado.value}")
        self.estado = estado

    def set_error(self, mensaje: str):
        logger.error(f"Pedido {self.id}: !! ERROR: {mensaje} !!")
        self.mensaje_error = mensaje
        self.set_estado(EstadoPedido.FALLIDO)

    # --- Añadimos métodos básicos para Cancelar/Solicitar Reembolso ---
    # Estos simplemente cambian el estado del pedido
    def cancelar(self):
        if self.estado in [EstadoPedido.PENDIENTE, EstadoPedido.VALIDANDO, EstadoPedido.CALCULANDO_PRECIOS, EstadoPedido.APLICANDO_DESCUENTOS, EstadoPedido.PROCESANDO_PAGO]:
             logger.info(f"Pedido {self.id}: Cancelando pedido desde estado {self.estado.value}")
             self.set_estado(EstadoPedido.CANCELADO)
        else:
             logger.warning(f"Pedido {self.id}: No se puede cancelar el pedido en estado {self.estado.value}")

    def solicitar_reembolso(self):
        """Procesa la solicitud de reembolso del pedido"""
        if self.estado == EstadoPedido.COMPLETADO:
            logger.info(f"Pedido {self.id}: Procesando solicitud de reembolso")
            
            # Verificar si el pedido es elegible para reembolso (ejemplo: menos de 24h)
            if self._es_elegible_para_reembolso():
                self.set_estado(EstadoPedido.REEMBOLSO_SOLICITADO)
                
                # Simular proceso de reembolso con el método de pago original
                if self._procesar_reembolso():
                    self.set_estado(EstadoPedido.REEMBOLSO_PROCESADO)
                    logger.info(f"Pedido {self.id}: Reembolso procesado exitosamente")
                    return True
                else:
                    self.set_estado(EstadoPedido.REEMBOLSO_RECHAZADO)
                    self.set_error("No se pudo procesar el reembolso con el método de pago original")
                    return False
            else:
                self.set_estado(EstadoPedido.REEMBOLSO_RECHAZADO)
                self.set_error("Pedido no elegible para reembolso")
                return False
        else:
            logger.warning(f"Pedido {self.id}: No se puede solicitar reembolso en estado {self.estado.value}")
            self.set_error("Solo se pueden reembolsar pedidos completados")
            return False

    def _es_elegible_para_reembolso(self) -> bool:
        """Verifica si el pedido es elegible para reembolso"""
        # Aquí puedes agregar tu lógica de negocio
        # Por ejemplo: verificar tiempo transcurrido, estado de los asientos, etc.
        return True  # Para demo, siempre retornamos True

    def _procesar_reembolso(self) -> bool:
        """Procesa el reembolso con el método de pago original"""
        # Aquí iría la lógica real de reembolso con la pasarela de pago
        # Para la demo, simulamos éxito excepto para ciertos métodos de pago
        if self.metodo_pago == "efectivo":
            logger.warning(f"Pedido {self.id}: Reembolso en efectivo requiere proceso manual")
            return False
        return True

    def __str__(self):
        return f"Pedido(ID: {self.id}, Estado: {self.estado.value}, Total: {self.total_final:.2f}, Error: {self.mensaje_error})"


# --- Interfaz del Manejador ---
# Define la interfaz que todos los manejadores deben seguir.

class ManejadorPedido(abc.ABC):
    @abc.abstractmethod
    def establecer_siguiente(self, siguiente_manejador: 'ManejadorPedido'):
        """Establece el siguiente manejador en la cadena."""
        pass

    @abc.abstractmethod
    def procesar_pedido(self, pedido: Pedido):
        """Procesa la solicitud o la pasa al siguiente manejador."""
        pass

# --- Implementación Base Abstracta ---
# Proporciona funcionalidad común para los manejadores, como el enlace.

class BaseManejadorPedido(ManejadorPedido, abc.ABC):
    _siguiente_manejador: ManejadorPedido = None

    def establecer_siguiente(self, siguiente_manejador: ManejadorPedido):
        self._siguiente_manejador = siguiente_manejador
        return siguiente_manejador

    def _pasar_al_siguiente(self, pedido: Pedido):
        """Pasa la solicitud al siguiente manejador si existe."""
        # Solo pasamos si el pedido no ha fallado en un manejador anterior
        if pedido.estado != EstadoPedido.FALLIDO and self._siguiente_manejador:
            logger.debug(f"  {self.__class__.__name__} pasa el pedido {pedido.id} al siguiente manejador ({self._siguiente_manejador.__class__.__name__}).")
            self._siguiente_manejador.procesar_pedido(pedido)
        elif pedido.estado != EstadoPedido.FALLIDO and not self._siguiente_manejador:
             logger.info(f"  {self.__class__.__name__} es el último manejador en la cadena para el pedido {pedido.id}. Procesamiento finalizado.")
             # El último manejador exitoso debería marcar como completado si no hubo fallo
             # Esto lo moveremos al ManejadorActualizacionInventario.
        else:
             logger.debug(f"  Pedido {pedido.id} ya falló. Deteniendo la cadena en {self.__class__.__name__}.")


    # El método procesar_pedido(self, pedido: Pedido) es abstracto y debe ser implementado
    # por las subclases concretas.


# --- Manejadores Concretos (Lógica de Negocio) ---

class ManejadorValidacionStock(BaseManejadorPedido):
    def procesar_pedido(self, pedido: Pedido):
        if pedido.estado == EstadoPedido.FALLIDO:
            logger.warning(f"ManejadorValidacionStock: Saltando procesamiento para pedido {pedido.id} (ya falló).")
            return

        pedido.set_estado(EstadoPedido.VALIDANDO)
        logger.info(f"ManejadorValidacionStock: Validando stock y asientos para pedido {pedido.id}")

        # --- Lógica de validación real ---
        stock_suficiente = True # <<-- Aquí va la lógica real de consulta a BD/inventario
        # Ejemplo: if not verificar_stock(pedido.items_confiteria) or not verificar_asientos(pedido.items_boletas): stock_suficiente = False
        # --- Fin Lógica ---

        if stock_suficiente:
            logger.info(f"ManejadorValidacionStock: Validación de stock/asientos exitosa para pedido {pedido.id}")
            # Pasa al siguiente solo si es exitoso
            self._pasar_al_siguiente(pedido)
        else:
            pedido.set_error("Stock o asientos insuficientes.")
            # No llama a _pasar_al_siguiente(), la cadena se detiene aquí


class ManejadorCalculoPreciosYImpuestos(BaseManejadorPedido):
     def procesar_pedido(self, pedido: Pedido):
        if pedido.estado == EstadoPedido.FALLIDO:
            logger.warning(f"ManejadorCalculoPreciosYImpuestos: Saltando procesamiento para pedido {pedido.id} (ya falló).")
            return

        pedido.set_estado(EstadoPedido.CALCULANDO_PRECIOS) # Nuevo estado
        logger.info(f"ManejadorCalculoPreciosYImpuestos: Calculando precios base e impuestos para pedido {pedido.id}")

        # --- Lógica de cálculo de precios e impuestos ---
        # Calcular subtotal base (antes de descuentos)
        subtotal_boletas = sum(item.precio for item in pedido.items_boletas) if pedido.items_boletas else 0.0 # Asume que ItemBoleta tiene atributo precio
        subtotal_confiteria = sum(item.precio * item.cantidad for item in pedido.items_confiteria) if pedido.items_confiteria else 0.0 # Asume que ItemConfiteria tiene precio y cantidad

        pedido.subtotal = subtotal_boletas + subtotal_confiteria

        # Calcular impuestos sobre el subtotal (o sobre subtotal - descuentos, dependiendo de la regla)
        # Si los impuestos se aplican después de descuentos, esta lógica podría ir en un manejador posterior.
        # Para este ejemplo, calculamos impuestos sobre el subtotal inicial.
        porcentaje_impuestos = 0.19 # Ejemplo: 19%
        pedido.impuestos = pedido.subtotal * porcentaje_impuestos

        # El total inicial antes de descuentos aplicados por el siguiente manejador
        pedido.total_final = pedido.subtotal + pedido.impuestos

        logger.info(f"  Subtotal calculado: {pedido.subtotal:.2f}, Impuestos: {pedido.impuestos:.2f}. Total inicial: {pedido.total_final:.2f}")
        # --- Fin Lógica ---

        self._pasar_al_siguiente(pedido) # Siempre pasa al siguiente


class ManejadorAplicacionDescuentos(BaseManejadorPedido): # Colocado DESPUES del cálculo base de precios
     def procesar_pedido(self, pedido: Pedido):
        if pedido.estado == EstadoPedido.FALLIDO:
            logger.warning(f"ManejadorAplicacionDescuentos: Saltando procesamiento para pedido {pedido.id} (ya falló).")
            return

        pedido.set_estado(EstadoPedido.APLICANDO_DESCUENTOS) # Nuevo estado
        logger.info(f"ManejadorAplicacionDescuentos: Aplicando descuentos para pedido {pedido.id}")

        # --- Lógica de descuento real ---
        descuento_calculado = 0.0

        if pedido.cupon_aplicado == "CINE20":
            # Aplicar 20% sobre el subtotal ANTES de impuestos (si esa es la regla)
            descuento_cupon = pedido.subtotal * 0.20
            descuento_calculado += descuento_cupon
            logger.info(f"  Aplicado cupón 'CINE20': {descuento_cupon:.2f} de descuento.")

        # --- Otras reglas de descuento ---
        # Ejemplo: descuento fijo si compra confitería
        if len(pedido.items_confiteria) > 0:
             descuento_confiteria = 2.0
             descuento_calculado += descuento_confiteria
             logger.info(f"  Aplicado descuento por confitería: {descuento_confiteria:.2f}.")
        # --- Fin Lógica ---

        pedido.descuento_aplicado = descuento_calculado
        pedido.total_final -= descuento_calculado # Restar el descuento del total

        if descuento_calculado > 0:
             logger.info(f"  Total de descuentos aplicados: {pedido.descuento_aplicado:.2f}. Nuevo Total Final: {pedido.total_final:.2f}")
        else:
             logger.info(f"  No se aplicaron descuentos al pedido {pedido.id}. Total Final sin cambios: {pedido.total_final:.2f}")


        self._pasar_al_siguiente(pedido) # Siempre pasa al siguiente


class ManejadorProcesamientoPago(BaseManejadorPedido):
    def procesar_pedido(self, pedido: Pedido):
        if pedido.estado == EstadoPedido.FALLIDO:
            logger.warning(f"ManejadorProcesamientoPago: Saltando procesamiento para pedido {pedido.id} (ya falló).")
            return

        # Asegurarse de que el total final esté calculado ANTES de intentar pagar
        # Asumimos que ManejadorCalculoPreciosYImpuestos y ManejadorAplicacionDescuentos
        # ya se ejecutaron y actualizaron pedido.total_final.

        if pedido.total_final <= 0:
             logger.warning(f"ManejadorProcesamientoPago: Pedido {pedido.id} tiene total_final <= 0 ({pedido.total_final:.2f}). Saltando procesamiento de pago real.")
             # Si el total es 0 o menos, no hay pago externo que procesar.
             # Lo consideramos como si el pago hubiera sido exitoso (implícitamente).
             pedido.set_estado(EstadoPedido.PAGADO)
             self._pasar_al_siguiente(pedido) # Continuar la cadena (ej. para generación de entradas/inventario)
             return


        pedido.set_estado(EstadoPedido.PROCESANDO_PAGO)
        logger.info(f"ManejadorProcesamientoPago: Procesando pago '{pedido.metodo_pago}' por {pedido.total_final:.2f} para pedido {pedido.id}")

        # --- Lógica de procesamiento de pago real ---
        pago_exitoso = True
        error_pago_detalle = None

        # Simulación de fallo por método de pago o comunicación con pasarela
        if pedido.metodo_pago == "Tarjeta rechazada":
            pago_exitoso = False
            error_pago_detalle = "Simulación: Tarjeta rechazada."
            logger.error(f"  Simulando pago fallido para pedido {pedido.id} con método '{pedido.metodo_pago}'.")
        # <<-- Aquí iría la llamada REAL a la pasarela de pago externa
        # else:
        #     try:
        #        resultado_pago = pasarela_pago.procesar(pedido.metodo_pago, pedido.total_final)
        #        if not resultado_pago.es_exitoso():
        #           pago_exitoso = False
        #           error_pago_detalle = resultado_pago.mensaje_error()
        #     except Exception as e:
        #        pago_exitoso = False
        #        error_pago_detalle = f"Error de comunicación con pasarela: {e}"

        # --- Fin Lógica ---

        if pago_exitoso:
            pedido.set_estado(EstadoPedido.PAGADO)
            self._pasar_al_siguiente(pedido) # Pasa al siguiente solo si el pago fue exitoso
        else:
            # Construir el mensaje de error de forma segura
            error_message = "Pago rechazado o fallido."
            if error_pago_detalle:
                 error_message += f" Detalle: {error_pago_detalle}"
            pedido.set_error(error_message)
            # No llama a _pasar_al_siguiente() si el pago falló


class ManejadorGeneracionEntradas(BaseManejadorPedido):
    def procesar_pedido(self, pedido: Pedido):
        # Solo procesar si el estado es PAGADO
        if pedido.estado != EstadoPedido.PAGADO:
            if pedido.estado != EstadoPedido.FALLIDO:
                 logger.warning(f"ManejadorGeneracionEntradas: Saltando generación de entradas para pedido {pedido.id} (estado no es PAGADO). Estado actual: {pedido.estado.value}")
            return # No procesar si no está en el estado correcto o si ya falló

        logger.info(f"ManejadorGeneracionEntradas: Generando entradas para pedido {pedido.id}")

        # --- Lógica de generación real ---
        tiene_boletas = len(pedido.items_boletas) > 0
        if tiene_boletas:
            logger.info(f"  Generando códigos/tickets para {len(pedido.items_boletas)} boletas.")
            # <<-- Aquí iría la lógica para crear códigos únicos, guardar en BD, asociar al usuario/pedido
        else:
             logger.info("  No hay boletas en este pedido, saltando generación específica de entradas.")
        # --- Fin Lógica ---

        # Asumimos que la generación siempre es exitosa si llegamos a este punto con estado PAGADO.
        # Si la generación pudiera fallar, deberíamos manejar ese error aquí y llamar a pedido.set_error().
        self._pasar_al_siguiente(pedido)


class ManejadorActualizacionInventario(BaseManejadorPedido):
    def procesar_pedido(self, pedido: Pedido):
        # Solo actualizar si se pagó.
        if pedido.estado != EstadoPedido.PAGADO:
             # Si llegó aquí y no está PAGADO, es que falló un manejador anterior,
             # o hubo un error de flujo. Simplemente no hacemos la actualización exitosa.
             if pedido.estado != EstadoPedido.FALLIDO:
                logger.warning(f"ManejadorActualizacionInventario: Saltando actualización de inventario para pedido {pedido.id} (estado no es PAGADO). Estado actual: {pedido.estado.value}")
             # Si el pedido ya falló, simplemente salimos.
             return

        logger.info(f"ManejadorActualizacionInventario: Actualizando inventario y asientos para pedido {pedido.id}")

        # --- Lógica de actualización real ---
        logger.info(f"  Descontando items de confitería: {len(pedido.items_confiteria)} items.")
        logger.info(f"  Marcando asientos como vendidos: {len(pedido.items_boletas)} asientos.")
        # <<-- Aquí iría la interacción con los sistemas de inventario y gestión de asientos
        # --- Fin Lógica ---

        # Si la actualización de inventario puede fallar, deberíamos manejar ese error aquí
        # y llamar a pedido.set_error().
        # Para este ejemplo, asumimos que si llegamos aquí, la actualización es exitosa.

        # Este es el último paso exitoso del procesamiento
        # Si llegamos aquí y el estado es PAGADO, significa que todos los pasos
        # anteriores fueron exitosos. Ahora marcamos como COMPLETO.
        if pedido.estado == EstadoPedido.PAGADO:
             pedido.set_estado(EstadoPedido.COMPLETADO)
             logger.info(f"Pedido {pedido.id}: Procesamiento COMPLETO y exitoso.")


        # Aunque es el último, llamamos a pasar_al_siguiente para mantener la uniformidad.
        # El método base verificará que no hay siguiente y registrará el fin.
        self._pasar_al_siguiente(pedido)


# --- Nota sobre el Cliente/Orquestación ---
# Las clases anteriores definen el MODELO (el patrón y las entidades).
# La lógica para:
# 1. Crear instancias de los manejadores concretos.
# 2. Enlazar los manejadores para construir la cadena.
# 3. Crear una instancia del objeto Pedido (DTO).
# 4. Llamar a procesar_pedido() en el primer manejador de la cadena.
# 5. Examinar el estado final del Pedido (devuelto por la cadena) y actuar en consecuencia.
# ... ESTA LÓGICA DE ORQUESTACIÓN DEBE RESIDIR FUERA de este archivo (en un Servicio, Controlador, etc.).