

class BaseGUIConfig:
    WINDOW_TITLE = ""
    TEXTS = []
    TEXT_COLOR = (0, 0, 0)

    @staticmethod
    def get_base_params(controller):
        return {
            'Select': {
                'text': 'Selection',
                'callback': lambda btn_name='selection': controller.on_button_click(btn_name)
            },
            'Draw': {
                'text': 'Drawing',
                'callback': lambda btn_name='drawing': controller.on_button_click(btn_name)
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
            'Save': {
                'text': 'Save',
                'callback': lambda btn_name='save': controller.save_mask()
            },
            'Load': {
                'text': 'Load',
                'callback': lambda btn_name='load': controller.load_mask()
            }
        }

    @staticmethod
    def get_base_trackbars(controller):
        return {
            'weight': {'value': controller.model.weight * 100, 'callback': controller.on_weight_trackbar},
            'threshold_min': {'value': controller.model.threshold_min,
                              'callback': controller.on_threshold_trackbar_min},
            'threshold_max': {'value': controller.model.threshold_max,
                              'callback': controller.on_threshold_trackbar_max},
        }


class MaskDrawingGUIConfig(BaseGUIConfig):
    TEXTS = ["Draw on the mask.",
             "LMouse/RMouse: erase/draw",
             "Mouse wheel: cursor size",
             "Press 'U'/'Y' to undo/redo.",
             "Press 'R' to reset the mask.",
             "Press 'space' to finish."]
    TEXT_COLOR = (0, 0, 0)
    TITLE = "Mask processing"

    @staticmethod
    def get_params(controller):
        return  {
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



