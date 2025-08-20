


class BaseGUIConfig:
    WINDOW_TITLE = ""
    TEXTS = []
    TEXT_COLOR = (0, 0, 0)

    @staticmethod
    def get_base_buttons(model):
        return {
            'Select': {
                'text': 'Selection',
                'callback': lambda btn_name='selection': model.on_button_click(btn_name)
            },
            'Threshold': {
                'text': 'Thresholding',
                'callback': lambda btn_name='threshold': model.on_button_click(btn_name)
            },
            'Draw': {
                'text': 'Drawing',
                'callback': lambda btn_name='drawing': model.on_button_click(btn_name)
            },
            'Erode': {
                'text': 'Erode',
                'callback': lambda btn_name='erode': model.on_button_click(btn_name)
            },
            'Redo': {
                'text': 'Redo',
                'callback': lambda btn_name='redo': model.redo()
            },
            'Undo': {
                'text': 'Undo',
                'callback': lambda btn_name='undo': model.undo()
            },
            'Reset mask': {
                'text': 'Reset',
                'callback': lambda btn_name='reset': model.reset_mask()
            },
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




class MaskErosionDilationGUIConfig(BaseGUIConfig):
    WINDOW_TITLE = "Mask Erosion and Dilation"
    TEXTS = [
        "Press 'D' to dilate the mask.",
        "Press 'E' to erode the mask.",
        "Press 'R' to reset the mask.",
        "Press 'space' to finish."
    ]
    TEXT_COLOR = (0, 0, 0)



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

    # @staticmethod
    # def get_buttons(model):
    #     return {
    #         'save_mask': {
    #             'text': 'Selection',
    #             'callback': lambda btn_name='selection': model.on_button_click(btn_name)
    #         },
    #         'reset_mask': {
    #             'text': 'Drawing',
    #             'callback': lambda btn_name='drawing': model.on_button_click(btn_name)
    #         },
    #         'load_mask': {
    #             'text': 'Erode',
    #             'callback': lambda btn_name='erode': model.on_button_click(btn_name)
    #         }
    #     }



class MaskThresholdingGUIConfig(BaseGUIConfig):
    WINDOW_TITLE = "Mask Thresholding"
    TEXTS = [
        "Use the trackbars to adjust the thresholding.",
        "Press 'space' to finish."
    ]
    TEXT_COLOR = (0, 0, 0)



