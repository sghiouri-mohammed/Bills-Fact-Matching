from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
import pandas as pd

def benchmark(df, df_predicted):
    """
    Calculate benchmark metrics for model predictions.
    
    Args:
        df (pd.DataFrame): Ground truth dataframe
        df_predicted (pd.DataFrame): Predictions dataframe
        
    Returns:
        dict: Dictionary containing benchmark metrics
    """
    # Merge the dataframes on common columns to align corresponding rows
    merged_df = pd.merge(df[['date', 'amount', 'currency', 'vendor', 'source']], 
                        df_predicted[['date', 'amount', 'currency', 'vendor', 'source']], 
                        on=['date', 'amount', 'currency', 'vendor'], 
                        suffixes=('_actual', '_predicted'))
    
    # Extract actual and predicted labels
    y_actual = merged_df['source_actual']
    y_predicted = merged_df['source_predicted']
    
    # Calculate metrics
    metrics = {
        'accuracy': accuracy_score(y_actual, y_predicted) * 100,
        'precision': precision_score(y_actual, y_predicted, average='weighted') * 100,
        'recall': recall_score(y_actual, y_predicted, average='weighted') * 100,
        'f1_score': f1_score(y_actual, y_predicted, average='weighted') * 100,
        'classification_report': classification_report(y_actual, y_predicted),
        'confusion_matrix': confusion_matrix(y_actual, y_predicted)
    }
    
    return metrics