import os
import open3d as o3d
import logging
import fnmatch
import numpy as np
import random
from PIL import Image, ImageDraw
import math

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


def euclidean_distance(
    image_path,
    point1,
    point2,
    beam_altitude_angles,
    beam_azimuth_angles,
    lidar_mount_angle=0.0
):
    """
    Calculates the 3D Euclidean distance between two points in an Ouster OS1 range image
    using the Ouster-specific beam alt/az angles rather than uniform angle distribution.

    Args:
        image_path (str): Path to the range panorama image (distances in mm).
        point1 (tuple): (x1, y1) pixel coordinates of the first point.
        point2 (tuple): (x2, y2) pixel coordinates of the second point.
        beam_altitude_angles (list or np.ndarray): Vertical angles in degrees for each beam (row).
        beam_azimuth_angles (list or np.ndarray): Azimuth offsets in degrees for each beam (row).
        lidar_mount_angle (float): Additional mounting angle offset in radians.
                                   Positive if tilted upwards, negative if tilted downwards.

    Returns:
        float: 3D Euclidean distance (in millimeters).
    """

    # Load the range image
    image = Image.open(image_path)
    ranges = np.array(image)  # distances in mm

    image_height, image_width = ranges.shape

    # Convert degrees to radians for beam angles
    beam_altitude_angles_rad = np.radians(beam_altitude_angles)
    beam_azimuth_angles_rad = np.radians(beam_azimuth_angles)

    # Extract pixel coordinates
    x1, y1 = point1
    x2, y2 = point2

    # Retrieve the range values (in mm) for the two points
    R1 = ranges[y1, x1]
    R2 = ranges[y2, x2]

    # Get the per-beam vertical and azimuth angles
    theta1_vertical = beam_altitude_angles_rad[y1] + lidar_mount_angle
    theta2_vertical = beam_altitude_angles_rad[y2] + lidar_mount_angle

    # Compute horizontal angles
    # Basic approach: horizontal angle per column = 2π * (x / image_width)
    theta1_horizontal = (2 * np.pi * (x1 / image_width)) + beam_azimuth_angles_rad[y1]
    theta2_horizontal = (2 * np.pi * (x2 / image_width)) + beam_azimuth_angles_rad[y2]
    
    # Convert spherical coordinates to Cartesian coordinates for the first point
    Z1 = R1 * np.sin(theta1_vertical)  # Z1 coordinate
    X1 = R1 * np.cos(theta1_vertical) * np.cos(theta1_horizontal)  # X1 coordinate
    Y1 = R1 * np.cos(theta1_vertical) * np.sin(theta1_horizontal)  # Y1 coordinate

    # Convert spherical coordinates to Cartesian coordinates for the second point
    Z2 = R2 * np.sin(theta2_vertical)  # Z2 coordinate
    X2 = R2 * np.cos(theta2_vertical) * np.cos(theta2_horizontal)  # X2 coordinate
    Y2 = R2 * np.cos(theta2_vertical) * np.sin(theta2_horizontal)  # Y2 coordinate

    # Euclidean distance
    distance = np.sqrt((X2 - X1)**2 + (Y2 - Y1)**2 + (Z2 - Z1)**2)

    return distance

def save_image_with_points_and_line(image_path, point1, point2, output_directory="./"):
    """
    Saves a PNG image of the range panorama with the specified points and line drawn in red.
    
    Args:
        image_path (str): Path to the original range panorama image.
        point1 (tuple): (x1, y1) pixel coordinates of the first point.
        point2 (tuple): (x2, y2) pixel coordinates of the second point.
        output_directory (str): Directory to save the modified image (default: "./").
    
    Returns:
        str: File path of the saved image.
    """
    # Load the image in mono16
    image = Image.open(image_path)
    image_array = np.array(image)

    # Normalize the image to 8-bit
    image_array = (image_array / image_array.max() * 255).astype(np.uint8)

    # Convert to RGB by stacking the grayscale image into three channels
    image_rgb = np.stack((image_array,) * 3, axis=-1)

    # Convert to PIL Image
    image_rgb = Image.fromarray(image_rgb)
    draw = ImageDraw.Draw(image_rgb)

    # Draw the points
    radius = 5  # Radius for the points
    x1, y1 = point1
    x2, y2 = point2

    # Draw circles at the points
    draw.ellipse((x1 - radius, y1 - radius, x1 + radius, y1 + radius), fill="red")
    draw.ellipse((x2 - radius, y2 - radius, x2 + radius, y2 + radius), fill="red")

    # Draw the line connecting the points
    draw.line([point1, point2], fill="red", width=2)

    # Generate the output file name
    original_filename = os.path.basename(image_path)
    output_filename = os.path.join(output_directory, f"distance_{original_filename}")

    # Save the modified image
    image_rgb.save(output_filename)


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
    directory = DEFAULT_DATA_DIR

    # Load the JSON metadata file that contains beam information
    metadata_file_path = './scripts/beam_intrinsics.json'
    if os.path.exists(metadata_file_path):
        with open(metadata_file_path, 'r') as f:
            metadata = json.load(f)
        beam_altitude_angles = metadata["beam_intrinsics"]["beam_altitude_angles"]
        beam_azimuth_angles = metadata["beam_intrinsics"]["beam_azimuth_angles"]
    else:
        logging.warning("Metadata file not found. Using dummy data.")
        beam_altitude_angles = np.linspace(20, -20, 128)  # Dummy vertical angles
        beam_azimuth_angles = np.zeros(128)              # Dummy azimuth offsets

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
        
        # Calculate median distance (placeholder function)
        median_distance = range_pano(random_file)
    else:
        logging.warning("No matching files found.")
        random_file = None

    if random_file:
        point1 = (700, 80)   # Example pixel coordinates
        point2 = (600, 60)
        
        distance_mm = euclidean_distance(random_file, point1, point2, beam_altitude_angles, beam_azimuth_angles)
        output_file = save_image_with_points_and_line(random_file, point1, point2)
        logging.info(f"3D distance between the two points: {distance_mm:.2f} mm")
        logging.info(f"Annotated range panorama image saved to.")

    # Example usage for .npz temperature file processing
    random_npz_file = find_random_valid_file(directory, "*.npz")
    if random_npz_file:
        logging.info(f"Randomly selected .npz file: {random_npz_file}")
        # Calculate median temperature
        median_temperature = median_temperature_from_npz(random_npz_file)
    else:
        logging.warning("No matching .npz files found.")

