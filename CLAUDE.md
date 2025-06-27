# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

This is a full-stack meeting recorder with speech-to-text transcription and AI summarization:
- **Backend**: Flask server (`app/server.py`) running on port 4000
- **Frontend**: Vanilla HTML/CSS/JavaScript (`frontend/index.html`)
- **Storage**: File-based storage in `transcripts/` and `summaries/` directories

## Key Development Commands

### Setup and Installation
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
python app/server.py
```
Server runs on http://localhost:4000 (note: README mentions 5000 but code uses 4000)

### Environment Configuration
Copy `.env.example` to `.env` and configure:
- `STT_MODE`: "online" (OpenAI Whisper) or "local" (local models)
- `OPENAI_API_KEY`: Required for OpenAI services
- `GOOGLE_API_KEY`: Required for Gemini summarization

## Core Application Flow

1. **Audio Recording**: Browser captures microphone input with real-time visualization
2. **Transcription**: POST to `/transcribe` with audio file
   - Online mode: OpenAI Whisper-1 API
   - Local mode: Hugging Face Transformers or MLX-Whisper (Apple Silicon)
3. **Summarization**: POST to `/summarize` with transcript ID
   - Supports OpenAI GPT-4.1-nano or Google Gemini-2.5-flash-lite
   - Returns summary in Traditional Chinese
4. **History**: GET `/history` returns all previous transcripts and summaries

## File Structure

- `app/server.py`: Main Flask application with all endpoints
- `frontend/index.html`: Single-page application with audio recording UI
- `transcripts/{uuid}.txt`: Stored transcript files
- `summaries/{uuid}.txt`: Stored summary files
- `tmp/`: Temporary audio files (auto-deleted after processing)

## Technology Stack

**Backend Dependencies:**
- Flask (web framework)
- OpenAI (GPT-4.1-nano, Whisper-1)
- Google Generative AI (Gemini-2.5-flash-lite)
- Transformers + PyTorch (local Whisper-large-v3-turbo)
- MLX-Whisper (Apple Silicon optimization)

**Frontend APIs:**
- Web Audio API (microphone access)
- MediaRecorder API (audio capture)
- Canvas API (waveform visualization)
- Fetch API (backend communication)

## Important Notes

- Server port is 4000 (not 5000 as mentioned in README)
- Summaries are generated in Traditional Chinese
- Local transcription prefers MLX-Whisper on Apple Silicon
- No database - uses filesystem for persistence
- Audio files are temporarily stored then deleted after processing