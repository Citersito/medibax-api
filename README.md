## Create a virtual venv
```
python -m venv .venv
```

## Activate a virtual venv
```
source .venv/bin/activate
```

## Install dependencies
```
pip install fastapi uvicorn
```

## Execute API
```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
