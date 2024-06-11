import os
import rasterio
import numpy as np
import logging
import warnings
from rasterio.errors import NotGeoreferencedWarning
import matplotlib.pyplot as plt
from rasterio.io import MemoryFile
from requirements import tf, np, cv2, base64, BytesIO, hashlib, requests


def classify_health_status(average_ndvi):
    if average_ndvi < 0.2:
        return "Poor"
    elif 0.2 <= average_ndvi < 0.4:
        return "Moderate"
    elif 0.4 <= average_ndvi < 0.6:
        return "Good"
    else:
        return "Excellent"

def calculate_ndvi(nir_image, red_image):

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", NotGeoreferencedWarning)

            with MemoryFile(red_image) as red_memfile:
                with red_memfile.open() as red_src:
                    red_band = red_src.read(1).astype(float)
                    red_meta = red_src.meta

            with MemoryFile(nir_image) as nir_memfile:
                with nir_memfile.open() as nir_src:
                    nir_band = nir_src.read(1).astype(float)
                    nir_meta = nir_src.meta

        # Calculate NDVI
        ndvi = np.where(
            (nir_band + red_band) == 0.,
            0,
            (nir_band - red_band) / (nir_band + red_band)
        )

        # Calculate the average NDVI
        average_ndvi = np.mean(ndvi[(nir_band + red_band) != 0])
        print(f"Average NDVI: {average_ndvi}")

        # Determine health status
        health_status = classify_health_status(average_ndvi)
        print(f"Health status: {health_status}")

        # Update metadata for the output file
        ndvi_meta = red_meta
        ndvi_meta.update(dtype=rasterio.float32, count=1)


        ndvi_base64 = ""
        with MemoryFile() as memfile:
            with memfile.open(**ndvi_meta) as dst:
                dst.write(ndvi.astype(rasterio.float32), 1)

            # Read the image back from memory file and encode as Base64
            with memfile.open() as src:
                ndvi_image = src.read(1)
                buffer = BytesIO()
                np.save(buffer, ndvi_image)
                buffer.seek(0)  # Ensure the buffer's position is at the start
                ndvi_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        # Plot the NDVI image
        return health_status, average_ndvi, ndvi_base64

    except Exception as e:
        logging.error(f"Failed to process red and nir image {e}")

def calculateNDVI():
    image_files = []
    image_urls = [
        'https://firebasestorage.googleapis.com/v0/b/capstone-project-yielsage.appspot.com/o/images%2FIMG_210204_100638_0349_NIR.tif?alt=media&token=0b211a20-c0ce-45a4-8915-ce9a3d1d0101',
        'https://firebasestorage.googleapis.com/v0/b/capstone-project-yielsage.appspot.com/o/images%2FIMG_210204_100638_0349_RED.tif?alt=media&token=185fef26-90da-49ec-8995-5ae0311548ba'
    ]

    for url in image_urls:
        response = requests.get(url)
        if response.status_code == 200:
            image = BytesIO(response.content).read()
            image_files.append(image)

    if len(image_files) == 2:
        result = calculate_ndvi(image_files[0], image_files[1])
        if result is not None:
            health_status, average_ndvi, ndvi_base64 = result
            print(health_status, average_ndvi, ndvi_base64)
        else:
            logging.error("Failed to calculate NDVI.")
    else:
        logging.error("Failed to download images or incorrect number of images.")


# if __name__ == '__main__':
#     calculateNDVI()