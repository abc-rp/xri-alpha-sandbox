import os
import open3d as o3d
import logging
import fnmatch
import numpy as np
import random
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DEFAULT_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data')


def find_random_valid_file(directory, pattern):
    """
    Recursively finds a random file matching the pattern in the given directory.

    :param directory: Directory to search for files
    :param pattern: File name pattern to match (e.g., 'range*.png')
    :return: Path to a random matching file, or None if not found
    """
    matching_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if fnmatch.fnmatch(file, pattern):
                matching_files.append(os.path.join(root, file))
    
    if not matching_files:
        return None
    
    return random.choice(matching_files)


def point_cloud(file_path):
    """
    Loads a point cloud, estimates normals, and computes FPFH features.

    :param file_path: Path to the point cloud file
    """
    # Load the point cloud
    pcd = o3d.io.read_point_cloud(file_path)
    logging.info(f"Loaded point cloud from {file_path}")

    # Estimate normals
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    logging.info("Estimated normals")

    # Compute FPFH features
    fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        pcd,
        o3d.geometry.KDTreeSearchParamHybrid(radius=0.25, max_nn=100)
    )
    logging.info(f"Computed FPFH features with shape: {fpfh.data.shape}")

    return fpfh


def range_pano(image_path):
    """
    Loads an image and calculates the median distance of the pixels using PIL.
    
    Args:
    - image_path (str): Path to the image.
    
    Returns:
    - float: Median distance of the pixels.
    """
    # Load the image using PIL
    image = Image.open(image_path)
    
    # Convert to a NumPy array
    image_array = np.array(image)
    
    # Calculate the median distance of the pixels
    median_distance = np.median(image_array)
    logging.info(f"Median pixel distance: {median_distance} mm")

    return median_distance


def median_temperature_from_npz(file_path):
    """
    Loads an .npz file, calculates the median temperature excluding NaN values.

    :param file_path: Path to the .npz file
    :return: Median temperature as a float
    """
    try:
        # Load the .npz file
        data = np.load(file_path)

        # Calculate the median temperature, excluding NaN values
        median_temp = np.nanmedian(data)
        logging.info(f"Median temperature: {median_temp:.1f}°C")
        return median_temp

    except Exception as e:
        logging.error(f"Failed to process .npz file {file_path}: {e}")
        return None


if __name__ == "__main__":
    # Example usage for finding a random range image
    directory = DEFAULT_DATA_DIR

    # Example usage for point cloud processing
    point_cloud_file = find_random_valid_file(directory, "*.pcd")  # Assuming point cloud files are .pcd
    if point_cloud_file:
        fpfh_features = point_cloud(point_cloud_file)
        logging.info(f"FPFH features computed for {point_cloud_file}")
    else:
        logging.warning("No point cloud files found.")
    
    random_file = find_random_valid_file(directory, "range*.png")
    if random_file:
        logging.info(f"Randomly selected file: {random_file}")
        
        # Calculate median distance
        median_distance = range_pano(random_file)
    else:
        logging.warning("No matching files found.")

    # Example usage for .npz temperature file processing
    random_npz_file = find_random_valid_file(directory, "*.npz")
    if random_npz_file:
        logging.info(f"Randomly selected .npz file: {random_npz_file}")
        # Calculate median temperature
        median_temperature = median_temperature_from_npz(random_npz_file)
    else:
        logging.warning("No matching .npz files found.")
