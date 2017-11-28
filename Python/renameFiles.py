import os
import re


# This program Rename multiple files in a directory located
# in "path" and has common "pattern" to "newTitle+newPattern+part of old file to be kept"
# File name text to be kept is "offset" number of character to the right of pattern
# Exemple: "Game of throne S01E01.avi", "GOT_S01E02.avi", "Gameofthrones_S01E01.mkv"
# renamed to "GOT S01E01.avi", "GOT S01E02.avi", "GOT S01E03.mkv"
# pattern is "S01E" and offset is '2' and "newTitle" is "GOT "

def rename_files():
    # path, new_title, pattern, new_pattern, offset
    repeat = True
    while repeat:
        path = input('Path = ')
        new_title = input('Title = ')
        pattern = input('pattern = ')
        new_pattern = input('new Pattern = ')
        offset = int(input('Max Offset = '))

        # List all files in the directory
        files = os.listdir(path)
        i = 0
        new_names = []

        # Iterate through files
        for file in files:
            # Split file name from files extensions
            file_name, file_ext = os.path.splitext(file)

            # Detect where the pattern start is located
            # Returns -1 if its not found
            index = file_name.find(pattern)

            if index != -1:
                if new_pattern == '':
                    # Crop the file name from index to offset
                    file_name = file_name[index:index + int(len(pattern)) + offset]
                else:
                    # Crop the file number
                    file_name = file_name[index + int(len(pattern)):index + int(len(pattern)) + offset]
                    file_number = re.findall(r'\b\d+\b', file_name)
                    file_name = new_pattern + str(file_number[0]).zfill(2)
                # Assign new Common tiltle head and reassign extension                
                new_name = new_title + file_name + file_ext
                print("     " + file + "      " + new_name)
                new_names.insert(files.index(file), new_name)
            i = i + 1

        doit = input("Continue ? (y/n) = ") == 'y'

        if doit:
            i = 0
            for f in files:
                if f.find(pattern) != -1:
                    # Rename the file
                    os.rename(path + '\\' + f, path + '\\' + new_names[i])
                    i = i + 1
        # Exit or Restart

        repeat = input("Exit ? (y/n) = ") == 'n'
        os.system("cls")
    exit()


# Means run my function as this file main function
if __name__ == "__main__":
    rename_files()
