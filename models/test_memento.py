from memento import SeleccionAsientos, GestorHistorialSeleccion

def main():
    seleccion = SeleccionAsientos()
    historial = GestorHistorialSeleccion()

    # Estado inicial
    seleccion.seleccionar_asiento("A1")
    historial.guardar(seleccion.crear_memento())

    seleccion.seleccionar_asiento("A2")
    historial.guardar(seleccion.crear_memento())

    seleccion.seleccionar_asiento("B1")
    historial.guardar(seleccion.crear_memento())

    print("🔵 Estado actual:")
    print(seleccion.obtener_estado_actual())

    # Deshacer una vez
    memento_deshacer = historial.deshacer()
    if memento_deshacer:
        seleccion.restaurar_desde_memento(memento_deshacer)
        print("\n🟠 Después de un deshacer:")
        print(seleccion.obtener_estado_actual())

    # Deshacer otra vez
    memento_deshacer = historial.deshacer()
    if memento_deshacer:
        seleccion.restaurar_desde_memento(memento_deshacer)
        print("\n🟠 Después de segundo deshacer:")
        print(seleccion.obtener_estado_actual())

    # Rehacer
    memento_rehacer = historial.rehacer()
    if memento_rehacer:
        seleccion.restaurar_desde_memento(memento_rehacer)
        print("\n🟢 Después de rehacer:")
        print(seleccion.obtener_estado_actual())

    # Confirmar
    print("\n✅ Confirmando selección:")
    seleccion.confirmar_seleccion()

if __name__ == "__main__":
    main()
