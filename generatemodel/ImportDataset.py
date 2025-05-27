import kaggle

#Authenticate with Kaggle API
kaggle.api.authenticate()

#Download and unzip the dataset into the 'data' folder
kaggle.api.dataset_download_files('mexwell/traveling-salesman-problem', path='../data', unzip=True)