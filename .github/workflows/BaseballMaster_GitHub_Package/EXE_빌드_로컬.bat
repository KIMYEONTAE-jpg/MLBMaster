@echo off
chcp 65001 > nul
python -m pip install pyinstaller
pyinstaller --noconfirm --clean --onefile --windowed --name BASEBALL_MASTER baseball_master.py
echo.
echo EXE 파일은 dist\BASEBALL_MASTER.exe 에 생성됩니다.
pause
