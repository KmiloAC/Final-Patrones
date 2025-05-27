# models/state.py
from abc import ABC, abstractmethod
class EstadoPedido(ABC):
    @abstractmethod
    def procesar_pago(self, pedido): pass

    @abstractmethod
    def cancelar(self, pedido): pass

    @abstractmethod
    def confirmar(self, pedido): pass

    @abstractmethod
    def emitir_entradas(self, pedido): pass

    @abstractmethod
    def solicitar_reembolso(self, pedido): pass

class Pedido:
    def __init__(self, id, items, metodo_pago, total):
        self.id = id
        self.items = items
        self.metodo_pago = metodo_pago
        self.total = total
        self.mensaje_error = ""
        self._estado_actual = EstadoPedidoPendiente()

    def establecer_estado(self, nuevo_estado):
        self._estado_actual = nuevo_estado

    def procesar_pago(self):
        self._estado_actual.procesar_pago(self)

    def cancelar(self):
        self._estado_actual.cancelar(self)

    def confirmar(self):
        self._estado_actual.confirmar(self)

    def emitir_entradas(self):
        self._estado_actual.emitir_entradas(self)

    def solicitar_reembolso(self):
        self._estado_actual.solicitar_reembolso(self)

class EstadoPedidoPendiente(EstadoPedido):
    def procesar_pago(self, pedido):
        print("Procesando pago...")
        pedido.establecer_estado(EstadoPedidoProcesandoPago())

    def cancelar(self, pedido):
        print("Pedido cancelado.")
        pedido.establecer_estado(EstadoPedidoCancelado())

    def confirmar(self, pedido):
        print("No se puede confirmar, aún no ha sido pagado.")

    def emitir_entradas(self, pedido):
        print("No se puede emitir entradas sin confirmar.")

    def solicitar_reembolso(self, pedido):
        print("No se puede reembolsar un pedido pendiente.")

class EstadoPedidoProcesandoPago(EstadoPedido):
    def procesar_pago(self, pedido):
        print("Ya se está procesando el pago...")

    def cancelar(self, pedido):
        print("Cancelando mientras se procesaba el pago.")
        pedido.establecer_estado(EstadoPedidoCancelado())

    def confirmar(self, pedido):
        print("Esperando confirmación de pago...")

    def emitir_entradas(self, pedido):
        print("Pago no confirmado aún.")

    def solicitar_reembolso(self, pedido):
        print("No se puede reembolsar sin pago confirmado.")

    def notificado_pago_exitoso(self, pedido):
        print("Pago exitoso.")
        pedido.establecer_estado(EstadoPedidoPagado())

    def notificado_pago_fallido(self, pedido, razon):
        print(f"Pago fallido: {razon}")
        pedido.mensaje_error = razon
        pedido.establecer_estado(EstadoPedidoFallido())

class EstadoPedidoPagado(EstadoPedido):
    def procesar_pago(self, pedido):
        print("El pedido ya fue pagado.")

    def cancelar(self, pedido):
        print("No se puede cancelar después de pagar.")

    def confirmar(self, pedido):
        print("Confirmando pedido...")
        pedido.establecer_estado(EstadoPedidoConfirmado())

    def emitir_entradas(self, pedido):
        print("Debe confirmar primero el pedido.")

    def solicitar_reembolso(self, pedido):
        print("Reembolsando...")
        pedido.establecer_estado(EstadoPedidoReembolsado())

class EstadoPedidoConfirmado(EstadoPedido):
    def procesar_pago(self, pedido):
        print("El pedido ya fue procesado.")

    def cancelar(self, pedido):
        print("No se puede cancelar después de confirmar.")

    def confirmar(self, pedido):
        print("Ya está confirmado.")

    def emitir_entradas(self, pedido):
        print("Entradas emitidas.")

    def solicitar_reembolso(self, pedido):
        print("Solicitando reembolso...")
        pedido.establecer_estado(EstadoPedidoReembolsado())

class EstadoPedidoCancelado(EstadoPedido):
    def procesar_pago(self, pedido):
        print("No se puede procesar un pedido cancelado.")

    def cancelar(self, pedido):
        print("Ya está cancelado.")

    def confirmar(self, pedido):
        print("No se puede confirmar un pedido cancelado.")

    def emitir_entradas(self, pedido):
        print("No se pueden emitir entradas para un pedido cancelado.")

    def solicitar_reembolso(self, pedido):
        print("Pedido cancelado, nada que reembolsar.")

class EstadoPedidoFallido(EstadoPedido):
    def procesar_pago(self, pedido):
        print("Reintentando pago...")
        pedido.establecer_estado(EstadoPedidoProcesandoPago())

    def cancelar(self, pedido):
        print("Cancelando pedido fallido...")
        pedido.establecer_estado(EstadoPedidoCancelado())

    def confirmar(self, pedido):
        print("No se puede confirmar un pago fallido.")

    def emitir_entradas(self, pedido):
        print("No se pueden emitir entradas.")

    def solicitar_reembolso(self, pedido):
        print("No se puede reembolsar, el pago falló.")

class EstadoPedidoReembolsado(EstadoPedido):
    def procesar_pago(self, pedido):
        print("El pedido ya fue reembolsado.")

    def cancelar(self, pedido):
        print("Ya está reembolsado.")

    def confirmar(self, pedido):
        print("No se puede confirmar un pedido reembolsado.")

    def emitir_entradas(self, pedido):
        print("Entradas no disponibles, fue reembolsado.")

    def solicitar_reembolso(self, pedido):
        print("Ya fue reembolsado.")