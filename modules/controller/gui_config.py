from dataclasses import dataclass

@dataclass
class TrackbarTexts:
    r_max = 'Red max:'
    r_min = 'Red min:'
    g_max = 'Green max:'
    g_min = 'Green min:'
    b_max = 'Blue max:'
    b_min = 'Blue min:'
    mode = 'Mode: Inpaint or most common color'
    w = 'Sharpening factor (w)'


class BaseGUIConfig:
    WINDOW_TITLE = ""
    TEXTS = []
    TEXT_COLOR = (0, 0, 0)

    @staticmethod
    def get_base_params(controller):
        return {
            'Select': {
                'text': 'Select (S)',
                'callback': controller.on_click_select,
                'position': (0, 0),
                'margin': (25, 0, 0, 0)
            },
            'Draw': {
                'text': 'Draw (C)',
                'callback': controller.on_click_draw,
                'position': (0, 1),
                'margin': (25, 0, 0, 0)
            },
            'Erode': {
                'text': 'Erode (E)',
                'callback': controller.erode_mask,
                'position': (1, 0)
            },
            'Dilate': {
                'text': 'Dilate (Q)',
                'callback': controller.dilate_mask,
                'position': (1, 1)
            },
            'Redo': {
                'text': 'Redo (Y)',
                'callback': controller.redo,
                'position': (2, 1)
            },
            'Undo': {
                'text': 'Undo (U)',
                'callback': controller.undo,
                'position': (2, 0)
            },
            'Reset mask': {
                'text': 'Reset mask (R)',
                'callback': controller.reset_mask,
                'position': (3, 0),
                'margin': (0, 0, 25, 0),
                'columnspan': 2
            },
            'Next': {
                'text': '>',
                'callback': controller.on_click_next,
                'position': (4, 1),
                'margin': (0, 0, 25, 0)
            },
            'Prev': {
                'text': '<',
                'callback': controller.on_click_prev,
                'position': (4, 0),
                'margin': (0, 0, 25, 0)
            },
            'Save mask': {
                'text': 'Save mask',
                'callback': controller.save_mask,
                'position': (5, 1)
            },
            'Load mask': {
                'text': 'Load mask',
                'callback': controller.load_mask,
                'position': (5, 0)
            },
            'Load images': {
                'text': 'Load images',
                'callback': controller.load_images,
                'position': (6, 0)
            },
            'Save images': {
                'text': 'Save images',
                'callback': controller.save_images,
                'position': (6, 1)
            },
            'Continue': {
                'text': 'Continue \n(Space)',
                'callback': controller.on_click_continue,
                'position': (7, 0),
                'margin': (25, 0, 0, 0),
                'columnspan': 2,
                'bg_color': (80, 135, 85)
            },
            'Exit': {
                'text': 'Exit',
                'callback': controller.exit,
                'position': (8, 0),
                'margin': (2, 0, 0, 0),
                'columnspan': 2,
                'bg_color': (150, 75, 75)
            }
        }

    @staticmethod
    def get_base_trackbars(controller):
        return {
            'Median Image Number': {'value': controller.model.get_aggregate_image_number(),
                                    'callback': controller.on_median_image_number_trackbar,
                                    'range': (1, max(1, controller.model.get_total_images()))
            },
            'Image <---> Mask': {'value': controller.model.get_weight() * 100,
                                    'callback': controller.on_weight_trackbar,
                                    'range': (0, 100)
            },
            'Threshold min:': {'value': controller.model.get_threshold_min(),
                              'callback': lambda val: controller.on_threshold_trackbar(val, 'min'),
                              'range': (0, 255)
            },
            'Threshold max:': {'value': controller.model.get_threshold_max(),
                              'callback': lambda val: controller.on_threshold_trackbar(val, 'max'),
                              'range': (0, 255)
            }
        }

    @staticmethod
    def get_params(controller):
        return {
            'mouse': controller.handle_mouse,
            'key': controller.on_key,
            'buttons': BaseGUIConfig.get_base_params(controller),
            'trackbars': BaseGUIConfig.get_base_trackbars(controller)
        }



