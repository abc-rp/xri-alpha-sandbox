
# Script Documentation

This repository contains three Python scripts designed for different data processing tasks. Below is an explanation of each script and its functionality.

---

## `br_decompress.py`

### Description
This script is designed to recursively decompress Brotli-compressed `.pcd.br` files found in a specified directory. The original compressed files are replaced with their decompressed `.pcd` counterparts.

### Features
- **Decompression:** Uses the Brotli library to decompress files.
- **Parallel Processing:** Utilizes the Ray library for parallel task execution to enhance performance.
- **Recursive Search:** Searches all subdirectories for `.pcd.br` files.
- **Logging:** Provides detailed logs of the operations performed.

### Usage
Run the script using the following command:
```bash
python br_decompress.py -d <directory_path>
```
- `-d`: Path to the directory to search for `.pcd.br` files. Defaults to `../data`.

---

## `loaders.py`

### Description
This script provides utility functions for loading and processing various types of data files, including point clouds, images, and `.npz` files.

### Features
1. **Point Cloud Processing:**
   - Loads point cloud files (`.pcd`).
   - Estimates normals and computes FPFH (Fast Point Feature Histograms) features.

2. **Image Analysis:**
   - Loads images (e.g., range panorama images) and calculates the median pixel distance.

3. **Temperature Data Processing:**
   - Loads `.npz` files and computes the median temperature, excluding NaN values.

4. **Random File Selection:**
   - Finds a random file matching a specific pattern within a directory.

### Example Usage
- **Point Cloud Processing:**
  ```python
  point_cloud_file = find_random_valid_file(directory, "*.pcd")
  if point_cloud_file:
      features = point_cloud(point_cloud_file)
  ```
- **Image Analysis:**
  ```python
  image_path = find_random_valid_file(directory, "range*.png")
  if image_path:
      median_distance = range_pano(image_path)
  ```
- **Temperature Data:**
  ```python
  temp_file = find_random_valid_file(directory, "*.npz")
  if temp_file:
      median_temp = median_temperature_from_npz(temp_file)
  ```

---

## `spec_modalities.py`

### Description
This script organizes and processes files based on specific modalities or file types. It identifies files by patterns, copies them to designated folders, and renames them to include a UPRN (Unique Property Reference Number).

### Features
- **File Categorization:** Matches files based on predefined patterns for different types.
- **Parallel Processing:** Uses Ray for faster execution.
- **Dynamic Renaming:** Renames files by appending a UPRN to their names.
- **Custom Filtering:** Processes specific file types or all types by default.

### Supported Types
The script recognizes various file types, such as:
- `icp_pcd`, `centre`, `nearir`, `range`, `reflec`, `signal`, `rgb`, `anon_mask`, `sam_mask`, `ir`.

### Usage
Run the script using the following command:
```bash
python spec_modalities.py -d <directory_path> -t <type>
```
- `-d`: Root directory to process (default: `../data`).
- `-t`: Specify the file type to process (e.g., `rgb`). If omitted, all types are processed.

---

## Requirements

Ensure the following Python libraries are installed:
- `ray`
- `brotli`
- `open3d`
- `numpy`
- `Pillow` (PIL)

Install dependencies using pip:
```bash
pip install ray brotli open3d numpy Pillow
```

---

## Logging
All scripts include detailed logging to track operations and potential errors. Logs are displayed in the console.

## License
This project is open-source and licensed under [MIT License](LICENSE).

---

For questions or contributions, please create an issue or pull request.
