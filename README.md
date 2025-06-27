# GPT Demo Meeting Recorder

This project provides a minimal example of recording audio in the browser,
transcribing it with a speech-to-text model and letting GPT summarize the
conversation.

## Requirements

- Python 3.8+
- `flask` and `openai` Python packages
- A valid OpenAI API key exported as `OPENAI_API_KEY`

## Running the server

```bash
pip install flask openai
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
will appear and you can press **Summarize** to let GPT produce a summary.
