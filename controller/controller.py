# controller/controller.py

# Importamos las clases Memento (existentes)
from models.memento import SeleccionAsientos, GestorHistorialSeleccion

# Importamos las clases Chain of Responsibility (y las nuevas clases Item)
from models.chain import (
    Pedido as ChainPedido, # Renombramos para evitar conflicto si había otro Pedido
    EstadoPedido,
    ManejadorValidacionStock,
    ManejadorCalculoPreciosYImpuestos,
    ManejadorAplicacionDescuentos,
    ManejadorProcesamientoPago,
    ManejadorGeneracionEntradas,
    ManejadorActualizacionInventario,
    ItemBoleta,      # Importamos las nuevas clases Item
    ItemConfiteria
)

import logging
from typing import List # Importar List si no está

logger = logging.getLogger(__name__)

class PedidoController:
    def __init__(self):
        # --- Memento Pattern (Existente) ---
        self.seleccionador = SeleccionAsientos()
        self.historial = GestorHistorialSeleccion()
        # Guardamos el primer estado vacío
        self.historial.guardar(self.seleccionador.crear_memento())

        # --- Chain of Responsibility Pattern ---
        # Atributo para guardar el pedido de la cadena de responsabilidad
        self.pedido_actual: ChainPedido = None

        # >> Contador simple para IDs de pedidos - Solución al AttributeError <<
        self.pedido_counter = 0 # Inicializamos el contador para generar IDs secuenciales

        # Construir la cadena de manejadores
        self.primer_manejador = ManejadorValidacionStock()
        manejador_precios = ManejadorCalculoPreciosYImpuestos()
        manejador_descuentos = ManejadorAplicacionDescuentos()
        manejador_pago = ManejadorProcesamientoPago()
        manejador_entradas = ManejadorGeneracionEntradas()
        manejador_inventario = ManejadorActualizacionInventario()

        # Enlazar los manejadores en el orden deseado
        self.primer_manejador.establecer_siguiente(manejador_precios)\
                             .establecer_siguiente(manejador_descuentos)\
                             .establecer_siguiente(manejador_pago)\
                             .establecer_siguiente(manejador_entradas)\
                             .establecer_siguiente(manejador_inventario) # El último manejador


        logger.info("PedidoController inicializado con Chain of Responsibility.")


    # --- Métodos de Selección y Deshacer/Rehacer (Memento Pattern - Existente) ---
    def seleccionar_asiento(self, asiento_id):
        self.seleccionador.seleccionar_asiento(asiento_id)
        self.historial.guardar(self.seleccionador.crear_memento())
        logger.info(f"Asiento {asiento_id} seleccionado.")

    def deseleccionar_asiento(self, asiento_id):
        self.seleccionador.deseleccionar_asiento(asiento_id)
        self.historial.guardar(self.seleccionador.crear_memento())
        logger.info(f"Asiento {asiento_id} deseleccionado.")

    def deshacer(self):
        memento = self.historial.deshacer()
        if memento:
            self.seleccionador.restaurar_desde_memento(memento)
            logger.info("Deshaciendo última selección.")
        else:
            logger.warning("No hay más acciones para deshacer.")


    def rehacer(self):
        memento = self.historial.rehacer()
        if memento:
            self.seleccionador.restaurar_desde_memento(memento)
            logger.info("Rehaciendo última selección.")
        else:
            logger.warning("No hay más acciones para rehacer.")

    # --- Método para iniciar el Proceso con Chain of Responsibility ---
    def iniciar_proceso_pedido(self, metodo_pago="efectivo", items_confiteria: List[ItemConfiteria] = None, cupon: str = None):
        """
        Recopila la selección actual, crea un objeto Pedido (de chain.py)
        y lo pasa al inicio de la cadena de responsabilidad para su procesamiento.
        """
        estado_seleccion = self.seleccionador.obtener_estado_actual()
        asientos_seleccionados_ids = estado_seleccion.get("asientos", [])

        # Si no hay nada seleccionado y no hay items de confitería, no creamos pedido.
        if not asientos_seleccionados_ids and (items_confiteria is None or len(items_confiteria) == 0):
            logger.warning("No hay asientos seleccionados ni items de confitería. No se crea el pedido.")
            self.pedido_actual = None
            return None # No se crea el pedido si está vacío

        # Convertir IDs de asientos a objetos ItemBoleta
        items_boletas = [ItemBoleta(asiento_id=asiento_id) for asiento_id in asientos_seleccionados_ids]

        # >> Incrementar el contador de pedidos para el nuevo ID <<
        self.pedido_counter += 1

        # Crear la instancia del Pedido usando la clase de models.chain
        # Proporcionamos una lista vacía para items_confiteria si no se pasa nada
        # Usamos el contador para generar un ID único
        self.pedido_actual = ChainPedido(
            # id=f"PED-{len(self.historial._historial) + 1}-{abs(hash(''.join(asientos_seleccionados_ids)) % 1000)}", # Línea anterior con error
            id=f"PED-{self.pedido_counter}-{abs(hash(''.join(asientos_seleccionados_ids or '')) % 1000)}", # >> LÍNEA CORREGIDA <<
            items_boletas=items_boletas,
            items_confiteria=items_confiteria if items_confiteria is not None else [],
            metodo_pago=metodo_pago,
            cupon_aplicado=cupon
        )

        logger.info(f"Pedido Chain creado: {self.pedido_actual}")

        # Iniciar el procesamiento pasando el pedido al primer manejador de la cadena
        logger.info(f"Iniciando cadena de procesamiento para pedido {self.pedido_actual.id}...")
        self.primer_manejador.procesar_pedido(self.pedido_actual)
        logger.info(f"Cadena de procesamiento finalizada para pedido {self.pedido_actual.id}.")

        # --- Reaccionar al resultado del procesamiento de la cadena ---
        # El controlador verifica el estado final del pedido después de que la cadena ha terminado
        if self.pedido_actual.estado == EstadoPedido.COMPLETADO:
            logger.info(f"Pedido {self.pedido_actual.id} procesado exitosamente (COMPLETADO).")
            # Opcional: Aquí podrías agregar lógica para limpiar la selección actual
            # en self.seleccionador si quieres que una vez completado el pedido,
            # la UI de selección se reinicie para una nueva compra.
            # Ejemplo: self.seleccionador.limpiar_seleccion()
            #          self.historial.guardar(self.seleccionador.crear_memento()) # Guardar estado vacío después de limpiar
            # Esto depende del flujo de usuario deseado.

        elif self.pedido_actual.estado == EstadoPedido.FALLIDO:
            logger.error(f"Pedido {self.pedido_actual.id} falló durante el procesamiento. Razón: {self.pedido_actual.mensaje_error}")
            # El controlador puede informar al usuario del fallo y el motivo (ya se hace en la UI).
            # La selección en el Seleccionador (Memento) permanece para que el usuario pueda corregir.

        else:
             logger.warning(f"Pedido {self.pedido_actual.id} terminó con estado inesperado: {self.pedido_actual.estado.value}")


        return self.pedido_actual # Retornar el objeto Pedido con su estado final (con el resultado del proceso)

    # --- Métodos para Cancelar/Reembolsar (ahora interactúan con el objeto ChainPedido) ---
    # Nota: Estos métodos no usan la cadena principal, actúan directamente sobre el estado del Pedido
    # podrías implementar cadenas separadas para cancelar/reembolsar si la lógica fuera compleja.

    def cancelar_pedido(self):
        """Cancela el pedido actual si es posible."""
        if self.pedido_actual:
            # Llama al método cancelar que añadimos a la clase ChainPedido
            self.pedido_actual.cancelar()
            logger.info(f"Solicitud de cancelación para pedido {self.pedido_actual.id} procesada.")
        else:
            logger.warning("No hay pedido actual para cancelar.")


    def solicitar_reembolso(self):
        """Solicita reembolso para el pedido actual si es posible."""
        if self.pedido_actual:
            # Llama al método solicitar_reembolso que añadimos a la clase ChainPedido
            self.pedido_actual.solicitar_reembolso()
            logger.info(f"Solicitud de reembolso para pedido {self.pedido_actual.id} procesada.")
        else:
            logger.warning("No hay pedido actual para solicitar reembolso.")


    # --- Métodos que ya no son llamados directamente para el flujo principal ---
    # La lógica de estos métodos ahora está en los Manejadores de la cadena.
    # Los mantenemos comentados para referencia, pero su lógica está en los manejadores.
    # def procesar_pago(self):
    #     # Lógica ahora en ManejadorProcesamientoPago
    #     if self.pedido_actual:
    #         # self.pedido_actual.procesar_pago() # <- Esto ya no se llama así
    #         logger.info("Lógica de procesamiento de pago manejada por la Chain.")
    #     pass # O eliminar completamente

    # def confirmar_pedido(self):
    #     # Lógica ahora en ManejadorActualizacionInventario (marcando como COMPLETO)
    #     if self.pedido_actual:
    #         # self.pedido_actual.confirmar() # <- Esto ya no se llama así
    #         logger.info("Lógica de confirmación de pedido manejada por la Chain.")
    #     pass # O eliminar completamente

    # def emitir_entradas(self):
    #     # Lógica ahora en ManejadorGeneracionEntradas
    #     if self.pedido_actual:
    #         # self.pedido_actual.emitir_entradas() # <- Esto ya no se llama así
    #         logger.info("Lógica de emisión de entradas manejada por la Chain.")
    #     pass # O eliminar completamente


    # --- Método Existente ---
    def obtener_estado_asientos(self):
        """Devuelve el estado actual de la selección de asientos desde el Memento."""
        return self.seleccionador.obtener_estado_actual()