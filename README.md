#  Watermark Remover

![Python](https://img.shields.io/badge/python-3.6+-green.svg)
![OpenCV](https://img.shields.io/badge/opencv_contrib_python--green.svg)
![PyMuPDF](https://img.shields.io/badge/pymupdf--green.svg)
![PyQt5](https://img.shields.io/badge/pyqt5--green.svg)


A Python application for removing watermarks from PDF files using mask-based image processing. 

## Overview
<p>
    <img src='gifs/both.png' width='100%' />
</p>

- **The "Image <---> Median Image" trackbar**: 
    - Default value is 1, which means the **actual image** is used.
    - Above that a **'median image'** is calculated from this number of pages. It is made by calculating the median color value for each pixel across the pages. This helps to highlight the watermark, as it is usually consistent across pages, while the content varies.
    - It is limited to 50 pages because it is computationally expensive.
<p>
    <img src='gifs/image.png' width='32%' />
    <img src='gifs/median_image_low.png' width='32%' />
    <img src='gifs/median_image_high.png' width='32%' />
</p>

- **The "Image <---> Mask" trackbar**: This trackbar changes the weighting between the image and the mask. 
    - At 0, only the image is shown.
    - At 100, only the mask is shown.
    - In between, a weighted combination of the two is displayed. This helps to visualize how well the mask aligns with the watermark in the image.
<p>
    <img src='gifs/image.png' width='32%' />
    <img src='gifs/both.png' width='32%' />
    <img src='gifs/mask.png' width='32%' />
</p>

- **Mask Selection:**: 
    - Left-click and drag to select an arbitrary area.
    - Releasing the mouse button finalizes the selection.
<p>
    <img src='gifs/area_selection.png' width='30%' />
    <img src='gifs/area_selection_after_release.png' width='30%' />
</p>

- **Mask Drawing:** Users can select and refine the mask by drawing on it with a cursor. 
    - Right-click to erase
    - Left-click to draw. 
    - There are two cursor types: circle and rectangle.
    - The cursor size is adjustable with mouse wheel.
<p>
    <img src='gifs/drawing_mask.png' width='30%' />
    <img src='gifs/erasing_mask.png' width='30%' />
    <img src='gifs/cursor_type_rectangle.png' width='30%' />
</p>

- **Thresholding:** Applies thresholding to the masked area of the image to refine the mask further.
<p>
    <img src='gifs/threshold_1.png' width='30%' />
    <img src='gifs/threshold_2.png' width='30%' />
    <img src='gifs/threshold_3.png' width='30%' />
</p>

- **Mask Erosion/Dilation:**
  - Erosion: Shrinks the white areas in the mask, which can help remove small unwanted details.
  - Dilation: Expands the white areas in the mask, which can help fill in gaps and/or to cover the edges of the watermark.
  - On the images below, the middle one is the original mask, the left one is after erosion, and the right one is after dilation.
<p>
    <img src='gifs/erode.png' width='30%' />
    <img src='gifs/erode_dilate_original.png' width='30%' />
    <img src='gifs/dilate.png' width='30%' />
</p>

- After pressing the **"Finished mask"** button, set the parameters for the watermark removal. 
  - **mode**: It has two values:
    - **inpainting**: The watermark area is filled in using an inpainting algorithm, which tries to reconstruct the missing parts based on the surrounding pixels.
    - **most_common_color**: The watermark area is filled with the most common color in the image, which can be effective for simple watermarks on uniform backgrounds.
  - **w**: sharpening factor
  - **r_min, r_max, g_min, g_max, b_min, b_max**: These define the color range for the watermark. Pixels within this range are considered part of the watermark.
  - Every page can have its own color range and mode.
  - When checkbox is checked, the same parameters are used for all pages.
<p>
    <img src='gifs/range_wide.png' width='32%' />
    <img src='gifs/range_narrow.png' width='32%' />
    <img src='gifs/range_optimal.png' width='32%' />
</p>

- **Watermark Removal:** Removes the watermark from the images and saves the output as a new PDF file, either by filling the area with the most common color or by inpainting.





## Python Version Compatibility

This script is compatible with `Python 3.6` and above.

## Dependencies

The script requires the following Python libraries:

- `opencv-contrib-python`: For image processing tasks.
- `pymupdf`: For handling PDF files.
- `pyqt5`: For the graphical user interface.
- `Pillow`: For image handling.

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
   if virtualenv is not installed, you can install it with:
   ```bash
   apt-get install python3-venv  # on Ubuntu/Debian
   ```
   
   then activate the virtual environment:
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
    pip install opencv-contrib-python pymupdf PyQt5 Pillow
    ```

    if tkinter is not installed, you can install it with:
   - on Ubuntu/Debian:
        ```bash
        sudo apt-get install python3-tk
        ```

## Running the Script

```
python remover.py 
```


The arguments for the script are as follows (all are optional)
- **--pdf_path**: The path to the PDF file. Default is `input.pdf`.
- **--gui_type**: The type of GUI to use. Default is `tkinter`. Other option is `pyqt` (but it is not tested on all platforms)
- **--dpi**: The resolution of the images extracted from the PDF file. Default is `175`.
- **--max_width**: The maximum width of the images shown during the mask selection. Default is `900`.
- **--max_height**: The maximum height of the images shown during the mask selection. Default is `800`.


```
python remover.py --pdf_path=input.pdf --gui_type=pyqt5 --dpi 300 --max_width 1920 --max_height 1080
```


## Troubleshooting

- **Process is too slow:**

   The reading of large PDF files can be slow, especially if the resolution is high. If the process is too slow, try decreasing the `dpi` parameter.
    The progress of the image loading is shown in the console.

## Disclaimer

This script is for educational purposes only. The watermark removal process may not be perfect and may not work for all types of watermarks. The script may also remove parts of the image that are not watermarks. Use this script at your own risk.
