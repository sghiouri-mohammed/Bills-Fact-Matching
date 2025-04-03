from src.server.api.extract_data import get_extracted_data
from src.server.api.matching import get_matching_rows
from src.server.api.upload import upload_file
from src.server.api.download import download_file
from src.server.api.delete import delete_file
from src.server.api.benchmark import benchmark, calculate_confusion_matrix
import pandas as pd

class APIService:
    def __init__(self):
        pass

    def get_extracted_data(self, image_path):
        return get_extracted_data(image_path)
    
    def get_matching_rows(self, csv_file_path, invoice_contents, threshold=70):
        return get_matching_rows(csv_file_path, invoice_contents, threshold)
    
    def upload_file(self, file_path, data):
        return upload_file(file_path, data)
    
    def download_file(self, file_path, data):
        return download_file(file_path, data)
    
    def delete_file(self, file_path):
        return delete_file(file_path)
    
    def benchmark(self, df, df_predicted):
        return benchmark(df, df_predicted)

    def calculate_confusion_matrix(self, csv_file_path, matching_results, image_filename):
        """
        Calculate confusion matrix for matching results.
        
        Args:
            csv_file_path: Path to the CSV file
            matching_results: List of matching results
            image_filename: Name of the image file
            
        Returns:
            dict: Dictionary containing confusion matrix and metrics
        """
        try:
            # Read CSV file
            df = pd.read_csv(csv_file_path)
            
            # Calculate confusion matrix
            return calculate_confusion_matrix(df, matching_results, image_filename)
        except Exception as e:
            print(f"Error calculating confusion matrix: {e}")
            return None

