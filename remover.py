import argparse

from modules.controller.base_controller import BaseController
from modules.pdf_image_extractor import PDFImageExtractor
from modules.controller.parameter_adjuster_controller import ParameterAdjuster
from modules.view.tkinter_view import TkinterView
from modules.watermark_remover import WatermarkRemover

import sys
sys.setrecursionlimit(2000)  # Example: increase limit

# Global variables
PDF_PATH = 'input.pdf'
SAVE_PATH = 'output.pdf'

# Set the maximum width and height for the images during the masking process
# The final PDF will have the same dimensions as the original PDF
MAX_WIDTH = 1000
MAX_HEIGHT = 900

# Set the DPI for the images, this affects the quality of the final PDF
DPI = 200


def parse_args():
    parser = argparse.ArgumentParser(description='Remove watermark from PDF.')
    parser.add_argument('pdf_path', type=str, nargs='?', default=PDF_PATH, help='Path to the input PDF file.')
    parser.add_argument('save_path', type=str, nargs='?', default=SAVE_PATH, help='Path to save the output PDF file.')
    parser.add_argument('--dpi', type=int, default=DPI, help='DPI for the images. Default is 300.')
    parser.add_argument('--max_width', type=int, default=MAX_WIDTH, help=f'Maximum width for the images. Default is {MAX_WIDTH}.')
    parser.add_argument('--max_height', type=int, default=MAX_HEIGHT, help=f'Maximum height for the images. Default is {MAX_HEIGHT}.')
    return parser.parse_args()


def main():
    args = parse_args()

    # Extract images from the PDF
    image_extractor = PDFImageExtractor(args.pdf_path, args.dpi, args.max_width, args.max_height)
    images_for_mask_making = image_extractor.get_images_for_mask_making()
    images_for_watermark_removal = image_extractor.get_images_for_watermark_removal()

    view_instance = TkinterView()

    # Draw the initial mask
    selector = BaseController(images_for_mask_making, view_instance)
    selector.run()
    # bgr_mask = selector.get_bgr_mask()

    # Set the color range to be filtered/removed
    # color_adjuster = ParameterAdjuster(images_for_mask_making, bgr_mask, view_instance)
    # color_adjuster.run()
    # parameters = color_adjuster.get_parameters()
    #
    # remover = WatermarkRemover(images_for_watermark_removal, bgr_mask, parameters)
    # remover.remove_watermark()
    # processed_images = remover.get_processed_images()
    # while True:
    #     resized_processed_images = image_extractor.resize_images_for_mask_making(processed_images)
    #     selector = BaseController(resized_processed_images, view_instance)
    #     selector.run()
    #     bgr_mask = selector.get_bgr_mask()
    #
    #     color_adjuster = ParameterAdjuster(resized_processed_images, bgr_mask, view_instance)
    #     color_adjuster.run()
    #     parameters = color_adjuster.get_parameters()
    #
    #     remover = WatermarkRemover(processed_images, bgr_mask, parameters)
    #     remover.remove_watermark()
    #     processed_images = remover.get_processed_images()


    # remover.save_pdf(args.save_path)

if __name__ == "__main__":
    main()





