@echo off
set "searchPath=C:\Users\venvs\"
set "mask=venvtgbot-"
poetry config virtualenvs.path "%searchPath%"
poetry config virtualenvs.in-project false
cd .\venvtgbot\
echo ________________________ Installing ________________________
poetry install
dir "%searchPath%" /b | find "%mask%" > temp_tg.txt
for /f "tokens=*" %%f in (temp_tg.txt) do (
    set "tgbotvenvname=%%f"
)
del temp_tg.txt
set pathvenvtg=C:\Users\venvs\%tgbotvenvname%\Scripts\python.exe
poetry env use %pathvenvtg%
cd ..
echo ____________________________ Run ____________________________
::C:\Users\venvs\%tgbotvenvname%\Scripts\scalene.exe --html --profile-all MAIN3.py
::%pathvenvtg% -m cProfile -o dump.out MAIN3.py
%pathvenvtg% MAIN3.py
::C:\Users\venvs\%tgbotvenvname%\Scripts\pyinstrument.exe -r html -o dump.html MAIN3.py
::C:\Users\venvs\%tgbotvenvname%\Scripts\mprof run --include-children MAIN3.py
pause