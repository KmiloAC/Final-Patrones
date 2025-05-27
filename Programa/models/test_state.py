from state import Pedido, EstadoPedidoProcesandoPago

# Crear pedido de prueba
pedido = Pedido(id="123", items=["Boleta A", "Combo 1"], metodo_pago="Tarjeta", total=25.0)

# Estado inicial
print("Estado inicial: Pendiente")
pedido.procesar_pago()

# Simular que el sistema externo notifica que el pago fue exitoso
if isinstance(pedido._estado_actual, EstadoPedidoProcesandoPago):
    pedido._estado_actual.notificado_pago_exitoso(pedido)

# Confirmar
pedido.confirmar()

# Emitir entradas
pedido.emitir_entradas()

# Solicitar reembolso
pedido.solicitar_reembolso()
