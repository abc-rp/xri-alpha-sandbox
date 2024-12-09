#!/usr/bin/env python3

import os
import sys
import shutil
import logging
import argparse
from multiprocessing import cpu_count
import ray

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Ray with half the available CPUs
ray.init(num_cpus=max(1, cpu_count() // 2))

# Supported types and their corresponding file patterns
FILE_PATTERNS = {
    'icp_pcd': ['icp_merged.pcd.br', 'icp_merged.pcd'],
    'centre': ['centre.pcd.br', 'centre.pcd.br'],
    'nearir': ['nearir_*.png'],
    'range': ['range_*.png'],
    'reflec': ['reflec_*.png'],
    'signal': ['signal_*.png'],
    'rgb': ['rgb_*.jpeg'],
    'anon_mask': ['rgb_*.json'],
    'sam_mask': ['sam_mask_rgb_*.jpeg', 'sam_mask_rgb_*.npz'],
    'ir': ['ir_temp_*.npz']
}

def find_files_by_type(directory, file_patterns):
    """
    Recursively find files in a directory that match the specified patterns.

    :param directory: Directory to search
    :param file_patterns: List of file patterns to match
    :return: List of matching files
    """
    matching_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            for pattern in file_patterns:
                if pattern.startswith('*'):
                    if file.endswith(pattern[1:]):
                        matching_files.append(os.path.join(root, file))
                elif pattern.endswith('*'):
                    if file.startswith(pattern[:-1]):
                        matching_files.append(os.path.join(root, file))
                elif '*' in pattern:
                    prefix, suffix = pattern.split('*')
                    if file.startswith(prefix) and file.endswith(suffix):
                        matching_files.append(os.path.join(root, file))
                else:
                    if file == pattern:
                        matching_files.append(os.path.join(root, file))
    return matching_files

@ray.remote
def copy_and_rename_file(src_file, dest_dir, uprn):
    """
    Copies a file to the destination directory, renaming it to include the <UPRN>.

    :param src_file: Source file path
    :param dest_dir: Destination directory path
    :param uprn: UPRN to prepend to the filename
    """
    try:
        os.makedirs(dest_dir, exist_ok=True)
        file_name = os.path.basename(src_file)
        dest_file = os.path.join(dest_dir, f"{uprn}_{file_name}")
        shutil.copy2(src_file, dest_file)
        logging.info(f"Copied {src_file} -> {dest_file}")
        return 1
    except Exception as e:
        logging.error(f"Failed to copy {src_file}: {e}")
        return 0

def process_directory(directory, type=None):
    """
    Processes the specified directory to gather files of the given type
    and copies them to a corresponding folder with filenames modified to
    include the <UPRN>.

    :param directory: Root directory to process
    :param type: Specific type to process (or None for all types)
    """
    if not os.path.exists(directory):
        logging.error(f"Directory not found: {directory}")
        sys.exit(1)

    types_to_process = [type] if type else FILE_PATTERNS.keys()
    total_files_moved = {t: 0 for t in types_to_process}
    
    for t in types_to_process:
        if t not in FILE_PATTERNS:
            logging.warning(f"Unsupported type: {t}")
            continue

        logging.info(f"Processing type: {t}")

        # Destination folder for the current type
        dest_dir = os.path.join(directory, t)

        # Find files matching the current type patterns
        matching_files = find_files_by_type(directory, FILE_PATTERNS[t])
        if not matching_files:
            logging.info(f"No files found for type: {t}")
            continue

        # Extract UPRN and process files
        tasks = []
        for file in matching_files:
            parts = file.split(os.sep)
            uprn = parts[-3] if len(parts) > 2 else "unknown"
            tasks.append(copy_and_rename_file.remote(file, dest_dir, uprn))

        # Wait for all copy tasks to complete and count the moved files
        results = ray.get(tasks)
        total_files_moved[t] = sum(results)

    logging.info("Processing complete.")
    for t, count in total_files_moved.items():
        logging.info(f"Total files moved to {t} folder: {count}")

def main():
    parser = argparse.ArgumentParser(description="Process and organize files by type.")
    parser.add_argument(
        "-d", "--directory", 
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data'),
        help="Root directory to process (default: ../data)"
    )
    parser.add_argument(
        "-t", "--type", 
        choices=FILE_PATTERNS.keys(),
        help="Specific type of file to process (e.g., 'rgb', 'nearir'). Process all types if omitted."
    )

    args = parser.parse_args()

    logging.info(f"Using directory: {args.directory}")
    if args.type:
        logging.info(f"Filtering by type: {args.type}")

    process_directory(args.directory, args.type)

    # Shutdown Ray
    ray.shutdown()

if __name__ == "__main__":
    main()