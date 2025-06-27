import express from 'express';
import multer from 'multer';
import fs from 'fs';
import { Configuration, OpenAIApi } from 'openai';

const app = express();
const upload = multer({ dest: 'uploads/' });

const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);

const transcriptsPath = './transcripts.json';

function loadTranscripts() {
  if (!fs.existsSync(transcriptsPath)) return [];
  return JSON.parse(fs.readFileSync(transcriptsPath));
}

function saveTranscripts(data) {
  fs.writeFileSync(transcriptsPath, JSON.stringify(data, null, 2));
}

app.use(express.static('public'));
app.use(express.json());

app.post('/upload', upload.single('audio'), async (req, res) => {
  const filePath = req.file.path;
  try {
    // Call Whisper STT
    const response = await openai.createTranscription(
      fs.createReadStream(filePath),
      'whisper-1'
    );
    const text = response.data.text;
    const transcripts = loadTranscripts();
    const record = { id: Date.now(), text };
    transcripts.push(record);
    saveTranscripts(transcripts);
    fs.unlinkSync(filePath); // remove audio file
    res.json(record);
  } catch (err) {
    console.error(err);
    fs.unlinkSync(filePath);
    res.status(500).json({ error: 'Failed to transcribe audio' });
  }
});

app.post('/summarize', async (req, res) => {
  const { id } = req.body;
  const transcripts = loadTranscripts();
  const record = transcripts.find(r => r.id === id);
  if (!record) return res.status(404).json({ error: 'Record not found' });
  try {
    const completion = await openai.createChatCompletion({
      model: 'gpt-3.5-turbo',
      messages: [{ role: 'user', content: `Summarize this meeting: ${record.text}` }],
    });
    const summary = completion.data.choices[0].message.content;
    record.summary = summary;
    saveTranscripts(transcripts);
    res.json({ summary });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to summarize transcript' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
