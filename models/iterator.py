from abc import ABC, abstractmethod
from typing import List, Iterator, Optional

class AsientoIterator(ABC):
    """Interfaz Iterator para recorrer asientos"""
    
    @abstractmethod
    def next(self) -> Optional[str]:
        """Retorna el siguiente asiento o None si no hay más"""
        pass
    
    @abstractmethod
    def has_next(self) -> bool:
        """Indica si hay más asientos para recorrer"""
        pass
    
    @abstractmethod
    def reset(self):
        """Reinicia el iterator a su posición inicial"""
        pass

class AsientosCollection:
    """Colección concreta de asientos que permite diferentes tipos de iteración"""
    
    def __init__(self, filas: List[str] = None, asientos_por_fila: int = 10):
        self._filas = filas or ["A", "B", "C"]
        self._asientos_por_fila = asientos_por_fila
        self._asientos_ocupados: List[str] = []
        self._asientos_vendidos: List[str] = []  # Nueva lista para asientos ya vendidos
    
    def crear_iterator_por_fila(self) -> 'AsientoPorFilaIterator':
        """Crea un iterator que recorre los asientos fila por fila"""
        return AsientoPorFilaIterator(self)
    
    def crear_iterator_por_columna(self) -> 'AsientoPorColumnaIterator':
        """Crea un iterator que recorre los asientos columna por columna"""
        return AsientoPorColumnaIterator(self)
    
    def marcar_asiento_ocupado(self, asiento_id: str):
        """Marca un asiento como ocupado"""
        if asiento_id not in self._asientos_ocupados:
            self._asientos_ocupados.append(asiento_id)
    
    def desmarcar_asiento_ocupado(self, asiento_id: str):
        """Desmarca un asiento ocupado"""
        if asiento_id in self._asientos_ocupados:
            self._asientos_ocupados.remove(asiento_id)
    
    def esta_ocupado(self, asiento_id: str) -> bool:
        """Verifica si un asiento está ocupado"""
        return asiento_id in self._asientos_ocupados
    
    def marcar_asiento_vendido(self, asiento_id: str):
        """Marca un asiento como vendido permanentemente"""
        if asiento_id in self._asientos_ocupados:
            self._asientos_ocupados.remove(asiento_id)
        self._asientos_vendidos.append(asiento_id)
    
    def desmarcar_asientos_vendidos(self, asientos: List[str]):
        """Desmarca asientos vendidos (útil para reembolsos)"""
        for asiento in asientos:
            if asiento in self._asientos_vendidos:
                self._asientos_vendidos.remove(asiento)
    
    def esta_vendido(self, asiento_id: str) -> bool:
        """Verifica si un asiento ya fue vendido"""
        return asiento_id in self._asientos_vendidos

    @property
    def filas(self) -> List[str]:
        return self._filas
    
    @property
    def asientos_por_fila(self) -> int:
        return self._asientos_por_fila
    
    @property
    def asientos_ocupados(self) -> List[str]:
        return self._asientos_ocupados.copy()
    
    @property
    def asientos_vendidos(self) -> List[str]:
        return self._asientos_vendidos.copy()

    def confirmar_venta_asientos(self, asientos: List[str]):
        """Confirma la venta de múltiples asientos"""
        for asiento in asientos:
            self.marcar_asiento_vendido(asiento)

class AsientoPorFilaIterator(AsientoIterator):
    """Iterator concreto que recorre asientos fila por fila"""
    
    def __init__(self, coleccion: AsientosCollection):
        self._coleccion = coleccion
        self._fila_actual = 0
        self._posicion_actual = 0
    
    def next(self) -> Optional[str]:
        if not self.has_next():
            return None
            
        fila = self._coleccion.filas[self._fila_actual]
        asiento = f"{fila}{self._posicion_actual + 1}"
        
        self._posicion_actual += 1
        if self._posicion_actual >= self._coleccion.asientos_por_fila:
            self._fila_actual += 1
            self._posicion_actual = 0
            
        return asiento
    
    def has_next(self) -> bool:
        return (self._fila_actual < len(self._coleccion.filas) and 
                (self._posicion_actual < self._coleccion.asientos_por_fila or 
                 self._fila_actual < len(self._coleccion.filas) - 1))
    
    def reset(self):
        self._fila_actual = 0
        self._posicion_actual = 0

class AsientoPorColumnaIterator(AsientoIterator):
    """Iterator concreto que recorre asientos columna por columna"""
    
    def __init__(self, coleccion: AsientosCollection):
        self._coleccion = coleccion
        self._columna_actual = 0
        self._fila_actual = 0
    
    def next(self) -> Optional[str]:
        if not self.has_next():
            return None
            
        fila = self._coleccion.filas[self._fila_actual]
        asiento = f"{fila}{self._columna_actual + 1}"
        
        self._fila_actual += 1
        if self._fila_actual >= len(self._coleccion.filas):
            self._columna_actual += 1
            self._fila_actual = 0
            
        return asiento
    
    def has_next(self) -> bool:
        return (self._columna_actual < self._coleccion.asientos_por_fila and 
                (self._fila_actual < len(self._coleccion.filas) or 
                 self._columna_actual < self._coleccion.asientos_por_fila - 1))
    
    def reset(self):
        self._columna_actual = 0
        self._fila_actual = 0