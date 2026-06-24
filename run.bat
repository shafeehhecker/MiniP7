@echo off
set ROOT=%~dp0
set PYTHONPATH=%ROOT%packages\schema\src;%ROOT%packages\engine\src;%ROOT%packages\persistence\src;%ROOT%packages\services\src;%ROOT%apps\api\src
if "%MINIP7_DB%"=="" set MINIP7_DB=%ROOT%minip7.db
echo Mini-P7 running at http://127.0.0.1:8000   (API docs at /docs)
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
