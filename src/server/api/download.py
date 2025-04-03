import streamlit as st
import pandas as pd
import io

# Function to convert DataFrame to CSV string
def convert_df_to_csv(df):
    # IMPORTANT: Use io.StringIO to create an in-memory text buffer
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)  # index=False to exclude the DataFrame index
    csv_buffer.seek(0)  # Go to the beginning of the buffer
    return csv_buffer.getvalue()

# You can also offer download as an Excel file:
def convert_df_to_excel(df):
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    return excel_buffer.getvalue()


def download_file(df, type='csv'):
    converted_data = None
    if type == 'csv':
        converted_data = convert_df_to_csv(df)
    else:
        converted_data = convert_df_to_excel(df)
        
    return converted_data