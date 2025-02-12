from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:8080",  # Ip del Front en Back
    # "http://192.168.137.184:8080",  # El Ip del fronend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def read_root():
    return {"Hello": "MediBax"}

@app.get("/test")
def test():
    return {"Test": "Coneccion Exitosa"}
