# Always run ADRS on port 8001
# GC-PGE prediction server uses port 8000
& d:\Downloads\GGC\Alternative_Drug\venv\Scripts\Activate.ps1
cd D:\Downloads\GGC\Alternative_Drug
uvicorn main:app --reload --port 8001