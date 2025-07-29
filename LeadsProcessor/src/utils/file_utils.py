import os
from pathlib import Path

def get_csv_files(input_dir):
    return [f for f in Path(input_dir).glob("*.csv")]

def move_to_processed(file_path, dest_dir):
    Path(dest_dir).mkdir(parents=True, exist_ok=True)
    os.rename(file_path, Path(dest_dir) / Path(file_path).name)
