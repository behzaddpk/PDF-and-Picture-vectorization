from fastapi import FastAPI, HTTPException, Form, UploadFile, APIRouter, File
from fastapi.responses import JSONResponse, StreamingResponse
import os
from pathlib import Path
import shutil
import pytesseract
from PIL import Image
import PyPDF2
from app.bot.vector_db import vectorize_to_supabase, load_document
import logging
import uuid
from app.bot.question import ask_question

logging.basicConfig(level=logging.INFO)

router = APIRouter()

@router.post('/upload-file/')
async def upload_file(file: UploadFile = File(...)):
    try:
        # Determine file extension and set metadata
        extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{extension}"
        metadata = {"file_name": file.filename}

        # Create the uploads directory if it doesn't exist
        file_path = f"documents/{unique_filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)

        documents = load_document(file_path, extension, metadata)

        # Log the documents structure
        logging.info(f"Documents: {documents}")

        vectorize_to_supabase(documents, file_path)
        return {"message": "File processed successfully", "documents": documents}

    except Exception as e:
        logging.error(f"Failed to upload file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {e}")

# Example of integrating the router into your FastAPI application
app = FastAPI()
app.include_router(router)


@router.post("/chat/")
async def chat(user_message: str = Form(...)):
    try:
        # Use the provided message to search for similar documents
        response_stream = ask_question(user_message)
        return StreamingResponse(response_stream)

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
