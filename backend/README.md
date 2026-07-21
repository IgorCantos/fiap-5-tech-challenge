Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\.venv\Scripts\Activate.ps1

uvicorn app.main:app --reload

.venv/bin/python scripts/preview_dataset.py --n 20 --out preview --boxes