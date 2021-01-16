from typing import Optional

from utilities.vec import Vec3


class Turn:
    def __init__(self, dir: Vec3, axis: Optional[Vec3]):
        self.dir = dir
        self.axis = axis
