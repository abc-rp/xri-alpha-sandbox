
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

## `spec_modalities.py`

### Description
This script organizes and processes files based on specific modalities or file types. It identifies files by patterns, copies them to designated folders, and renames them to include a UPRN (Unique Property Reference Number).

### Features
- **File Categorization:** Matches files based on predefined patterns for different types.
- **Parallel Processing:** Uses Ray for faster execution.
- **Dynamic Renaming:** Renames files by appending a UPRN to their names.
- **Custom Filtering:** Processes specific file types or all types by default.

### Supported Types
The script recognizes various data modalities, such as:
- `icp_pcd`, `centre_pcd`, `nearir`, `range`, `reflec`, `signal`, `rgb`, `anon_mask`, `sam_mask`, `ir`.

There are some types that may not be immediately obvious what they are, e.g. `anon_mask` which provides the mask generated to remove humans and vehicales, `sam_mask` which is the segment anything masks, and `icp_pcd` and `centre_pcd` the two different pcd files.

### Usage
Run the script using the following command:
```bash
python spec_modalities.py -d <directory_path> -t <type>
```
- `-d`: Root directory to process (default: `../data`).
- `-t`: Specify the file type to process (e.g., `rgb`). If omitted, all types are processed.

---

## `loaders.py`

### Description
This script provides utility functions for loading pointclouds, range panoroma, and the radiometric temperature `.npz` files. This to show you how to load and use some file types you may not be familiar with

### Features
1. **Point Cloud Processing:**
   - Loads point cloud files (`.pcd`).
   - Estimates normals and computes FPFH (Fast Point Feature Histograms) features.

2. **Range Panorama:**
   - Loads range panorama images and calculates the median pixel distance.

3. **Temperature Data Processing:**
   - Loads the temperature `.npz` files and computes the median temperature, excluding NaN mask values.

4. **Random File Selection:**
   - Finds a random file matching a specific pattern within a directory.


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