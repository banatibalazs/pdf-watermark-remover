import argparse

from modules.mask_processing.mask_drawing import MaskDrawing
from modules.mask_processing.mask_erosion_dilation import MaskErosionDilation
from modules.mask_processing.mask_thresholding import MaskThresholding
from modules.median_mask_making import MedianMaskMaking
from modules.pdf_image_extractor import PDFImageExtractor
from modules.mask_selector import MaskSelector
from modules.color_adjuster import ColorAdjuster
from modules.watermark_remover import WatermarkRemover

# Global variables
PDF_PATH = 'input.pdf'
SAVE_PATH = 'output.pdf'

# Set the maximum width and height for the images during the masking process
# The final PDF will have the same dimensions as the original PDF
MAX_WIDTH = 1400
MAX_HEIGHT = 800

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

    # Draw the initial mask
    selector = MaskSelector(images_for_mask_making)
    selector.draw_mask()
    drawn_mask = selector.get_gray_mask()

    # Create a median mask
    median_mask_maker = MedianMaskMaking(images_for_mask_making, drawn_mask)

    # Threshold the mask
    mask_thresholder = MaskThresholding(median_mask_maker.get_gray_mask())
    mask_thresholder.process_mask()

    # Draw on the mask
    mask_drawer = MaskDrawing(mask_thresholder.get_gray_mask())
    mask_drawer.process_mask()

    # Erode and dilate the mask
    mask_eroder_dilater = MaskErosionDilation(mask_drawer.get_gray_mask())
    mask_eroder_dilater.process_mask()
    bgr_mask = mask_eroder_dilater.get_bgr_mask()

    # Set the color range to be filtered/removed
    color_adjuster = ColorAdjuster(images_for_mask_making, bgr_mask)
    color_adjuster.adjust_color_filter()
    parameters = color_adjuster.get_parameters()

    # Remove the watermark and save the final PDF
    remover = WatermarkRemover(images_for_watermark_removal, bgr_mask, parameters)
    remover.remove_watermark()
    remover.save_pdf(args.save_path)

if __name__ == "__main__":
    main()





