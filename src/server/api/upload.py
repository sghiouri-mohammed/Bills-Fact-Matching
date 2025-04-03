def upload_file(file_path, data):
    """
    Uploads data to the specified file path.

    Args:
        file_path (str): The path where the file will be saved.
        data (bytes): The data to be written to the file.
    """
    try:
        
        with open(file_path, 'wb') as file:
            file.write(data)
        print(f"File uploaded successfully to {file_path}")
        return {"success": True, "data":{"message": f"File uploaded successfully to {file_path}"}}
    except Exception as e:
        print(f"Error uploading file: {e}")
        return {"success": False, "error":{"message": f"Error uploading file: {e}"}}
