

class BaseGUIConfig:
    WINDOW_TITLE = ""
    TEXTS = []
    TEXT_COLOR = (0, 0, 0)

    @staticmethod
    def get_base_params(controller):
        return {
            'Select': {
                'text': 'Select',
                'callback': controller.on_click_select,
                'position': (0, 0)
            },
            'Draw': {
                'text': 'Draw',
                'callback': controller.on_click_draw,
                'position': (0, 1)
            },
            'Erode': {
                'text': 'Erode',
                'callback': controller.erode_mask,
                'position': (1, 0)
            },
            'Dilate': {
                'text': 'Dilate',
                'callback': controller.dilate_mask,
                'position': (1, 1)
            },
            'Redo': {
                'text': 'Redo',
                'callback': controller.redo,
                'position': (2, 1)
            },
            'Undo': {
                'text': 'Undo',
                'callback': controller.undo,
                'position': (2, 0)
            },
            'Reset mask': {
                'text': 'Reset mask',
                'callback': controller.reset_mask,
                'position': (2, 2)
            },
            'Save mask': {
                'text': 'Save mask',
                'callback': controller.save_mask,
                'position': (3, 1)
            },
            'Load mask': {
                'text': 'Load mask',
                'callback': controller.load_mask,
                'position': (3, 0)
            },
            'Load images': {
                'text': 'Load images',
                'callback': controller.load_images,
                'position': (4, 0)
            },
            'Save image': {
                'text': 'Save image',
                'callback': controller.save_images,
                'position': (4, 1)
            },
            'Continue': {
                'text': 'Continue',
                'callback': controller.on_click_continue,
                'position': (5, 0)
            },
            'Exit': {
                'text': 'Exit',
                'callback': controller.exit,
                'position': (5, 1)
            }
        }

    @staticmethod
    def get_base_trackbars(controller):
        return {
            'weight': {'value': controller.model.get_weight() * 100, 'callback': controller.on_weight_trackbar},
            'threshold_min': {'value': controller.model.get_threshold_min(),
                              'callback': lambda val: controller.on_threshold_trackbar(val, 'min')},
            'threshold_max': {'value': controller.model.get_threshold_max(),
                              'callback': lambda val: controller.on_threshold_trackbar(val, 'max')}
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
                'Back': {
                    'text': 'Back',
                    'callback':controller.on_click_back,
                    'position': (0, 0)
                },
                'Remove': {
                    'text': 'Remove watermark',
                    'callback': controller.on_click_remove,
                    'position': (0, 1)
                }
            },
            'key': controller.on_key,
            'trackbars': {
                'mode': {'value': controller.model.current_parameters.mode,
                         'callback': lambda val, attr='mode': controller.on_parameter_changed(attr, val)},
                'w': {'value': controller.model.current_parameters.w,
                      'callback': lambda val, attr='w': controller.on_parameter_changed(attr, val)},
                'r_min': {'value': controller.model.current_parameters.r_min,
                          'callback': lambda val, attr='r_min': controller.on_parameter_changed(attr, val)},
                'r_max': {'value': controller.model.current_parameters.r_max,
                          'callback': lambda val, attr='r_max': controller.on_parameter_changed(attr, val)},
                'g_min': {'value': controller.model.current_parameters.g_min,
                          'callback': lambda val, attr='g_min': controller.on_parameter_changed(attr, val)},
                'g_max': {'value': controller.model.current_parameters.g_max,
                          'callback': lambda val, attr='g_max': controller.on_parameter_changed(attr, val)},
                'b_min': {'value': controller.model.current_parameters.b_min,
                          'callback': lambda val, attr='b_min': controller.on_parameter_changed(attr, val)},
                'b_max': {'value': controller.model.current_parameters.b_max,
                          'callback': lambda val, attr='b_max': controller.on_parameter_changed(attr, val)}
            }
        }



