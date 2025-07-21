from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pdf2docx import Converter
import os
import uuid

app = FastAPI()

origins = [
    'http://localhost:5500',
    'http://localhost:8000',
    'http://127.0.0.1:5500',
    'http://127.0.0.1:8000',
    'https://fus-elearning.org',
    'https://www.fus-elearning.org'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/convert/")
async def convert(file: UploadFile = File(...)):
    output_dir = "converted"
    os.makedirs(output_dir, exist_ok=True)

    try:
        contents = await file.read()

        input_path = os.path.join(output_dir, f"{uuid.uuid4().hex}.pdf")
        output_filename = file.filename.replace('.pdf', '.docx')
        output_path = os.path.join(output_dir, output_filename)

        with open(input_path, "wb") as f:
            f.write(contents)
            f.flush()
            os.fsync(f.fileno())

        cv = Converter(input_path)
        try:
            cv.convert(output_path, start=0, end=None)
        finally:
            cv.close()

        return FileResponse(output_path, filename=os.path.basename(output_path))

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
