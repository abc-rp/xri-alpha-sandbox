#!/usr/bin/env python3

import os
import brotli
import ray
import logging
import argparse
from multiprocessing import cpu_count

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Ray with half the available CPUs
ray.init(num_cpus=max(1, cpu_count() // 2))

@ray.remote
def decompress_and_replace(input_file):
    """
    Decompresses a Brotli-compressed .pcd.br file and replaces it with the decompressed .pcd file.

    :param input_file: Path to the Brotli-compressed .pcd.br file
    """
    try:
        # Define the output file by removing the '.br' extension
        output_file = input_file[:-3]  # Remove '.br'

        # Read the compressed data
        with open(input_file, 'rb') as compressed_file:
            compressed_data = compressed_file.read()

        # Decompress the data
        decompressed_data = brotli.decompress(compressed_data)

        # Write the decompressed data to the output file
        with open(output_file, 'wb') as decompressed_file:
            decompressed_file.write(decompressed_data)

        # Remove the original .pcd.br file
        os.remove(input_file)

        logging.info(f"Decompressed and replaced: {input_file} -> {output_file}")
    except Exception as e:
        logging.error(f"Error processing {input_file}: {e}")

def find_and_replace_pcd_br(directory):
    """
    Finds all Brotli-compressed .pcd.br files in the specified directory recursively,
    decompresses them, and replaces the original files with the decompressed .pcd files.

    :param directory: Path to the directory to search for .pcd.br files
    """
    if not os.path.exists(directory):
        logging.error(f"Directory not found: {directory}")
        return

    # Find all .pcd.br files
    pcd_br_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.pcd.br'):
                pcd_br_files.append(os.path.join(root, file))

    if not pcd_br_files:
        logging.warning(f"No .pcd.br files found in directory: {directory}")
        return

    logging.info(f"Found {len(pcd_br_files)} .pcd.br files to decompress.")

    # Create Ray tasks to decompress and replace each file
    tasks = [decompress_and_replace.remote(file) for file in pcd_br_files]

    # Execute the tasks in parallel
    ray.get(tasks)

    logging.info("All decompression and replacement tasks completed.")

def main():
    parser = argparse.ArgumentParser(description="Decompress Brotli-compressed .pcd.br files.")
    parser.add_argument(
        "-d", "--directory", 
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data'),
        help="Directory to search for .pcd.br files (default: ../data)"
    )
    args = parser.parse_args()

    logging.info(f"Using directory: {args.directory}")
    find_and_replace_pcd_br(args.directory)

    # Shutdown Ray after tasks are complete
    ray.shutdown()

if __name__ == "__main__":
    main()
