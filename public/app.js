let mediaRecorder;
let chunks = [];
const recordBtn = document.getElementById('recordBtn');
const indicator = document.getElementById('recordingIndicator');
const transcriptEl = document.getElementById('transcript');
const summarizeBtn = document.getElementById('summarizeBtn');
const summaryEl = document.getElementById('summary');
let recordId;

recordBtn.addEventListener('click', async () => {
  if (!mediaRecorder || mediaRecorder.state === 'inactive') {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = e => chunks.push(e.data);
    mediaRecorder.onstop = uploadAudio;
    mediaRecorder.start();
    indicator.classList.remove('hidden');
    recordBtn.textContent = 'Stop Recording';
  } else {
    mediaRecorder.stop();
    indicator.classList.add('hidden');
    recordBtn.textContent = 'Start Recording';
  }
});

async function uploadAudio() {
  const blob = new Blob(chunks, { type: 'audio/webm' });
  chunks = [];
  const formData = new FormData();
  formData.append('audio', blob, 'recording.webm');
  const res = await fetch('/upload', { method: 'POST', body: formData });
  const data = await res.json();
  recordId = data.id;
  transcriptEl.textContent = data.text;
  summarizeBtn.classList.remove('hidden');
}

summarizeBtn.addEventListener('click', async () => {
  const res = await fetch('/summarize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id: recordId })
  });
  const data = await res.json();
  summaryEl.textContent = data.summary;
});
