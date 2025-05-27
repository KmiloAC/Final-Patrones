# models/memento.py

from typing import List, Any


class MementoSeleccionAsientos:
    def __init__(self, estado_asientos: List[str], estado_datos_adicionales: Any):
        self._estado_asientos = list(estado_asientos)  # Copia defensiva
        self._estado_datos_adicionales = estado_datos_adicionales

    # Métodos simulando visibilidad protegida (solo el originador debe usarlos)
    def _get_estado_asientos(self) -> List[str]:
        return self._estado_asientos

    def _get_estado_datos_adicionales(self) -> Any:
        return self._estado_datos_adicionales


class SeleccionAsientos:
    def __init__(self):
        self._asientos_seleccionados: List[str] = []
        self._otros_datos_estado: dict = {}  # Ejemplo: {'precio': 10000, 'tarifa': 'normal'}

    def seleccionar_asiento(self, asiento_id: str):
        if asiento_id not in self._asientos_seleccionados:
            self._asientos_seleccionados.append(asiento_id)

    def deseleccionar_asiento(self, asiento_id: str):
        if asiento_id in self._asientos_seleccionados:
            self._asientos_seleccionados.remove(asiento_id)

    def confirmar_seleccion(self):
        # Aquí podría ir lógica para persistir la selección o procesar el pago
        print(f"Selección confirmada: {self._asientos_seleccionados}")

    def crear_memento(self) -> MementoSeleccionAsientos:
        return MementoSeleccionAsientos(
            estado_asientos=self._asientos_seleccionados,
            estado_datos_adicionales=self._otros_datos_estado
        )

    def restaurar_desde_memento(self, memento: MementoSeleccionAsientos):
        self._asientos_seleccionados = list(memento._get_estado_asientos())
        self._otros_datos_estado = memento._get_estado_datos_adicionales()

    def obtener_estado_actual(self) -> dict:
        return {
            "asientos": self._asientos_seleccionados,
            "otros_datos": self._otros_datos_estado
        }


class GestorHistorialSeleccion:
    def __init__(self):
        self._historial_mementos: List[MementoSeleccionAsientos] = []
        self._redo_stack: List[MementoSeleccionAsientos] = []

    def guardar(self, memento: MementoSeleccionAsientos):
        self._historial_mementos.append(memento)
        self._redo_stack.clear()  # Al guardar un nuevo estado, se pierde el camino de rehacer

    def deshacer(self) -> MementoSeleccionAsientos | None:
        if len(self._historial_mementos) > 1:
            memento_actual = self._historial_mementos.pop()
            self._redo_stack.append(memento_actual)
            return self._historial_mementos[-1]
        elif self._historial_mementos:
            return self._historial_mementos[0]
        return None

    def rehacer(self) -> MementoSeleccionAsientos | None:
        if self._redo_stack:
            memento = self._redo_stack.pop()
            self._historial_mementos.append(memento)
            return memento
        return None

    def limpiar_historial(self):
        self._historial_mementos.clear()
        self._redo_stack.clear()
