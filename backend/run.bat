@echo off
python -m uvicorn main:app --host 0.0.0.0 --port 8003 --reload