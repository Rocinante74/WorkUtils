import os
import shutil
from datetime import datetime
from watchfiles import run_process
import time
import csv

# Open the CSV file with the `csv` module to know where to copy files
with open('project_dict.csv') as csvfile:
    # Create a reader object from the CSV file
    reader = csv.reader(csvfile)

    # Create an empty dictionary
    destinations = {}

    for row in reader:
        # Iterate through the csv file and add a "My Drive" location for personal backup
        # Each row should be in this format:
        # JobNumber,DirectoryToCopyTo,SecondDirectoryToCopyTo

        number = row[0]
        dirs = row[1:]

        # Adding the "My Drive" folder + ensuring it exists
        my_drive_path = "G:\\My Drive\\Projects\\" + number
        if not os.path.exists(my_drive_path):
            os.mkdir(my_drive_path)
        my_drive_path = my_drive_path + "\\Prints"
        if not os.path.exists(my_drive_path):
            os.mkdir(my_drive_path)
        dirs.append(my_drive_path)

        destinations[number] = dirs

# The path to the folder that we want to watch
folder_to_watch = os.path.expanduser('~\Documents')


def run_script():
    # Add some sleep time to ensure the file is fully present
    time.sleep(5)

    # get pdf files in the directory
    pdf_files = [f for f in os.listdir(folder_to_watch) if f.endswith(".pdf")]

    # Loop through the PDF files
    for pdf_file in pdf_files:

        # Ignore files with "DNC" to enable ignoring PDFs to be edited before copying
        # Removing "DNC" will trigger another change in the folder, causing the file to be moved
        if "DNC" in pdf_file:
            continue

        # Get the current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d")

        # Construct the new file name
        new_file_name = timestamp + " - " + pdf_file

        # Get the job number
        job_number = ""
        for job_numbers in destinations:
            if job_numbers in pdf_file:
                job_number = job_numbers
                break
        if not job_number:
            continue

        # Use the job number to determine where the PDFs should go
        destination_folders = destinations[job_number]

        # Check if the destination folders exist - Shouldn't hit this
        for folder in destination_folders:
            if not folder:
                continue
            if not os.path.exists(folder):
                print("The destination folder '%s' does not exist. Please check the path and try again." % folder)
                continue

        # Copy the file to the destination folders
        for folder in destination_folders:
            if not folder:
                continue
            try:
                shutil.copy(os.path.join(folder_to_watch, pdf_file), os.path.join(folder, new_file_name))
            except:
                print("Something went wrong copying to '%s'. Maybe close the file?" % folder)

        # Delete the original file
        os.remove(os.path.join(folder_to_watch, pdf_file))


# Check if the watched folder exists first
if not os.path.exists(folder_to_watch):
    print("The folder to watch does not exist. Please check the path and try again.")
    exit()

if __name__ == '__main__':
    run_process(folder_to_watch, target=run_script)
