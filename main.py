import os
import shutil
from datetime import datetime
from typing import Dict, Any

from watchfiles import run_process
import time
import csv
import json


# The path(s) to the folder(s) that we want to watch
folder_to_watch = os.path.expanduser('~\Documents')
second_folder = os.path.expanduser('~\Downloads')


class CopyRobot:
    def __init__(self):
        self.calc_destinations = self.get_calc_destinations()
        self.plot_destinations = self.get_plot_destinations()

    def go(self, change_list):
        """
        this is the function to run everything (the target for the run_process function)
        :type change_list: list[list[str,str]]
        """
        time.sleep(5)
        for change in change_list:
            reason: str = change[0]
            path: str = change[1]

            folder = path.split("\\")[-2]
            file_name = path.split("\\")[-1]

            if reason == "deleted":
                continue

            if "DNC" in file_name:
                continue

            if folder == "Documents":
                self.documents_workflow(path)
            elif folder == "Downloads":
                self.downloads_workflow(path)

    def parse_dict_csv(self):
        pass

    def get_plot_destinations(self):
        # Open the CSV file with the `csv` module to know where to copy files
        with open('project_dict.csv') as csvfile:
            # Create a reader object from the CSV file
            reader = csv.reader(csvfile)

            # Create an empty dictionary
            plot_destinations = {}

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

                plot_destinations[number] = dirs
        return plot_destinations

    def get_calc_destinations(self):
        # Open the CSV file with the `csv` module to know where to copy files
        with open('calc_dict.csv') as csvfile:
            # Create a reader object from the CSV file
            reader = csv.reader(csvfile)

            # Create an empty dictionary
            plot_destinations = {}

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
                my_drive_path = my_drive_path + "\\Calcs"
                if not os.path.exists(my_drive_path):
                    os.mkdir(my_drive_path)
                dirs.append(my_drive_path)

                plot_destinations[number] = dirs
        return plot_destinations

    def documents_workflow(self, full_path):
        file_name = full_path.split("\\")[-1]

        for job_number in self.plot_destinations.keys():
            if job_number in file_name:
                folders_to_copy = self.plot_destinations[job_number]
                self.copy_files(full_path, folders_to_copy)

    def downloads_workflow(self, full_path):
        file_name = full_path.split("\\")[-1]

        for job_number in self.calc_destinations.keys():
            if job_number in file_name:
                folders_to_copy = self.calc_destinations[job_number]
                self.copy_files(full_path, folders_to_copy)

    def copy_files(self, file, folders_to_copy):
        for folder in folders_to_copy:
            if not folder:
                continue
            try:
                shutil.copy(file, os.path.join(folder, self.get_new_name(file)))

                # Delete the original file
                os.remove(file)
            except:
                print("Something went wrong copying to '%s'. Maybe close the file?" % folder)

    def get_new_name(self, file_path):
        file_name = file_path.split("\\")[-1]

        user_names = ["david-hood"]

        for user_name in user_names:
            name = "_" + user_name
            if name in file_name:
                file_name = file_name.replace(name, "")

        timestamp = datetime.now().strftime("%Y-%m-%d")
        new_file_name = timestamp + " - " + file_name

        return new_file_name


# Check if the watched folder exists first
if not os.path.exists(folder_to_watch):
    print("The folder to watch does not exist. Please check the path and try again.")
    exit()

copy_bot = CopyRobot()


def copy_process():
    # changes will be an empty list "[]" the first time the function is called
    # gives a list in the format [["reason 1 change", "path to file 1"], ["reason 2 change", "path to file 2"]]
    changes = os.getenv('WATCHFILES_CHANGES')
    changes = json.loads(changes)

    if not changes:
        # could use this for initial run
        return

    copy_bot.go(changes)


if __name__ == '__main__':
    run_process(folder_to_watch, second_folder, target=copy_process)
