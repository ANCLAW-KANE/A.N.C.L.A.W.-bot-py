poetry config virtualenvs.path "C:\\Users\\venvs"
poetry config virtualenvs.in-project false
cd .\venvvkbot\
poetry install

@REM заменить на имя окружения из C:\Users\venvs
set tgbotvenvname=venvvkbot-LAmQ-QDi-py3.11

set pathvenvtg=C:\Users\venvs\%tgbotvenvname%\Scripts\python.exe
poetry env use %pathvenvtg%
cd ..
%pathvenvtg% MAIN.py