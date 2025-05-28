import kaggle
import os

#Authenticate with Kaggle API
kaggle.api.authenticate()

data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

#Download and unzip the dataset into the 'data' folder
kaggle.api.dataset_download_files('mexwell/traveling-salesman-problem', path=data_dir, unzip=True)