import os
import uuid
from flask import Flask, request, jsonify, send_from_directory

from dotenv import load_dotenv

load_dotenv()

try:
    import openai
    client = openai.OpenAI()
except Exception:  # noqa: BLE001
    openai = None  # placeholder if openai package not installed
    client = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None  # placeholder if google-generativeai package not installed

app = Flask(__name__)

TRANSCRIPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'transcripts')
SUMMARIES_DIR = os.path.join(os.path.dirname(__file__), '..', 'summaries')
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
os.makedirs(SUMMARIES_DIR, exist_ok=True)
os.makedirs('tmp', exist_ok=True)

STT_MODE = os.getenv('STT_MODE', 'online').lower()


def local_transcribe(audio_path: str) -> str:
    """Transcribe audio using a local Whisper model."""
    try:
        import torch
    except ImportError:
        torch = None

    # Prefer MPS with mlx-whisper when available
    if torch and hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        try:
            from mlx_whisper import transcribe
            result = transcribe(audio_path, path_or_hf_repo="mlx-community/whisper-large-v3-turbo")
            return result.get("text", "")
        except Exception as e:  # noqa: BLE001
            return f"[Local MPS transcription error: {e}]"

    # Default to Hugging Face pipeline (supports GPU/CPU)
    try:
        from transformers import pipeline
        device = 0 if torch and torch.cuda.is_available() else -1
        asr = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-large-v3-turbo",
            device=device,
        )
        result = asr(audio_path)
        return result.get("text", "")
    except Exception as e:  # noqa: BLE001
        return f"[Local transcription error: {e}]"


@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory(FRONTEND_DIR, path)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    audio_file = request.files['audio']
    audio_path = os.path.join('tmp', f"{uuid.uuid4()}.wav")
    audio_file.save(audio_path)

    transcript_text = ""
    if STT_MODE == 'local':
        transcript_text = local_transcribe(audio_path)
    else:
        if client is None:
            transcript_text = "[OpenAI package not installed. Unable to transcribe.]"
        else:
            with open(audio_path, 'rb') as f:
                try:
                    response = client.audio.transcriptions.create(model='whisper-1', file=f)
                    transcript_text = response.text
                except Exception as e:  # noqa: BLE001
                    transcript_text = f"[Transcription error: {e}]"

    os.remove(audio_path)

    transcript_id = str(uuid.uuid4())
    transcript_path = os.path.join(TRANSCRIPTS_DIR, f"{transcript_id}.txt")
    with open(transcript_path, 'w', encoding='utf-8') as t_file:
        t_file.write(transcript_text)

    return jsonify({'transcript_id': transcript_id, 'text': transcript_text})

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json(force=True)
    transcript_id = data.get('transcript_id')
    model_choice = data.get('model', 'openai').lower()
    if not transcript_id:
        return jsonify({'error': 'transcript_id is required'}), 400

    transcript_path = os.path.join(TRANSCRIPTS_DIR, f"{transcript_id}.txt")
    if not os.path.exists(transcript_path):
        return jsonify({'error': 'transcript not found'}), 404

    with open(transcript_path, 'r', encoding='utf-8') as t_file:
        transcript_text = t_file.read()

    summary_text = ""

    if model_choice == 'gemini':
        if genai is None:
            summary_text = "[google-generativeai package not installed. Unable to summarize.]"
        else:
            try:
                genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
                model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17')
                response = model.generate_content(
                    f"Summarize the following meeting transcript.\n1. return in Traditional Chinese.\nmeeting transcript: {transcript_text}"
                )
                summary_text = response.text
            except Exception as e:
                summary_text = f"[Gemini summarization error: {e}]"
    else:
        if openai is None:
            summary_text = "[OpenAI package not installed. Unable to summarize.]"
        else:
            try:
                response = client.chat.completions.create(
                    model='gpt-4.1-nano',
                    messages=[
                        {'role': 'system', 'content': 'Summarize the following meeting transcript.\n1. return in Traditional Chinese.'},
                        {'role': 'user', 'content': transcript_text}
                    ]
                )
                summary_text = response.choices[0].message.content
            except Exception as e:
                summary_text = f"[Summarization error: {e}]"

    summary_path = os.path.join(SUMMARIES_DIR, f"{transcript_id}.txt")
    with open(summary_path, 'w', encoding='utf-8') as s_file:
        s_file.write(summary_text)

    return jsonify({'summary': summary_text})


@app.route('/history')
def history():
    """Return all transcripts with their summaries."""
    entries = []
    transcript_files = [
        (f, os.path.getmtime(os.path.join(TRANSCRIPTS_DIR, f)))
        for f in os.listdir(TRANSCRIPTS_DIR)
        if f.endswith('.txt')
    ]
    for fname, _ in sorted(transcript_files, key=lambda x: x[1]):
        transcript_id = os.path.splitext(fname)[0]
        with open(os.path.join(TRANSCRIPTS_DIR, fname), 'r', encoding='utf-8') as t_f:
            text = t_f.read()
        summary_path = os.path.join(SUMMARIES_DIR, f"{transcript_id}.txt")
        summary = ''
        if os.path.exists(summary_path):
            with open(summary_path, 'r', encoding='utf-8') as s_f:
                summary = s_f.read()
        entries.append({'id': transcript_id, 'text': text, 'summary': summary})
    return jsonify({'history': entries})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
