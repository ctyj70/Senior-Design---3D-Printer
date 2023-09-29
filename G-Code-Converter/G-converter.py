import os
import numpy
import shutil

outputFile = 'example.txt'
inputFile = './failed.gcode'

#need to be updated as print expands
radius:float = 84.5 #units are mm
previousZ:float = 0.0

# Takes an input file and opens it, reading each line in the file
def scanner (inputFile):
    with open(inputFile,'r') as fileRead:
        for line in fileRead:
            printLine(line)

# Processes G-Code and/or M-Code and writes them to an output file
def printLine(line):
    with open(outputFile,'a') as fileAppend:

        #check first character for comment
        if (line[0] == ';'):
            pass

        #check first character for new line/white space
        elif line[0] == '\n' or line[0] == '' or line[0] == ' ':
            pass

        #check first character for G code
        elif line[0] == 'G':
            line = convertCoordinates(line)
            fileAppend.write(f'\n{line}')

        #check for M code
        elif line[0] == 'M':
            line = convertCoordinates(line)
            fileAppend.write(f'\n{line}')
        #mostly does M, left as a catch-all
        else: 
            fileAppend.write(f'\t\t{line}')

# Processes G-code lines wth G1 commands, converts specific coordinates
# and updates them, while also handling comments and other cases by
# preserving/appending them to output string
def convertCoordinates(line):
    split = line.split()
    copy = split
    result = ''

    #convert G1
    if copy[0] == 'G1':
        result += copy[0]
        copy.pop(0)
        for _ in copy:
            #X: Up and down cylinder
            #Y: Horozontal above
            #Z: Vertical 
            #A: Rotate Cylinder
            #B: Rotate Printer head
            if(_[0] == 'X'):
                _ = _.replace('X', 'A') #CONVERT TO A
                degrees = _convertDegree(float(_[1:])) #output is location in degrees to move to
                _ = (f"{_[0]}{degrees}")
                result += (f" {_}")
            #convert Y to X
            elif(_[0] == 'Y'):
                #3DY -> 5DX
                _ = _.replace('Y', 'X') #CONVERT TO X
                result += (f" {_}")
            #convert Z to Z
            elif(_[0] == 'Z'):
                #3DZ -> 5DY
                _ = _.replace('Z', 'Z') #CONVERT TO Z
                result += (f" {_}")
                _updateRadius(float(_[1:])) #RADIUS MAY OR MAY NOT NEED TO BE UPDATED FOR THE A PLANE ROTATION 
                                            #AS THE ROTATION IS DONT NOT BY DISTANCE TRAVELLED BUT BY DEGREE POSITION
            elif not (_[0] == 'Z' or _[0] == 'Y' or _[0] == 'X'):
                if (_[0] == ';'):
                    result += (f"{_}")
                else:
                    result += (f" {_}")
    else:
        result = line
    return result

# Performs a conversion between units used in G Code and degrees
# (Most likely for scaling factor/dimensions for 3D Printer)
def _convertDegree(input:float):
    global radius
    return (input/radius)*(180/numpy.pi)

# Keeps 'radius' variable updated based on changes to Z-axis coordinate.
def _updateRadius(new:float):
    global radius
    global previousZ
    diff = new - previousZ
    radius += diff

# Processes G Code files found in a specific folder, clear contents of
# an output file (if it exists and isn't empty), and move both input and output
# files to seperate folders.
if __name__ == '__main__':
    #inputFile = input("path to file:\n")
    path = os.getcwd()
    INPUTNAME = 'INPUT G-CODE HERE'
    fileName = ''
    with os.scandir(path) as itr:
        for entry in itr:
            if entry.name == INPUTNAME:
                for fileSelect in os.listdir(path + '\\' + INPUTNAME):
                    inputFile = path + '\\' + INPUTNAME + '\\' + fileSelect
                    outputFile =  inputFile.replace('.gcode','.txt')
                    fileName = fileSelect

    # check if file exists and then check if it has contents
    if os.path.isfile(outputFile):
        if os.path.getsize(outputFile) > 0:
            open(outputFile,'w').close()

    # Handles Error when no input file is found.
    if (fileName == ''):
        print("ERROR -- NO FILE INPUT INTO FOLDER\nINSERT G-CODE IN \"INPUT G-CODE HERE\"")
    else:
        print("Starting Conversion Process...")
        scanner(inputFile)
        os.replace(inputFile, path + r'\\G-Code (Finished)\\' + fileName)
        
        print("Conversion Finished! Package G-Code?[Y/N]")
        answer = input()
        if (answer.capitalize() == "Y"):
            os.mkdir(path + "\\" + fileName + " Runtime Package")
            os.replace(outputFile, path + "\\" + fileName + " Runtime Package" + "\\" + fileName.replace('.gcode','.g'))
            shutil.copyfile(path + "\\Config Storage\\config.g", path + "\\" + fileName + " Runtime Package" + r"\\config.g")
        else:
            os.replace(outputFile, path + r'\\G-Code (Translated)\\' + fileName.replace('.gcode','.txt'))
    
