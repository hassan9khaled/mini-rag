from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
from models import ResponseSignal
import re, os, csv
from helpers.config import get_settings
import base64

settings = get_settings()

class DataController(BaseController):
    """Controller for handling data-related operations, such as file uploads and validations."""
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576
    
    def validate_csv_file(self, file_path: str):
        destination_path = file_path[:-4] + "_processed" + ".csv"
        
        try:
            # Open the input file in text mode, and the output file for writing
            # newline='' is crucial for the csv module to handle line endings correctly
            with open(file_path, mode='r', newline='', encoding='utf-8') as infile, \
                open(destination_path, mode='w', newline='', encoding='utf-8') as outfile:
                
                # Create reader and writer objects
                csv_reader = csv.reader(infile)
                csv_writer = csv.writer(outfile)

                # Process the header row first, if it exists
                try:
                    header = next(csv_reader)
                    csv_writer.writerow(header)
                    record_counter = 1
                except StopIteration:
                    # The file is empty, so we stop here
                    return False, False, ResponseSignal.FILE_IS_EMPTY.value

                # Iterate over the remaining rows
                for row in csv_reader:
                    # Write the row to the output file
                    csv_writer.writerow(row)
                    
                    # Increment the counter
                    record_counter += 1
                    
                    # Check if we've reached our limit
                    if record_counter > settings.CSV_FILE_MAX_RECORDS:
                        os.remove(file_path)
                        return destination_path, record_counter, ResponseSignal.RECORDS_EXCEEDED.value
        
        except FileNotFoundError:
            return
        except Exception as e:
            return False, False, ResponseSignal.PROCESSING_CSV_FAILED.value
        os.remove(file_path)
        return destination_path, record_counter, ResponseSignal.PROCESSING_CSV_SUCCESS.value
        
    def validate_uploaded_file(self, file: UploadFile):
        """Validates the uploaded file based on its type and size."""

        print(file.content_type)

        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        # Read the file to get its size
        contents = file.file.read()
        file_size = len(contents)
        file.file.seek(0)  # Reset file pointer for further use

        if file_size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, ResponseSignal.FILE_UPLOADED_SUCCESS.value  # Return True if all checks pass
    
    def generate_unique_filepath(self, original_file_name, project_name: str):
        """Generates a unique file path for the uploaded file."""

        # Generate a random key to ensure uniqueness
        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_name=project_name)
        cleaned_file_name = self.get_clean_file_name(original_file_name=original_file_name)
        
        new_file_path = os.path.join(
            project_path,
            random_key + "_" + cleaned_file_name
        )
        # Ensure the file path is unique
        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
                project_path,
                random_key + "_" + cleaned_file_name
            )

        return new_file_path, random_key + "_" + cleaned_file_name
    
        
    def get_clean_file_name(self, original_file_name: str):
        """Cleans the original file name by removing special characters and replacing spaces with underscores."""
        # remove any special characters, except underscore and .
        cleaned_file_name = re.sub(r'[^\w.]', '', original_file_name.strip())

        # replace spaces with underscore
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name        