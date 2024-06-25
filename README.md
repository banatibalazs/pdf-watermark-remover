#  Watermark Removal

This python script removes watermarks from PDFs using opencv.


## Dependencies

The script requires the following Python libraries:

- `pdf2image`: Used for converting PDF files into images.
- `img2pdf`: Used for converting images back into a PDF file.
- `opencv-contrib-python`: A wrapper package for OpenCV python bindings along with its extra modules.
- `tqdm`: Used for displaying progress bars in the console.

## Installation

Create a virtual environment, activate it and install the required libraries.

```bash
python -m venv env_name
```
    
```bash
env_name\Scripts\activate
```


```bash
pip install pdf2image img2pdf opencv-contrib-python tqdm
```

## Running the Script

```
python remover.py input.pdf output.pdf
```


The arguments for the script are as follows (all are optional)
- **pdf_path**: The path to the PDF file. Default is `input.pdf`.
- **save_path**: The path to save the output PDF file. Default is `output.pdf`.
- **--dpi**: The resolution of the images extracted from the PDF file. Default is `300`.
- **--max_width**: The maximum width of the images shown during the mask selection. Default is `1920`.
- **--max_height**: The maximum height of the images shown during the mask selection. Default is `1080`.


```
python remover.py input.pdf output.pdf --dpi 300 --max_width 1920 --max_height 1080
```

## Usage

For `watermark.py`:

1. **Path to your pdf:** Set `PDF_PATH` global variable or pass it as an argument in the command line. 
2. **Area Selection:** Draw on the image to create a mask for the watermark.
![draw mask gif](url_of_your_gif)
4. **Median Image Calculation:** This process sorts pixel values at each location in a set of images and selects the middle value. It helps to identify the constant features in the image.
![threshold mask gif](url_of_your_gif)
4. **Thresholding:** Adjust the threshold value to fine-tune the mask.
5. **Mask Adjustment:** Use 'd', 'e', or 'r' to dilate, erode, or reset the mask.
![erode dilate mask gif](url_of_your_gif)
6. **Color Range:** After finalizing the mask, set the color range with trackbars.
![adjust color filter gif](url_of_your_gif)
7. **Watermark Removal:** The script removes the watermark from the images and saves the output as a new PDF file.

Note: Large files or high DPI can slow the reading of the PDF file. If the process is too slow, consider decreasing the DPI or using smaller PDFs.

## Note
This project is for educational purposes and should not infringe on copyrights.
