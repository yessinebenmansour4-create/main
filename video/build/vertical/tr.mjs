import { pipeline, env } from '@huggingface/transformers';
import fs from 'fs';
env.allowRemoteModels = false;
env.localModelPath = new URL('./node_modules/sts-whisper-small/models/', import.meta.url).pathname;
const buf = fs.readFileSync(process.argv[2]);
// 16-bit mono PCM wav, 44-byte header assumed (ffmpeg default)
const pcm = new Int16Array(buf.buffer, buf.byteOffset + 44, (buf.length - 44) >> 1);
const audio = Float32Array.from(pcm, v => v / 32768);
const asr = await pipeline('automatic-speech-recognition', 'Xenova/whisper-small', { dtype: 'q8' });
const mode = process.argv[3] || 'word';
const out = await asr(audio, { language: 'french', task: 'transcribe', chunk_length_s: 30, stride_length_s: 5,
  return_timestamps: mode === 'word' ? 'word' : true });
fs.writeFileSync(process.argv[4], JSON.stringify(out, null, 1));
console.log(out.text);
