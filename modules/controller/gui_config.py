

class BaseGUIConfig:
    WINDOW_TITLE = ""
    TEXTS = []
    TEXT_COLOR = (0, 0, 0)

    @staticmethod
    def get_base_params(controller):
        return {
            'Select': {
                'text': 'Select',
                'callback': lambda btn_name='select': controller.on_button_click(btn_name)
            },
            'Draw': {
                'text': 'Draw',
                'callback': lambda btn_name='draw': controller.on_button_click(btn_name)
            },
            'Erode': {
                'text': 'Erode',
                'callback': controller.erode_mask
            },
            'Dilate': {
                'text': 'Dilate',
                'callback': controller.dilate_mask
            },
            'Redo': {
                'text': 'Redo',
                'callback': lambda btn_name='redo': controller.redo()
            },
            'Undo': {
                'text': 'Undo',
                'callback': lambda btn_name='undo': controller.undo()
            },
            'Reset mask': {
                'text': 'Reset',
                'callback': lambda btn_name='reset': controller.reset_mask()
            },
            'Save mask': {
                'text': 'Save mask',
                'callback': lambda btn_name='save': controller.save_mask()
            },
            'Save image': {
                'text': 'Save image',
                'callback': lambda btn_name='save_image': controller.save_images()
            },
            'Load': {
                'text': 'Load',
                'callback': lambda btn_name='load': controller.load_mask()
            },
            'Continue': {
                'text': 'Continue',
                'callback': lambda btn_name='continue': controller.on_button_click(btn_name)
            },
            'Exit': {
                'text': 'Exit',
                'callback': lambda btn_name='exit': controller.exit()
            }
        }

    @staticmethod
    def get_base_trackbars(controller):
        return {
            'weight': {'value': controller.model.weight * 100, 'callback': controller.on_weight_trackbar},
            'threshold_min': {'value': controller.model.threshold_min,
                              'callback': lambda val: controller.on_threshold_trackbar(val, 'min')},
            'threshold_max': {'value': controller.model.threshold_max,
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
                    'callback': lambda btn_name='back': controller.on_button_click(btn_name)
                },
                'Remove': {
                    'text': 'Remove watermark',
                    'callback': lambda btn_name='remove': controller.on_button_click(btn_name)
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



