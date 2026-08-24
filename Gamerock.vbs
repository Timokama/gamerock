Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\user\gamerock\gamerock"
WshShell.Run "venv\Scripts\pythonw.exe main.py", 0, False
