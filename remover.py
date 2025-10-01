import argparse

from modules.controller.base_controller import BaseController

import sys
sys.setrecursionlimit(2000)  # Example: increase limit

# Global variables
PDF_PATH = 'input.pdf'
SAVE_PATH = 'output.pdf'

# Set the maximum width and height for the images during the masking process
# The final PDF will have the same dimensions as the original PDF
MAX_WIDTH = 900
MAX_HEIGHT = 800
# DEFAULT_GUI = 'pyqt5'
DEFAULT_GUI = 'tkinter'

# Set the DPI for the images, this affects the quality of the final PDF
DPI = 175


def parse_args():
    parser = argparse.ArgumentParser(description='Remove watermark from PDF.')
    parser.add_argument('pdf_path', type=str, nargs='?', default=PDF_PATH, help='Path to the input PDF file.')
    parser.add_argument('--gui_type', type=str, nargs='?', default=DEFAULT_GUI, help='Path to save the output PDF file.')
    parser.add_argument('--dpi', type=int, default=DPI, help='DPI for the images. Default is 300.')
    parser.add_argument('--max_width', type=int, default=MAX_WIDTH, help=f'Maximum width for the images. Default is {MAX_WIDTH}.')
    parser.add_argument('--max_height', type=int, default=MAX_HEIGHT, help=f'Maximum height for the images. Default is {MAX_HEIGHT}.')
    return parser.parse_args()


def main():
    args = parse_args()

    selector = BaseController(args)
    selector.run()

if __name__ == "__main__":
    main()





