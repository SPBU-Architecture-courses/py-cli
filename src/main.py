import abc


class Abstarct(abc.ABC):
    def __init__(self) -> None:
        super().__init__()
        self.new_field: int
