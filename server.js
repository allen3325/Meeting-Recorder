const fs = require('fs');
const path = require('path');
const express = require('express');
const fetch = require('node-fetch');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const DATA_PATH = path.join(__dirname, 'transcripts.json');

function loadData() {
  try {
    const raw = fs.readFileSync(DATA_PATH, 'utf8');
    return JSON.parse(raw);
  } catch (err) {
    return { transcripts: [] };
  }
}

function saveData(data) {
  fs.writeFileSync(DATA_PATH, JSON.stringify(data, null, 2));
}

// Store transcript
app.post('/transcript', (req, res) => {
  const { text } = req.body;
  if (!text) {
    return res.status(400).json({ error: 'No transcript text provided' });
  }
  const data = loadData();
  data.transcripts.push({ text, summary: null });
  saveData(data);
  res.json({ status: 'ok' });
});

// Summarize latest transcript using GPT
app.post('/summarize', async (req, res) => {
  const data = loadData();
  const last = data.transcripts[data.transcripts.length - 1];
  if (!last) {
    return res.status(400).json({ error: 'No transcript to summarize' });
  }
  if (last.summary) {
    return res.json({ summary: last.summary });
  }
  try {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      return res.status(500).json({ error: 'Missing OPENAI_API_KEY' });
    }
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: 'gpt-3.5-turbo',
        messages: [{ role: 'user', content: `Summarize the following conversation:\n${last.text}` }]
      })
    });
    const json = await response.json();
    const summary = json.choices && json.choices[0] && json.choices[0].message.content || '';
    last.summary = summary;
    saveData(data);
    res.json({ summary });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to summarize' });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
