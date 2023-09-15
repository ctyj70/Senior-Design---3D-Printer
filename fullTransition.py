import os

if __name__ == '__main__':
    path = os.getcwd()
    INPUTNAME = 'Finished G-Code'
    fileName = 'error'
    with os.scandir(path + '\\SLICER\\') as itr:
        for entry in itr:
            if entry.name == INPUTNAME:
                for fileSelect in os.listdir(path + '\\SLICER\\' + INPUTNAME):
                    inputFile = path + '\\SLICER\\' + INPUTNAME + '\\' + fileSelect
                    fileName = fileSelect
    if (fileName == 'error'):
        print("ERROR -- No Finished G-Code Detected.")
    else:
        os.replace(inputFile, path + r'\\G-Code-Converter\\INPUT G-CODE HERE\\' + fileName)
    
