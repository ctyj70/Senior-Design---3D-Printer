import os
import numpy

outputFile = 'example.txt'
inputFile = './failed.gcode'

#need to be updated as print expands
radius:float = 84.5 #units are mm
previousZ:float = 0.0


def scanner (inputFile):
    with open(inputFile,'r') as fileRead:
        for line in fileRead:
            printLine(line)

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

def _convertDegree(input:float):
    global radius
    return (input/radius)*(180/numpy.pi)

def _updateRadius(new:float):
    global radius
    global previousZ
    diff = new - previousZ
    radius += diff

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
    
    if (fileName == ''):
        print("ERROR -- NO FILE INPUT INTO FOLDER\nINSERT G-CODE IN \"INPUT G-CODE HERE\"")
    else:
        scanner(inputFile)
        os.replace(inputFile, path + r'\\G-Code (Finished)\\' + fileName)
        os.replace(outputFile, path + r'\\G-Code (Translated)\\' + fileName.replace('.gcode','.txt'))
        print("Conversion Finished!")
    