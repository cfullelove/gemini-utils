# Meeting Transcript Summarizer

This project provides a FastAPI-based API endpoint to transcribe audio or video files and generate a summary of the conversation, including speaker diarization and action items. It utilizes Google's Generative AI (Gemini 2.5 Pro) for transcription and content generation.

## Features

- Transcribes audio and video files.
- Provides speaker diarization.
- Summarizes what each speaker discussed.
- Identifies action items, including who called for the action and who it was assigned to (if specified).
- Secured endpoint using Bearer token authentication.

## Prerequisites

- Python 3.7+
- Google Cloud API Key with access to the Generative AI (Gemini) services.

## Setup

1.  **Clone the repository (if applicable):**
    ```bash
    # git clone <repository-url>
    # cd <repository-directory>
    ```

2.  **Install dependencies:**
    This project uses FastAPI, Uvicorn (for running the server), python-dotenv, and the Google Generative AI SDK. You can install them using pip:
    ```bash
    pip install fastapi uvicorn python-dotenv google-generativeai
    ```
    It's recommended to use a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install fastapi uvicorn python-dotenv google-generativeai
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the root directory of the project and add your Google API Key:
    ```env
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
    ```
    The application will load this key automatically.

## Running the Application

You can run the FastAPI application using Uvicorn:

```bash
uvicorn main:app --reload
```

This will typically start the server on `http://127.0.0.1:8000`.

## API Endpoint

### `POST /transcribe/`

This endpoint accepts an audio or video file and returns its transcription and summary.

**Request:**

-   **Method:** `POST`
-   **URL:** `/transcribe/`
-   **Headers:**
    -   `Authorization: Bearer <YOUR_ACCESS_TOKEN>`
-   **Body:** `multipart/form-data`
    -   `file`: The audio or video file to be transcribed.

**Authentication:**

The endpoint requires a Bearer token for authentication. For this example, any non-empty token will be accepted. In a production environment, this token should be validated.

**Example cURL Request:**

```bash
curl -X POST "http://127.0.0.1:8000/transcribe/" \
     -H "Authorization: Bearer yoursecuretoken" \
     -F "file=@/path/to/your/audiofile.mp3"
```

**Successful Response (200 OK):**

```json
{
  "transcript": "Speaker 1 talked about X, Y, and Z. Speaker 2 discussed A, B, and C. Action: John to follow up on task P by EOD, assigned by Jane."
}
```

**Error Responses:**

-   **400 Bad Request:** If the uploaded file is not an audio or video type.
    ```json
    {
      "detail": "Invalid file type. Please upload an audio or video file."
    }
    ```
-   **401 Unauthorized:** If the Bearer token is missing or invalid.
    ```json
    {
      "detail": "Invalid authentication credentials",
      "headers": {
        "WWW-Authenticate": "Bearer"
      }
    }
    ```
-   **500 Internal Server Error:** If an error occurs during file processing or interaction with the Google API.
    ```json
    {
      "detail": "Google API Error: <error_message>"
    }
    ```
    or
    ```json
    {
      "detail": "An unexpected error occurred: <error_message>"
    }
    ```
    or
    ```json
    {
      "detail": "File upload failed with state: <state_code>"
    }
    ```

## How it Works

1.  **File Upload:** The client uploads an audio/video file to the `/transcribe/` endpoint.
2.  **Temporary Storage:** The file is temporarily saved on the server.
3.  **Google Cloud Upload:** The temporary file is uploaded to Google Cloud Storage using the Gemini Files API (`genai.upload_file`).
4.  **File Processing:** The system waits for Google to process the file and mark it as `ACTIVE`.
5.  **Transcription & Summarization:** The `gemini-2.5-pro-preview-03-25` model is invoked with the uploaded file and a prompt to generate a transcript, speaker diarization, summary of topics per speaker, and action items.
6.  **Cleanup:** The temporary file on the server and the uploaded file on Google Cloud Storage are deleted.

## Key Technologies

-   **FastAPI:** For building the API.
-   **Google Generative AI (Gemini 2.5 Pro):** For transcription, diarization, and summarization.
-   **python-dotenv:** For managing environment variables.
-   **Uvicorn:** ASGI server to run the FastAPI application.

## Future Improvements

-   Implement robust token validation.
-   Add more detailed error logging.
-   Support for more audio/video formats if needed.
-   Allow customization of the summarization prompt.
-   Asynchronous processing for very large files to avoid long request times.
