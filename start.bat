@echo off

title Kim bolaman sayti

call .venv\Scripts\activate

python -m uvicorn app.main:app --reload

pause