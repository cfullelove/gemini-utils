import os
import tempfile
import time
import os
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import exceptions

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

genai.configure(api_key=API_KEY)

app = FastAPI()
security_scheme = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    # In a real application, you would validate the token here.
    # For this example, we'll just check if a token is provided.
    if not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials # Return the token itself for now

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...), token: str = Depends(get_current_user)):
    if not file.content_type.startswith("audio/") and not file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload an audio or video file.",
        )

    # Create a temporary file to save the uploaded content
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name

    try:
        # Upload the file to Google Cloud Storage via Gemini Files API
        print(f"Uploading file: {tmp_file_path}")
        uploaded_file = genai.upload_file(path=tmp_file_path, mime_type=file.content_type)
        print(f"Uploaded file '{uploaded_file.display_name}' as: {uploaded_file.uri}")

        # Wait for the file to be active
        print("Waiting for file to be active...")
        file_status = genai.get_file(name=uploaded_file.name)
        # Assuming state 1 is PROCESSING and state 2 is ACTIVE based on previous error
        while file_status.state == 1: # Assuming 1 is PROCESSING
            print(f"File state: {file_status.state}")
            time.sleep(10)
            file_status = genai.get_file(name=uploaded_file.name)

        if file_status.state != 2: # Assuming 2 is ACTIVE
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File upload failed with state: {file_status.state}",
            )
        print(f"File state: {file_status.state}")

        # Call Gemini for transcription and diarization
        print("Calling Gemini for transcription and diarization...")
        model = genai.GenerativeModel("gemini-2.5-pro-preview-03-25") # Using 1.5 Pro as it has better audio capabilities
        response = model.generate_content(
            # [uploaded_file, "Generate a transcript with speaker diarization."]
            [uploaded_file, "For each speaker, summarise what they spoke about. Also include all actions, noting who called for the action, and who it was assigned to (if specified)"]
        )
        print("Gemini response received.")

        transcript = response.text

        return {"transcript": transcript}

    except exceptions.GoogleAPIError as e:
        print(f"Google API Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google API Error: {e}",
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}",
        )
    finally:
        # Clean up the temporary file
        os.remove(tmp_file_path)
        print(f"Temporary file removed: {tmp_file_path}")
        # Clean up the uploaded file from GCS
        if 'uploaded_file' in locals() and uploaded_file:
            try:
                genai.delete_file(name=uploaded_file.name)
                print(f"Uploaded file deleted from GCS: {uploaded_file.name}")
            except exceptions.GoogleAPIError as e:
                print(f"Failed to delete file from GCS: {e}")
