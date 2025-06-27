# Meeting Recorder Demo

This project demonstrates a basic meeting recorder that converts audio to text using OpenAI's Whisper API and summarizes the conversation with GPT.

## Features

1. **Record Audio** – Record meeting audio in the browser. A blinking indicator shows when recording is active.
2. **Speech to Text** – After stopping the recording, the audio is sent to the server where Whisper transcribes it. The transcript is displayed on the page.
3. **Summarization** – A button allows you to request a GPT summary of the transcript. Both the transcript and summary are saved to `transcripts.json`.
4. **Cleanup** – The uploaded audio file is removed after transcription.

## Setup

1. Install dependencies

```bash
npm install
```

2. Set your OpenAI API key

```bash
export OPENAI_API_KEY=your_key_here
```

3. Start the server

```bash
npm start
```

4. Open `http://localhost:3000` in your browser.

## Files

- `server.js` – Express server handling uploads, transcription, and summarization.
- `public/` – Static front-end files.
- `transcripts.json` – Stores transcripts and summaries.

This is a minimal demonstration and may require additional error handling and security measures for production use.

