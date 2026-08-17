# Frontend (Flask)

## Setup for local

## macOS:

cd frontend
python3 -m venv venv          # first time only
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # first time only, then fill in the values
python app.py

## Windows (PowerShell):
cd frontend
python -m venv venv           # first time only
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env        # first time only, then fill in the values
python app.py