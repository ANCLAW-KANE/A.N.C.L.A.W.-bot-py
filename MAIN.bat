@echo off
set "searchPath=C:\Users\venvs\"
set "mask=venvvkbot-"
poetry config virtualenvs.path "%searchPath%"
poetry config virtualenvs.in-project false
cd .\venvvkbot\
echo ________________________ Installing ________________________
poetry install
dir "%searchPath%" /b | find "%mask%" > temp_vk.txt
for /f "tokens=*" %%f in (temp_vk.txt) do (
    set "vkbotvenvname=%%f"
)
del temp_vk.txt
set pathvenvvk=C:\Users\venvs\%vkbotvenvname%\Scripts\python.exe
poetry env use %pathvenvvk%
cd ..
echo ___________________________ Run ___________________________
%pathvenvvk% MAIN.py
pause