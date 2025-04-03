import os

def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"File '{file_path}' has been deleted.")
        return {"success": True, "data":{"message": f"File '{file_path}' has been deleted."}}
    except FileNotFoundError:
        print(f"File '{file_path}' does not exist.")
        return {"success": False, "error":{"message": f"File '{file_path}' does not exist."}}
    except PermissionError:
        print(f"Permission denied to delete file '{file_path}'.")
        return {"success": False, "error":{"message": f"Permission denied to delete file '{file_path}'."}}
    except Exception as e:
        print(f"An error occurred while deleting file '{file_path}': {e}")
        return {"success": False, "error":{"message": f"An error occurred while deleting file '{file_path}': {e}"}}   
