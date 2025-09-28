from dataclasses import dataclass
from typing import List, Dict, Any

from modules.model.image_model import ImageModel


@dataclass
class ParamsForRemoval:
    r_min: int = 90
    r_max: int = 240
    g_min: int = 90
    g_max: int = 240
    b_min: int = 90
    b_max: int = 240
    w: float = 0
    mode: bool = True

    def get_parameters(self):
        return [self.r_min, self.r_max, self.g_min, self.g_max, self.b_min, self.b_max, self.w, self.mode]

    def set_parameters(self, args):
        self.r_min, self.r_max, self.g_min, self.g_max, self.b_min, self.b_max, self.w, self.mode = args

    @staticmethod
    def get_parameter_names():
        return ['r_min', 'r_max', 'g_min', 'g_max', 'b_min', 'b_max', 'w', 'mode']

    def get_params_as_dict(self):
        return {'names': self.get_parameter_names(),
                'values': self.get_parameters()}



class ParameterModel:
    def __init__(self, image_model: ImageModel):
        self.image_model = image_model
        self.parameters: List[ParamsForRemoval] = [ParamsForRemoval() for _ in range(self.image_model.get_number_of_pages())]
        self.apply_same_parameters = False

    def get_current_parameters(self) -> Dict[str, Any]:
        return self.parameters[self.image_model.get_current_page_index()]

    def get_current_parameters_data_as_dict(self):
        return self.parameters[self.image_model.get_current_page_index()].get_params_as_dict()

    def set_all_parameters_the_same_as_current(self) -> None:
        params = self.get_current_parameters().get_parameters()
        for param in self.parameters:
            param.set_parameters(params)

    def get_parameters(self) -> List[ParamsForRemoval]:
        return self.parameters

    def toggle_apply_same_parameters(self) -> bool:
        self.apply_same_parameters = not self.apply_same_parameters
        return self.apply_same_parameters

    def get_apply_same_parameters(self) -> bool:
        return self.apply_same_parameters

    def set_current_parameter(self, attr: str, val: Any) -> None:
        if hasattr(self.get_current_parameters(), attr):
            setattr(self.get_current_parameters(), attr, val)
            # If apply_same_parameters is enabled, update all parameters
            if self.apply_same_parameters:
                self.set_all_parameters_the_same_as_current()
        else:
            raise AttributeError(f"ParamsForRemoval has no attribute '{attr}'")