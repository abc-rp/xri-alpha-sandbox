#!/bin/bash

# Get the latest git tag (or fallback to "no-tag" if none exists)
latest_tag=$(git describe --tags 2>/dev/null || echo "no-tag")

# Define the repository directory and output zips directory
repo_dir="$(pwd)"
repo_name="$(basename "$repo_dir")"
output_dir="${repo_dir}/zips"

# Create the zips directory if it doesn't exist
mkdir -p "$output_dir"

# Loop to create zip files for each part
for i in {1..6}; do
  (
    # Change to the parent directory
    cd "$(dirname "$repo_dir")"

    # Collect all tracked and untracked files, but not ignored files
    file_list=$(cd "$repo_dir" && git ls-files --cached --exclude-standard)

    # Prepare the list of files prefixed with repo_name/
    files_to_zip=""
    for file in $file_list; do
      files_to_zip+=" ${repo_name}/${file}"
    done

    # Explicitly include data/part-$i directory
    explicit_data="${repo_name}/data/part-$i"

    # Create the zip file in the zips directory
    zip -r -0 "${output_dir}/part-${i}-${latest_tag}.zip" $files_to_zip "$explicit_data" &
  )
done

# Wait for all background jobs to complete
wait

echo "All zip files created in ${output_dir}"
