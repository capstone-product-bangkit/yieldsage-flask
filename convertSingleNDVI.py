import os
import rasterio
import numpy as np
import logging
import warnings
from rasterio.errors import NotGeoreferencedWarning
import matplotlib.pyplot as plt

def classify_health_status(average_ndvi):
    if average_ndvi < 0.2:
        return "Poor"
    elif 0.2 <= average_ndvi < 0.4:
        return "Moderate"
    elif 0.4 <= average_ndvi < 0.6:
        return "Good"
    else:
        return "Excellent"

def main():
    # Define the paths for the output directory
    ndvi_dir = 'Corn Multispectral/Multispectral-images/NDVI'

    # Create the NDVI directory if it doesn't exist
    os.makedirs(ndvi_dir, exist_ok=True)

    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Define the input paths for RED and NIR images
    red_path = 'path/to/red.tif'
    nir_path = 'path/to/nir.tif'

    # Ensure the RED and NIR files exist
    if not os.path.exists(red_path):
        logging.error(f"Red file does not exist: {red_path}")
        raise FileNotFoundError(f"Red file does not exist: {red_path}")
    if not os.path.exists(nir_path):
        logging.error(f"NIR file does not exist: {nir_path}")
        raise FileNotFoundError(f"NIR file does not exist: {nir_path}")

    # Construct the output NDVI file path
    red_filename = os.path.basename(red_path)
    ndvi_filename = red_filename.replace('RED', 'NDVI')
    ndvi_path = os.path.join(ndvi_dir, ndvi_filename)

    try:
        # Ignore the NotGeoreferencedWarning
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", NotGeoreferencedWarning)

            # Load the Red band
            with rasterio.open(red_path) as red_src:
                red_band = red_src.read(1).astype(float)
                red_meta = red_src.meta

            # Load the NIR band
            with rasterio.open(nir_path) as nir_src:
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
        print(f"Average NDVI for {red_path} and {nir_path}: {average_ndvi}")

        # Determine health status
        health_status = classify_health_status(average_ndvi)
        print(f"Health status: {health_status}")

        # Update metadata for the output file
        ndvi_meta = red_meta
        ndvi_meta.update(dtype=rasterio.float32, count=1)

        # Write the NDVI band to the output file
        with rasterio.open(ndvi_path, 'w', **ndvi_meta) as dst:
            dst.write(ndvi.astype(rasterio.float32), 1)

        logging.info(f"Successfully processed NDVI for {red_path}")

        # Plot the NDVI image
        plt.figure(figsize=(10, 6))
        plt.title(f"NDVI Image for {red_path} and {nir_path} - Health status: {health_status}")
        plt.imshow(ndvi, cmap='RdYlGn')
        plt.colorbar(label='NDVI value')
        plt.show()

    except Exception as e:
        logging.error(f"Failed to process {red_path} and {nir_path}: {e}")

if __name__ == "__main__":
    main()