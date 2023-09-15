cd %~dp0

move ".\SLICER\INPUT STL FILE HERE" ".\INPUT STL FILE HERE TEMP"
move ".\INPUT STL FILE HERE" ".\SLICER\INPUT STL FILE HERE"
cd ".\SLICER"

call ".\Run Slicer Program.bat"

cd "..\"
move ".\SLICER\INPUT STL FILE HERE" ".\INPUT STL FILE HERE"
move ".\INPUT STL FILE HERE TEMP" ".\SLICER\INPUT STL FILE HERE"

python3 .\fullTransition.py

cd ".\G-Code-Converter"

call ".\Run G-Code Program"