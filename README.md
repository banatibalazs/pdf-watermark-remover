#  Watermark Remover

![Python](https://img.shields.io/badge/python-3.6+-green.svg)
![PDF2Image](https://img.shields.io/badge/pdf2image--green.svg)
![Img2PDF](https://img.shields.io/badge/img2pdf--green.svg)
![OpenCV](https://img.shields.io/badge/opencv_contrib_python--green.svg)


This Python project uses OpenCV to remove watermarks or other objects from PDFs. The process includes steps such as area selection, thresholding, drawing, mask erosion/dilation, and color range setting. The final result is a new PDF file with the watermark removed, either filled with the most common color in the image or inpainted.

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

5. **Draw on the mask**: Use the mouse to draw on the mask to refine it. Erase the unwanted parts of the mask or draw on the missing parts. 

6. **Mask Adjustment:** Use 'd', 'e', or 'r' to dilate, erode, or reset the mask.

<p align="center">
  <img src="https://github.com/banatibalazs/pdf-watermark-remover/blob/main/gifs/sm_3_erode_dilate.gif" alt="draw mask gif">
</p>

7. **Color Range:** Set the color range with trackbars to finalize the mask
<p align="center">
  <img src="https://github.com/banatibalazs/pdf-watermark-remover/blob/main/gifs/sm_4_color_filter.gif" alt="draw mask gif">
</p>

8. **Watermark Removal:** The script removes the watermark from the images and saves the output as a new PDF file. <u> The area of the removed watermark is either filled with the **most common color** in the image or **inpainted**. </u>


## Python Version Compatibility

This script is compatible with `Python 3.6` and above.

## Dependencies

The script requires the following Python libraries:

- `pdf2image`: Used for converting PDF files into images. This library depends on `poppler-utils`, which is a set of command line tools for working with PDF files. You need to install `poppler-utils` separately for `pdf2image` to work. The installation process depends on your operating system.
- `img2pdf`: Used for converting images back into a PDF file.
- `opencv-contrib-python`: A wrapper package for OpenCV python bindings along with its extra modules.

## Installation 

0. **Clone the repository**

    ```bash
    git clone https://github.com/banatibalazs/pdf-watermark-remover.git
   ```
    ```commandline
    cd pdf-watermark-remover
    ```
1. **Create a virtual environment and activate it**

    ```bash
    python -m venv env_name
    ```
   - on Windows:
    
        ```bash
        env_name\Scripts\activate
        ```

   - on Linux:
        ```
        source env_name/bin/activate
        ```

2. **Install the required libraries.**
    
    ```bash
    pip install pdf2image img2pdf opencv-contrib-python 
    ```

3. **Install poppler-utils**

    - **Windows**: Download a precompiled version of Poppler from [this link](https://github.com/oschwartz10612/poppler-windows/releases/). Extract the contents of the zip file and add the `bin` folder to your system's PATH environment variable.
    - **Ubuntu/Debian**: Install `poppler-utils` with the following command: `sudo apt-get install -y poppler-utils`
    - **macOS**: If you have Homebrew installed, you can install `poppler` with the following command: `brew install poppler`
   

## Running the Script

```
python remover.py 
```


The arguments for the script are as follows (all are optional)
- **pdf_path**: The path to the PDF file. Default is `input.pdf`.
- **save_path**: The path to save the output PDF file. Default is `output.pdf`.
- **--dpi**: The resolution of the images extracted from the PDF file. Default is `200`.
- **--max_width**: The maximum width of the images shown during the mask selection. Default is `1400`.
- **--max_height**: The maximum height of the images shown during the mask selection. Default is `800`.


```
python remover.py input.pdf output.pdf --dpi 300 --max_width 1920 --max_height 1080
```


## Troubleshooting

- **Trackbars not visible:**

   If you cannot see the trackbar, try decreasing the `max_height` parameter.

   **Note:** On Linux, the trackbars are displayed at the bottom of the window, while on Windows, they are displayed at the top.


- **Process is too slow:**

   The reading of large PDF files can be slow, especially if the resolution is high. If the process is too slow, try decreasing the `dpi` parameter.

## Disclaimer

This script is for educational purposes only. The watermark removal process may not be perfect and may not work for all types of watermarks. The script may also remove parts of the image that are not watermarks. Use this script at your own risk.
