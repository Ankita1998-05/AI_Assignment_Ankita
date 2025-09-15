# app.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from huggingface_hub import InferenceClient
import os
import whisper
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Hugging Face Inference Client
hf_client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
)

# Load the Whisper model once to improve performance
model = whisper.load_model("base")

@app.post("/summarize_audio/")
async def summarize_audio(audio_file: UploadFile = File(...)):
    """
    Transcribes an uploaded audio/video file and summarizes the transcript.
    Supports MP3, MP4, and WAV formats.
    """
    # Check the file content type
    allowed_types = ["audio/mpeg", "audio/wav", "video/mp4"]
    if audio_file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {audio_file.content_type}. Please upload a WAV, MP3, or MP4 file."
        )

    # Save the uploaded file temporarily
    file_path = f"temp_{audio_file.filename}"
    with open(file_path, "wb") as f:
        f.write(await audio_file.read())

    try:
        # Transcribe the audio/video file using whisper-cpp
        # whisper-cpp automatically handles various formats (MP3, WAV, MP4, etc.)
        result = model.transcribe(file_path)
        transcript = result['text']

        # Prepare messages for the LLM
        messages = [
            {"role": "system", "content": "You are an assistant that summarizes messy voice-to-text into refined, professional, pointwise notes."},
            {"role": "user", "content": f"Here is the transcript:\n{transcript}\n\nSummarize into clear bullet points:"}
        ]

        # Get summary from Hugging Face model
        response = hf_client.chat_completion(messages=messages, max_tokens=200)
        summary = response.choices[0].message.content

        # Return the summary
        return {"transcript": transcript, "summary": summary}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up the temporary file
        os.remove(file_path)