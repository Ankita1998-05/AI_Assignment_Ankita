import streamlit as st
import whisper
from huggingface_hub import InferenceClient
import os
import tempfile

# Initialize Hugging Face client with token
client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
)

# Load the Whisper model once to improve performance
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

model = load_whisper_model()

# Set up the Streamlit app
st.title("Audio to Summary App 📝")
st.markdown("Upload an audio file (.mp3, .mp4, .wav) and get a summarized transcript.")

# File uploader widget
uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "mp4", "wav"])

if uploaded_file is not None:
    # Display a spinner while processing
    with st.spinner("Processing your audio..."):
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.type.split('/')[1]}") as tmp_file:
            tmp_file.write(uploaded_file.read())
            audio_path = tmp_file.name

        try:
            # Transcribe the audio using Whisper
            st.info("Transcribing audio...")
            result = model.transcribe(audio_path)
            transcript = result["text"]

            # Display the full transcript
            st.subheader("Full Transcript")
            st.text_area("Transcript", transcript, height=200)

            # Generate the summary using Mistral
            st.info("Summarizing the transcript...")
            messages = [
                {"role": "system", "content": "You are an assistant that summarizes messy voice-to-text into refined, professional, pointwise notes."},
                {"role": "user", "content": f"Here is the transcript:\n{transcript}\n\nSummarize into clear bullet points:"}
            ]

            response = client.chat_completion(messages=messages, max_tokens=200)
            summary = response.choices[0].message.content

            # Display the summary
            st.subheader("Summary")
            st.markdown(summary)

        except Exception as e:
            st.error(f"An error occurred: {e}")
        finally:
            # Clean up the temporary file
            os.unlink(audio_path)
