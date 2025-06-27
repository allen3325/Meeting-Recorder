const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const summarizeBtn = document.getElementById('summarizeBtn');
const transcriptEl = document.getElementById('transcript');
const summaryEl = document.getElementById('summary');
const indicator = document.getElementById('recordingIndicator');

let recognition;
let transcriptText = '';

function initRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert('Speech Recognition not supported in this browser.');
    return null;
  }
  const recog = new SpeechRecognition();
  recog.interimResults = true;
  recog.continuous = true;
  recog.lang = 'en-US';
  recog.onresult = event => {
    let text = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      text += event.results[i][0].transcript;
    }
    transcriptText = text;
    transcriptEl.textContent = transcriptText;
  };
  recog.onend = () => {
    indicator.classList.add('hidden');
    startBtn.disabled = false;
    stopBtn.disabled = true;
    summarizeBtn.disabled = false;
    // Save transcript to server
    fetch('/transcript', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: transcriptText })
    });
  };
  return recog;
}

startBtn.addEventListener('click', () => {
  if (!recognition) {
    recognition = initRecognition();
    if (!recognition) return;
  }
  transcriptText = '';
  transcriptEl.textContent = '';
  summaryEl.textContent = '';
  startBtn.disabled = true;
  stopBtn.disabled = false;
  summarizeBtn.disabled = true;
  indicator.classList.remove('hidden');
  recognition.start();
});

stopBtn.addEventListener('click', () => {
  if (recognition) {
    recognition.stop();
  }
});

summarizeBtn.addEventListener('click', async () => {
  const res = await fetch('/summarize', { method: 'POST' });
  const data = await res.json();
  summaryEl.textContent = data.summary || data.error;
});
