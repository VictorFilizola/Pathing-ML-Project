# My Data Science Project

## Overview
This project demonstrates an end-to-end data science workflow, including data ingestion, machine learning model creation, and a front-end application for user interaction. The application allows users to input addresses, generate optimized routes, and export them as PDF files.

## Project Structure
```
my-data-science-project
├── data
│   └── large.csv          # Dataset imported from Kaggle
├── models
│   └── pathing_model.pkl  # Machine learning model generated from the dataset
├── frontend
│   └── FrontEnd.py        # GUI application for PDF generation and routing
├── generatemodel
│   ├── CreateModel.py     # Script to create the machine learning model
│   └── ImportDataset.py   # Script to import the dataset
├── outputs                # Directory for generated PDF files and other outputs
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd my-data-science-project
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. **Import the Dataset**  
   Use the `ImportDataset.py` script to download and prepare the dataset:
   ```bash
   python generatemodel/ImportDataset.py
   ```

2. **Generate the Model**  
   Run the `CreateModel.py` script to process the dataset and create the machine learning model:
   ```bash
   python generatemodel/CreateModel.py
   ```

3. **Launch the Front-End Application**  
   Start the graphical interface to input addresses and generate PDF files:
   ```bash
   python frontend/FrontEnd.py
   ```

## Features
- **Dataset Import**: Automates the process of importing a dataset from Kaggle.
- **Model Creation**: Builds a machine learning model (`pathing_model.pkl`) using the imported dataset.
- **PDF Generation**: Provides a user-friendly interface for generating PDF files based on the model's output.
- **Routing Application**: Allows users to input addresses and generate optimized routes in PDF format.