import os

def rename_files(base_dir):
    for root, _, files in os.walk(base_dir):
        for file in files:
            old_path = os.path.join(root, file)
            new_filename = file.lower().replace(" ", "_")
            new_path = os.path.join(root, new_filename)
            if old_path != new_path:  # Rename only if there's a change
                os.rename(old_path, new_path)
                print(f"Renamed: {old_path} -> {new_path}")

base_dir = "/Users/phoenix/Desktop/pythonscripts/nft-generator-py/trait-layers"
rename_files(base_dir)
