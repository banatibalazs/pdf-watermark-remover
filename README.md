#  Watermark Remover

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
python remover.py 
```


The arguments for the script are as follows (all are optional)
- **pdf_path**: The path to the PDF file. Default is `input.pdf`.
- **save_path**: The path to save the output PDF file. Default is `output.pdf`.
- **--dpi**: The resolution of the images extracted from the PDF file. Default is `100`.
- **--max_width**: The maximum width of the images shown during the mask selection. Default is `1920`.
- **--max_height**: The maximum height of the images shown during the mask selection. Default is `1080`.


```
python remover.py input.pdf output.pdf --dpi 300 --max_width 1920 --max_height 1080
```

## Usage


1. **Path to your pdf:** Set `PDF_PATH` global variable or pass it as an argument in the command line. 
2. **Area Selection:** Draw on the image to create a mask for the watermark.

<p align="center">
  <img src="https://github.com/banatibalazs/pdf-watermark-remover/blob/main/gifs/sm_1_draw.gif" alt="draw mask gif">
</p>

3. **Median Image Calculation:** This process sorts pixel values at each location in a set of images and selects the middle value. It helps to identify the constant features in the image.

4. **Thresholding:** Adjust the threshold value to fine-tune the mask.

<p align="center">
  <img src="https://github.com/banatibalazs/pdf-watermark-remover/blob/main/gifs/sm_2_threshold.gif" alt="draw mask gif">
</p>

5. **Mask Adjustment:** Use 'd', 'e', or 'r' to dilate, erode, or reset the mask.

<p align="center">
  <img src="https://github.com/banatibalazs/pdf-watermark-remover/blob/main/gifs/sm_3_erode_dilate.gif" alt="draw mask gif">
</p>

6. **Color Range:** Set the color range with trackbars to finalize the mask
<p align="center">
  <img src="https://github.com/banatibalazs/pdf-watermark-remover/blob/main/gifs/sm_4_color_filter.gif" alt="draw mask gif">
</p>

7. **Watermark Removal:** The script removes the watermark from the images and saves the output as a new PDF file. <u> The area of the removed watermark is filled with the **most common color** in the image. </u>

## Note
Large files or high DPI can slow the reading of the PDF file. If the process is too slow,
consider decreasing the DPI or using smaller PDFs.
This project is for educational purposes and should not infringe on copyrights.
