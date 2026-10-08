import { pipeline, env } from '@huggingface/transformers';
import fs from 'fs';
env.allowRemoteModels = false;
env.localModelPath = new URL('./node_modules/sts-whisper-small/models/', import.meta.url).pathname;
const asr = await pipeline('automatic-speech-recognition', 'Xenova/whisper-small', { dtype: 'q8' });
const read = p => { const b = fs.readFileSync(p); const pcm = new Int16Array(b.buffer, b.byteOffset + 44, (b.length - 44) >> 1); return Float32Array.from(pcm, v => v / 32768); };
for (const p of process.argv.slice(2)) {
  const o = await asr(read(p), { language: 'french', task: 'transcribe' });
  console.log(p.split('/').pop().padEnd(22), '|', o.text.trim());
}
