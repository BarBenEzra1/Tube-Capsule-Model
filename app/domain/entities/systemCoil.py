from app.domain.entities.coil import Coil


class SystemCoil:
    def __init__(self, coil_id: int, position: float, coil: Coil):
        self.coil_id = coil_id
        self.position = position
        self.coil = coil
