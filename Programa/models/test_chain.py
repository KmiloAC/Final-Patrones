
# test_chain.py

from chain import (
    Pedido,
    ManejadorValidacionStock,
    ManejadorAplicacionDescuentos,
    ManejadorCalculoPreciosYImpuestos,
    ManejadorProcesamientoPago,
    ManejadorGeneracionEntradas,
    ManejadorActualizacionInventario
)

def main():
    # --- Crear un pedido ficticio ---
    pedido = Pedido(
        id="P12345",
        items_boletas=["B1", "B2"],  # Puedes usar strings dummy como identificadores
        items_confiteria=["C1", "C2"],
        metodo_pago="Tarjeta",
        cupon_aplicado="CINE20"
    )

    # --- Construir la cadena de responsabilidad ---
    validador = ManejadorValidacionStock()
    descuentos = ManejadorAplicacionDescuentos()
    calculo = ManejadorCalculoPreciosYImpuestos()
    pago = ManejadorProcesamientoPago()
    generador = ManejadorGeneracionEntradas()
    inventario = ManejadorActualizacionInventario()

    validador.establecer_siguiente(descuentos)\
             .establecer_siguiente(calculo)\
             .establecer_siguiente(pago)\
             .establecer_siguiente(generador)\
             .establecer_siguiente(inventario)

    # --- Ejecutar el procesamiento ---
    validador.procesar_pedido(pedido)

    # --- Ver resultado final ---
    print("Estado final del pedido:")
    print(pedido)

if __name__ == "__main__":
    main()