class MaskSelectorGUIConfig(BaseGUIConfig):
    WINDOW_TITLE = "Mask Selector"
    TEXTS = [
        "Draw a circle around the object you want to remove.",
        "Press 'A'/'D' to go to the previous/next page.",
        "Press 'U'/'Y' to undo/redo.",
        "Press 'R' to reset the mask.",
        "Press 'space' to finish."
    ]
    TEXT_COLOR = (255, 255, 255)

    @staticmethod
    def get_params(controller):
        return {
            'mouse': controller.handle_mouse,
            'key': controller.on_key,
            'buttons': BaseGUIConfig.get_base_params(controller),
            'trackbars': BaseGUIConfig.get_base_trackbars(controller)
        }

class ParameterAdjusterGUIConfig(BaseGUIConfig):
    TEXTS = ["Set the color range with trackbars.",
             "Press 'A'/'D' to go to the previous/next page.",
             "Press 'T' to set different parameters for each image.",
             "Press 'space' to finish."]
    TEXT_COLOR = (255, 255, 255)
    TITLE = "Parameter adjuster"

    @staticmethod
    def get_params(controller):
        return {
            'buttons': {
                'Prev': {
                    'text': '<',
                    'callback': controller.on_click_prev,
                    'position': (0, 0),
                    'margin': (25, 0, 0, 0)
                },
                'Next': {
                    'text': '>',
                    'callback': controller.on_click_next,
                    'position': (0, 1),
                    'margin': (25, 0, 0, 0)
                },
                'Remove': {
                    'text': 'Remove watermark \n(Space)',
                    'callback': controller.on_click_remove,
                    'position': (1, 0),
                    'margin': (45, 0, 0, 0),
                    'columnspan': 2,
                    'bg_color': (70,125, 75),
                },
                'Back': {
                    'text': 'Back',
                    'callback':controller.on_click_back,
                    'position': (2, 0),
                    'margin': (5, 0, 0, 0),
                    'columnspan': 2,
                    'bg_color': (150, 75, 75)
                }
            },
            'key': controller.on_key,
            'trackbars': {
                'mode' : {'value': controller.model.current_parameters.mode,
                         'callback': lambda val, attr='mode': controller.on_parameter_changed(attr, val),
                         'range': (0, 1)
                                      },
                'w': {'value': controller.model.current_parameters.w,
                      'callback': lambda val, attr='w': controller.on_parameter_changed(attr, val),
                      'range': (0, 25)
                                   },
                'r_min': {'value': controller.model.current_parameters.r_min,
                          'callback': lambda val, attr='r_min': controller.on_parameter_changed(attr, val)
                                       },
                'r_max': {'value': controller.model.current_parameters.r_max,
                          'callback': lambda val, attr='r_max': controller.on_parameter_changed(attr, val)
                                      },
                'g_min': {'value': controller.model.current_parameters.g_min,
                          'callback': lambda val, attr='g_min': controller.on_parameter_changed(attr, val)
                                      },
                'g_max': {'value': controller.model.current_parameters.g_max,
                          'callback': lambda val, attr='g_max': controller.on_parameter_changed(attr, val)
                                      },
                'b_min': {'value': controller.model.current_parameters.b_min,
                          'callback': lambda val, attr='b_min': controller.on_parameter_changed(attr, val)
                                      },
                'b_max': {'value': controller.model.current_parameters.b_max,
                          'callback': lambda val, attr='b_max': controller.on_parameter_changed(attr, val)
                                      }
            },
            'checkboxes': {
                'Apply same parameters to all pages': {
                    'value': controller.model.config_data.apply_same_parameters,
                    'callback': controller.on_toggle_apply_same_parameters
                }
            }
        }



