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


def euclidean_distance(image_path, point1, point2, vertical_fov_degrees=45, horizontal_fov_degrees=360, lidar_mount_angle=0.0):
    """
    Loads a range panorama and calculates the 3D Euclidean distance between two points using trigonometry.
    
    Args:
        image_path (str): Path to the range panorama image (distances encoded in mm).
        point1 (tuple): (x1, y1) pixel coordinates of the first point.
        point2 (tuple): (x2, y2) pixel coordinates of the second point.
        vertical_fov_degrees (float): Vertical field of view of the LiDAR in degrees (default: 45 degrees).
        horizontal_fov_degrees (float): Horizontal field of view of the LiDAR in degrees (default: 360 degrees).
        lidar_mount_angle (float): Additional mounting angle offset in radians if the LiDAR is tilted.
                                   Positive if tilted upwards, negative if tilted downwards.
    
    Returns:
        float: 3D Euclidean distance (in millimeters) between the two specified points.
    """
    # Load the range panorama using PIL and convert to a NumPy array
    image = Image.open(image_path)
    ranges = np.array(image)  # This array encodes distances in mm

    # Extract image dimensions
    image_height, image_width = ranges.shape

    # Calculate vertical and horizontal angular resolutions
    vertical_fov_radians = np.radians(vertical_fov_degrees)
    horizontal_fov_radians = np.radians(horizontal_fov_degrees)
    vertical_angle_per_pixel = vertical_fov_radians / image_height
    horizontal_angle_per_pixel = horizontal_fov_radians / image_width

    # Compute vertical angles for each row
    vertical_angles = (np.arange(image_height) - image_height / 2) * vertical_angle_per_pixel
    # Compute horizontal angles for each column
    horizontal_angles = (np.arange(image_width) - image_width / 2) * horizontal_angle_per_pixel

    # Extract pixel coordinates
    x1, y1 = point1
    x2, y2 = point2

    # Retrieve the range values (in mm) for the two points
    R1 = ranges[y1, x1]
    R2 = ranges[y2, x2]

    # Get the vertical and horizontal angles for the two points
    theta1_vertical = vertical_angles[y1] + lidar_mount_angle
    theta2_vertical = vertical_angles[y2] + lidar_mount_angle
    theta1_horizontal = horizontal_angles[x1]
    theta2_horizontal = horizontal_angles[x2]

    # Calculate 3D Cartesian coordinates for the two points
    # Point 1
    Z1 = R1 * np.sin(theta1_vertical)  # Height (vertical component)
    X1 = R1 * np.cos(theta1_vertical) * np.cos(theta1_horizontal)  # Forward (horizontal x-axis)
    Y1 = R1 * np.cos(theta1_vertical) * np.sin(theta1_horizontal)  # Sideways (horizontal y-axis)

    # Point 2
    Z2 = R2 * np.sin(theta2_vertical)  # Height (vertical component)
    X2 = R2 * np.cos(theta2_vertical) * np.cos(theta2_horizontal)  # Forward (horizontal x-axis)
    Y2 = R2 * np.cos(theta2_vertical) * np.sin(theta2_horizontal)  # Sideways (horizontal y-axis)

    # Calculate the 3D Euclidean distance between the two points
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
    
    point1 = (1000, 80)          # Example top pixel (x, y)
    point2 = (600, 110)       # Example bottom pixel (x, y)
    distance_mm = euclidean_distance(random_file, point1, point2)
    output_file = save_image_with_points_and_line(random_file, point1, point2)
    logging.info(f"3D distance between the two points: {distance_mm:.2f} mm")
    logging.info(f"Annotated image saved to: {output_file}")

    # Example usage for .npz temperature file processing
    random_npz_file = find_random_valid_file(directory, "*.npz")
    if random_npz_file:
        logging.info(f"Randomly selected .npz file: {random_npz_file}")
        # Calculate median temperature
        median_temperature = median_temperature_from_npz(random_npz_file)
    else:
        logging.warning("No matching .npz files found.")


