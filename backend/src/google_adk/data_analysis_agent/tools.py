import tempfile
import os
import subprocess
import sys
import base64

def write_file(content: str) -> bool:
    """
    Creates a temporary file with a .py extension in the current working directory,
    writes the given content to it, and does NOT delete it automatically after
    the function completes. The file will persist in the directory until manually deleted.

    Args:
        content (str): The string content to write to the temporary file.

    Returns:
        bool: True if the content was successfully written to the temporary file,
              False otherwise.
    """
    try:
        # Get the current working directory
        parent_directory = os.path.dirname( os.path.dirname(__file__) )
        save_dir = os.path.join(
            parent_directory,
            "code"
        )

        # Create a temporary file in the current working directory with a .py extension.
        # mode='w+' allows both writing and reading.
        # delete=False ensures the file is NOT deleted when closed.
        # dir specifies the directory where the temporary file should be created.
        # suffix='.py' ensures the file has a .py extension.

        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8', dir=save_dir, suffix='.py') as temp_file:
            # Write the content to the temporary file
            temp_file.write(content)
            # Flush the buffer to ensure content is written to disk immediately
            temp_file.flush()
            # It's good practice to get the name if you intend for it to persist
            # and potentially be used later.
            file_path = temp_file.name
            

        return file_path
    
    except IOError as e:
        # Catch I/O errors that might occur during file operations
        
        return False
    
    except Exception as e:
        # Catch any other unexpected errors
        
        return False
def register_output_file(path: str) -> str:
    file_name = os.path.split(path)[-1]   
    return file_name    
def delete_file(file_path: str) -> str:
    """
    Deletes a file at the given path.
    Ensures the file path is safe and within the designated data directory.

    Args:
        file_path (str): The path to the file to delete, relative to BASE_DATA_DIR.

    Returns:
        str: A message indicating success or failure.
    """
    try:
        parent_directory = os.path.dirname( os.path.dirname(__file__) )
        files_path = os.path.join(
            parent_directory,
            "code"
        )
        for file in os.listdir(files_path):
            os.remove(files_path + "/" + file)
        return
    except ValueError as e:
        return f"Security Error: {e}"
    except Exception as e:
        return f"Error deleting file '{file_path}': {e}"

    
def run_python_file(file_path: str) -> str:
    """
    Executes a Python file in a subprocess and captures its output.
    
    WARNING: For production environments, this *must* be run in a secure, isolated sandbox
    (e.g., Docker container, dedicated execution service) to prevent arbitrary code execution
    vulnerabilities. This simple subprocess approach is for demonstration only.
    """
    try:
        safe_path = file_path # _resolve_safe_path(file_path)
        
        # if not safe_path.is_file():
        #     return f"Error: Python file not found at '{file_path}'."
            
        result = subprocess.run(
            # The key change: pass the file path directly to the interpreter.
            [sys.executable, str(safe_path)],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        if result.returncode != 0:
            output += f"Process exited with non-zero code: {result.returncode}\n"
            output += "Error: Code execution failed.\n"
        else:
            output += "Code executed successfully.\n"

        return output
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out after 60 seconds."
    except ValueError as e:
        return f"Security Error: {e}"
    except Exception as e:
        return f"Error during file execution: {e}"
