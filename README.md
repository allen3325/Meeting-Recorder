# GPT Demo Meeting Recorder

This project provides a minimal example of recording audio in the browser,
transcribing it with a speech-to-text model and letting GPT summarize the
conversation.

## Requirements

- Python 3.8+
- `flask`, `openai`, `python-dotenv`, and `google-generativeai` packages
- For local speech recognition:
  - `transformers` and `torch` for GPU/CPU
  - `mlx-whisper` when running on Apple&nbsp;Silicon (MPS)
- A valid OpenAI API key exported as `OPENAI_API_KEY` (only required when using OpenAI STT or summarization)
- A Google API key exported as `GOOGLE_API_KEY` if using Gemini summarization

## Running the server

Create a `.env` file in the project root to choose the speech-to-text backend:

```bash
STT_MODE=online  # or "local"
```

Then install the dependencies and start the server:

```bash
pip install -r requirements.txt
python app/server.py
```

The server exposes two endpoints:

- `/transcribe` &ndash; accepts a POST request with an audio file (form field
  `audio`) and returns the transcript text.
- `/summarize` &ndash; accepts a POST request with a JSON body containing
  `transcript_id` and returns a summarized version of that transcript.

Transcripts and summaries are saved under the `transcripts/` and `summaries/`
folders respectively. Temporary audio files are deleted after transcription.

## Frontend

Open `http://localhost:5000` in a browser (served by the Flask app). Press
**Start Recording** to record microphone audio. After stopping, the transcript
will appear along with a drop-down to choose **OpenAI** or **Gemini** for
summarization. Pick a model and then press **Summarize** to generate the
summary.
