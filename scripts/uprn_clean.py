#!/usr/bin/env python3

import os
import argparse
import pandas as pd
import shutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def delete_folders(directory, folder_list):
    """
    Deletes folders from the specified directory that match the provided list.

    :param directory: Root directory to search for folders
    :param folder_list: List of folder names to delete
    """
    if not os.path.exists(directory):
        logging.error(f"Directory not found: {directory}")
        return

    deleted = 0
    for folder_name in folder_list:
        folder_path = os.path.join(directory, str(folder_name))
        if os.path.isdir(folder_path):
            try:
                shutil.rmtree(folder_path)  # Recursively delete the directory
                logging.info(f"Deleted folder: {folder_path}")
                deleted += 1
            except Exception as e:
                logging.error(f"Failed to delete {folder_path}: {e}")
        else:
            logging.warning(f"Folder not found: {folder_path}")

    logging.info(f"Total folders deleted: {deleted}/{len(folder_list)}")

def main():
    parser = argparse.ArgumentParser(description="Delete folders listed in a CSV file.")
    parser.add_argument(
        "-d", "--directory",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data'),
        help="Root directory to process (default: ../data)"
    )
    parser.add_argument(
        "-f", "--file",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uprn_clean.csv'),
        help="Path to the CSV file containing folder names to delete (default: ./uprn_clean.csv)"
    )

    args = parser.parse_args()

    # Load folder names from the CSV file
    try:
        folder_data = pd.read_csv(args.file)
        folder_list = folder_data.iloc[:, 0].tolist()  # Assumes folder names are in the first column
    except Exception as e:
        logging.error(f"Failed to read the file: {e}")
        return

    logging.info(f"Loaded {len(folder_list)} folders to remove from: {args.file}")
    delete_folders(args.directory, folder_list)

if __name__ == "__main__":
    main()
