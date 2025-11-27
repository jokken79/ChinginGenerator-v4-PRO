@echo off
chcp 65001 >nul
cd /d "d:\ChinginGenerator-v4-PRO"
python -X utf8 -m uvicorn app:app --host 0.0.0.0 --port 8989
