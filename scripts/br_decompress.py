#!/usr/bin/env python3

import os
import brotli
import ray
from multiprocessing import cpu_count

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

        print(f"Decompressed and replaced: {input_file} -> {output_file}")
    except Exception as e:
        print(f"Error processing {input_file}: {e}")

def find_and_replace_pcd_br():
    """
    Finds all Brotli-compressed .pcd.br files in the current directory recursively,
    decompresses them, and replaces the original files with the decompressed .pcd files.
    """
    # Use the current directory as the root
    root_directory = os.getcwd()

    # Find all .pcd.br files
    pcd_br_files = []
    for root, _, files in os.walk(root_directory):
        for file in files:
            if file.endswith('.pcd.br'):
                pcd_br_files.append(os.path.join(root, file))

    # Create Ray tasks to decompress and replace each file
    tasks = [decompress_and_replace.remote(file) for file in pcd_br_files]

    # Execute the tasks in parallel
    ray.get(tasks)

    print("All decompression and replacement tasks completed.")

# Run the script
if __name__ == "__main__":
    find_and_replace_pcd_br()

    # Shutdown Ray after tasks are complete
    ray.shutdown()
