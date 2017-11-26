import os
import re

        ## This program Rename multiple files in a directory located
        ## in "path" and has common "pattern" to "newTitle+newPattern+part of old file to be kept"
        ## File name text to be kept is "offset" number of character to the right of pattern
        ## Exemple: "Game of throne S01E01.avi", "GOT_S01E02.avi", "Gameofthrones_S01E01.mkv"
        ## renamed to "GOT S01E01.avi", "GOT S01E02.avi", "GOT S01E03.mkv"
        ## pattern is "S01E" and offset is '2' and "newTitle" is "GOT "

def renameFiles():
    #path, newTitle, pattern, newPattern, offset
    repeat = True
    while repeat:
        path = input('Path = ')
        newTitle = input('Title = ')
        pattern = input('pattern = ')
        newPattern = input('new Pattern = ')
        offset = int(input('Max Offset = '))
        
        # List all files in the directory
        files = os.listdir(path)
        i = 0
        newNames = []
        
        # Iterate through files
        for file in files:
            # Split file name from files extensions
            fileName, fileExt = os.path.splitext(file)

            # Detect where the pattern start is located
            # Returns -1 if its not found
            index =fileName.find(pattern)            

            if index != -1:
                if newPattern == '':
                    # Crop the file name from index to offset
                    fileName = fileName[index:index+int(len(pattern))+offset]
                else:
                    # Crop the file number
                    fileName = fileName[index+int(len(pattern)):index+int(len(pattern))+offset]
                    fileNumber = re.findall(r'\b\d+\b', fileName)
                    fileName = newPattern + str(fileNumber[0]).zfill(2)
                # Assign new Common tiltle head and reassign extension                
                newName = newTitle +fileName+ fileExt
                print("     "+file + "      "+ newName)
                newNames.insert(files.index(file),newName)
            i= i+1
        
        doit = input("Continue ? (y/n) = ") == 'y'
        
        if doit:
            i=0
            for f in files:
                if f.find(pattern)!= -1:
                    # Rename the file
                    os.rename(path+'\\' + f, path+'\\' + newNames[i])
                    i = i+1
        # Exit or Restart
        
        repeat = input("Exit ? (y/n) = ") == 'n'
        os.system("cls")
    exit()

# Means run my function as this file main function
if __name__ == "__main__":
    renameFiles()