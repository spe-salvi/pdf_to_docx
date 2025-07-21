from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pdf2docx import Converter
from zipfile import ZipFile
import os
import uuid

app = FastAPI()

origins = [
    'http://localhost:5500',
    'http://localhost:8000',
    'http://127.0.0.1:5500',
    'http://127.0.0.1:8000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/convert/")
async def convert(files: list[UploadFile] = File(...)):
    output_dir = "converted"
    os.makedirs(output_dir, exist_ok=True)

    docx_paths = []
    try:
        for file in files:
            contents = await file.read()

            input_path = f"/tmp/{uuid.uuid4().hex}.pdf"
            output_filename = file.filename.replace('.pdf', '.docx')
            output_path = os.path.join(output_dir, output_filename)

            # 🔧 Ensure /tmp directory exists
            os.makedirs(os.path.dirname(input_path), exist_ok=True)

            with open(input_path, "wb") as f:
                f.write(contents)

            cv = Converter(input_path)
            cv.convert(output_path, start=0, end=None)
            cv.close()

            docx_paths.append(output_path)

        if len(docx_paths) == 1:
            return FileResponse(docx_paths[0], filename=os.path.basename(docx_paths[0]))
        else:
            zip_path = os.path.join(output_dir, f"converted_{uuid.uuid4().hex}.zip")
            with ZipFile(zip_path, "w") as zipf:
                for docx in docx_paths:
                    zipf.write(docx, arcname=os.path.basename(docx))
            return FileResponse(zip_path, filename="converted_files.zip")

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)