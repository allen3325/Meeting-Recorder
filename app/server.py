import os
import uuid
from flask import Flask, request, jsonify, send_from_directory

try:
    import openai
except ImportError:
    openai = None  # placeholder if openai package not installed

app = Flask(__name__)

TRANSCRIPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'transcripts')
SUMMARIES_DIR = os.path.join(os.path.dirname(__file__), '..', 'summaries')
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
os.makedirs(SUMMARIES_DIR, exist_ok=True)
os.makedirs('tmp', exist_ok=True)


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
    if openai is None:
        transcript_text = "[OpenAI package not installed. Unable to transcribe.]"
    else:
        with open(audio_path, 'rb') as f:
            try:
                response = openai.Audio.transcribe('whisper-1', f)
                transcript_text = response['text']
            except Exception as e:
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
    if not transcript_id:
        return jsonify({'error': 'transcript_id is required'}), 400

    transcript_path = os.path.join(TRANSCRIPTS_DIR, f"{transcript_id}.txt")
    if not os.path.exists(transcript_path):
        return jsonify({'error': 'transcript not found'}), 404

    with open(transcript_path, 'r', encoding='utf-8') as t_file:
        transcript_text = t_file.read()

    summary_text = ""
    if openai is None:
        summary_text = "[OpenAI package not installed. Unable to summarize.]"
    else:
        try:
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[
                    {'role': 'system', 'content': 'Summarize the following meeting transcript.'},
                    {'role': 'user', 'content': transcript_text}
                ]
            )
            summary_text = response['choices'][0]['message']['content']
        except Exception as e:
            summary_text = f"[Summarization error: {e}]"

    summary_path = os.path.join(SUMMARIES_DIR, f"{transcript_id}.txt")
    with open(summary_path, 'w', encoding='utf-8') as s_file:
        s_file.write(summary_text)

    return jsonify({'summary': summary_text})

if __name__ == '__main__':
    app.run(debug=True)
