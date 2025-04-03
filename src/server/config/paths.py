import os

# Get the root directory of the project
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Define storage paths
STORAGE_DIR = os.path.join(ROOT_DIR, 'storage')
DATASET_DIR = os.path.join(STORAGE_DIR, 'dataset')
CSV_DIR = os.path.join(DATASET_DIR, 'csv')
IMAGES_DIR = os.path.join(DATASET_DIR, 'images')

# Create directories if they don't exist
for directory in [STORAGE_DIR, DATASET_DIR, CSV_DIR, IMAGES_DIR]:
    os.makedirs(directory, exist_ok=True) 