# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install the dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    poppler-utils \
    libxkbcommon-x11-0 \
    libxcb-xinerama0

# Install the dependencies
RUN pip install pdf2image img2pdf opencv-contrib-python Flask flask-socketio

# Copy the necessary files and directories into the container
COPY static/ ./static/
COPY templates/ ./templates/
COPY utils.py .
COPY app.py .

# Expose the port the app runs on
EXPOSE 5000

# Set the environment variable for Flask
ENV FLASK_APP=app

# Run the Flask application
CMD ["flask", "run", "--host=0.0.0.0"]