from abc import ABC, abstractmethod

class BaseNotifier(ABC):
    @abstractmethod
    def __init__(self, config):
        pass

    @abstractmethod
    def send_vehicle_notification(self, vehicles: list) -> None:
        pass

    @classmethod
    @abstractmethod
    def validate_config(cls, config):
        pass