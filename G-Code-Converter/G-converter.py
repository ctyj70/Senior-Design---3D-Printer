import os
import numpy
import shutil

outputFile = 'example.txt'
inputFile = './failed.gcode'

#need to be updated as print expands
radius:float = 84.5 #units are mm
previousZ:float = 0.0
lastT = -1

# Takes an input file and opens it, reading each line in the file
def scanner (inputFile):
    print("Insert Additional Configurations in G-Code? (Y/N)")
    answer = input()
    if (answer.capitalize() == "Y"):
        printConfig(inputFile)
    
    with open(inputFile,'r') as fileRead:
        for line in fileRead:
            printLine(line)

def getInput (includedString, defaultVal):
    answer = input()
    if (answer == ""):
        return includedString + defaultVal + "\n"
    elif (answer.upper() == "SKIP"):
        return ""
    elif (not answer.isnumeric()):
        print("ERROR: NON-NUMERIC INPUT")
        return ""    
    else:
        return includedString + answer + "\n"

def getInputArray (includedString, defaultVal):
    repeatVal = len(includedString)
    totalString = ""
    for i in range(repeatVal):
        usableString = includedString[i].strip()
        if (usableString[0] == "M"): 
            usableString = usableString.split()[1]
        print("INSERT " + usableString + ":")
        answer = input()
        if (answer == ""):
            totalString += includedString[i] + defaultVal[i]
        elif (answer.upper() == "SKIP"):
            return ""
        elif (not answer.isnumeric()):
            print("ERROR: NON-NUMERIC INPUT")
            return ""
        else:
            totalString += includedString[i] + answer
    return totalString + "\n"

def printConfig (inputFile):
    with open(outputFile,'a') as fileAppend:
        print("Input the following values.\nYou may utilize a default value by pressing enter.\nYou may also skip a specific option by writing \"SKIP\".")
        
        # Microstepping With Interpolation
        #fileAppend.write("M350 X4 Y2 Z1 A8 B32 E16 I1\n")
        
        # Probe Speed
        print("INSERT PROBE SPEED:")
        fileAppend.write(getInput("M558 P0 H5 F120 T","6000"))
        
        # Regular Maximum Speeds
        print("INSERT REGULAR MAXIMUM SPEEDS:")
        fileAppend.write(getInputArray(["M203 X"," Y"," Z"," A"," B"," E"], ["300.00","600.00","120.00","240.00","45.00","4.00"]))
        
        # Steps per unit
        print("INSERT STEPS PER UNIT")
        fileAppend.write(getInputArray(["M92 X"," Y"," Z"," A"," B"," E"," S"],["25.00", "5.00","25.000","2.381","1.00","6.00","1"]))
        
        # Maximum Instantaneous Speeds
        print("INSERT MAXIMUM INSTANTANEOUS SPEEDS:")
        fileAppend.write(getInputArray(["M566 X"," Y"," Z"," A"," B"," E"],["200.00","200.00","20.00","20.00","20.00","120.00"]))
        
        # Set Accelerations
        #fileAppend.write("M201 X10.00 Y10.00 Z5.00 A5.00 B20.00 E250.00\n")
        # Set Motor Currents
        #fileAppend.write("M906 X2000 Y1000 Z2000 A2800 B2000 E800 I100\n")
        
        # Axis Limits (A Has no limit)
        #fileAppend.write("M208 X0 Y-227.1 Z84.5 A-360000000 B-1 S1\n")
        #fileAppend.write("M208 X280 Y102.9 Z287.5 A360000000 B1 S0\n")
        
        # Fan Power
        print("INSERT FAN POWER (0 to 255):")
        fileAppend.write(getInputArray(["M106 P0 S","\nM106 P1 S","\nM106 P2 S"],["255","255","255"]))
        
        # Temperature Settings
        print("INSERT TEMPERATURE:")
        fileAppend.write(getInputArray(["M143 H1 S","\nM143 H0 S"],["262","300"]))
        
        # Set Idle Timeout
        print("INSERT IDLE TIMEOUT (IN SECONDS):")
        fileAppend.write(getInput("M84 S","30"))

        print("CONTINUING WITH TRANSLATION...")
        fileAppend.close()
        
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
                _ = _.replace('Z', 'Y') #CONVERT TO Y
                result += (f" {_}")
                _updateRadius(float(_[1:])) #RADIUS MAY OR MAY NOT NEED TO BE UPDATED FOR THE A PLANE ROTATION 
                                            #AS THE ROTATION IS DONT NOT BY DISTANCE TRAVELLED BUT BY DEGREE POSITION
            elif not (_[0] == 'Z' or _[0] == 'Y' or _[0] == 'X'):
                if (_[0] == ';'):
                    result += (f"{_}")
                else:
                    result += (f" {_}")
    elif copy[0] == "M82": # Ignore this command when converting
        result = ""
    elif copy[0] == "M104" and "T" in copy[1]:
        tValue = get_number_from_string(line, "T")
        sValue = get_number_from_string(line, "S")
        
        result = "".join(["G10 P", str(int(tValue[0]) + 1), " S", sValue[
            0], " R", str(int(sValue[0]) - 50)])
    elif "M104 S" in line:
        afterS = int(get_number_from_string(line, 'S')[0])
        afterR = afterS - 50
        if last_T != -1:
            result = "G10 P" + str(lastT) + " S" + str(afterS) + " R" + str(afterR)
            last_T = -1
        else:
            result = ""
    elif 'T' in line:
        for i in range(0, len(line) - 1):
            if line[i] == 'T' and line[i + 1].isdigit():
                lastT = int(line[i + 1]) + 1
                result = ''
                break
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

def get_number_from_string(string, char_before):
    number_found, number, int_length = False, '', 0
    for char in string:
        if not number_found:  # This if statement looks for the first P because we know the number will be right after
            if char == char_before:
                number_found = True
        else:
            if char == ' ' or char == "\n":  # This looks for a space because once a space is found, the number has ended. This is useful in case the number is ever multiple digits.
                break
            else:  # This else block adds each number after the p to a string, and counts how many digits this is so that I can reconstruct the string where the number leaves off.
                number += char
                int_length += 1
    return [number, int_length]

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
        
        print("Conversion Finished!") 
        
        print("Package G-Code?[Y/N]")
        answer = input()
        if (answer.capitalize() == "Y"):
            os.mkdir(path + "\\" + fileName + " Runtime Package")
            os.replace(outputFile, path + "\\" + fileName + " Runtime Package" + "\\" + fileName.replace('.gcode','.g'))
            shutil.copyfile(path + "\\Config Storage\\config.g", path + "\\" + fileName + " Runtime Package" + r"\\config.g")
        else:
            os.replace(outputFile, path + r'\\G-Code (Translated)\\' + fileName.replace('.gcode','.txt'))
    