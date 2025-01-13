# Flask Web Application

This will be the web version of the PDF watermark remover app.


## Running the app

1. **Set the FLASK_APP environment variable**:
    ```sh
    export FLASK_APP=app
    ```

2. **Run the Flask app**:
    ```sh
    flask run
    ```

3. **Access the application**:
    Open your web browser and go to `http://127.0.0.1:5000/`.


## Running the App with Docker

1. **Build the Docker image**:
    ```sh
    docker build -t pdf-watermark-remover .
    ```

2. **Run the Docker container**:
    ```sh
    docker run -p 5000:5000 pdf-watermark-remover
    ```

3. **Access the application**:
    Open your web browser and go to `http://127.0.0.1:5000/`.


## Using the App

1. **Upload a PDF file**:
    Click on the `Choose File` button to upload a PDF file.

2. **Draw bounding box(es) around the watermark(s)**:
    Click and drag to draw a bounding box around the watermark in the uploaded PDF file.
3. **Refine the mask**:
   ![Description of the first image](assets/first-image-file.png)
    Threshold the mask.
    Use the `Erode` and `Dilate` buttons to refine the mask around the watermark.
4. **Set the color range**:
   Use the trackbars to set the color range for the mask.
   ![Description of the second image](assets/second-image-file.png)
5. **Remove watermark**:
    Click on the `Remove Watermark` button to remove the watermark from the uploaded PDF file.

TODO:
    - [ ] Add error handling for invalid PDF files.
