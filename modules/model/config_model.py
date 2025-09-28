from dataclasses import dataclass

from modules.controller.constants import MaskMode


@dataclass
class ConfigData:
    mode: MaskMode = MaskMode.SELECT
    # threshold_min: int = 1
    # threshold_max: int = 225
    weight: float = 0.45
    # apply_same_parameters: bool = True


class ConfigModel:
    def __init__(self):
        self.config_data = ConfigData()

    def get_mode(self) -> MaskMode:
        return self.config_data.mode

    def set_mode(self, mode: MaskMode):
        self.config_data.mode = mode

    def get_weight(self) -> float:
        return self.config_data.weight

    def set_weight(self, weight: float):
        self.config_data.weight = weight

    # def get_threshold_min(self) -> int:
    #     return self.config_data.threshold_min
    #
    # def set_threshold_min(self, value: int):
    #     self.config_data.threshold_min = int(value)
    #
    # def get_threshold_max(self) -> int:
    #     return self.config_data.threshold_max
    #
    # def set_threshold_max(self, value: int):
    #     self.config_data.threshold_max = int(value)

    # def toggle_apply_same_parameters(self) -> bool:
    #     self.config_data.apply_same_parameters = not self.config_data.apply_same_parameters
    #     return self.config_data.apply_same_parameters
    #
    # def get_apply_same_parameters(self) -> bool:
    #     print(self.config_data.apply_same_parameters)
    #     return self.config_data.apply_same_parameters