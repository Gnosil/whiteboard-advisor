import { useCallback, useRef, useState } from "react";

const TARGET_RATE = 16000;

function downsample(buffer: Float32Array, inRate: number, outRate: number): Float32Array {
  if (outRate >= inRate) return buffer;
  const ratio = inRate / outRate;
  const outLen = Math.floor(buffer.length / ratio);
  const out = new Float32Array(outLen);
  for (let i = 0; i < outLen; i++) {
    out[i] = buffer[Math.floor(i * ratio)];
  }
  return out;
}

function floatToPcm16Base64(buffer: Float32Array): string {
  const pcm = new DataView(new ArrayBuffer(buffer.length * 2));
  for (let i = 0; i < buffer.length; i++) {
    const s = Math.max(-1, Math.min(1, buffer[i]));
    pcm.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  let binary = "";
  const bytes = new Uint8Array(pcm.buffer);
  for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
  return btoa(binary);
}

/** 录制 16kHz 单声道 16-bit PCM,stop 时返回 base64。 */
export function useRecorder() {
  const [recording, setRecording] = useState(false);
  const ctxRef = useRef<AudioContext | null>(null);
  const procRef = useRef<ScriptProcessorNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Float32Array[]>([]);

  const start = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    streamRef.current = stream;
    const ctx = new AudioContext();
    ctxRef.current = ctx;
    const source = ctx.createMediaStreamSource(stream);
    const proc = ctx.createScriptProcessor(4096, 1, 1);
    procRef.current = proc;
    chunksRef.current = [];
    proc.onaudioprocess = (e) => {
      chunksRef.current.push(new Float32Array(e.inputBuffer.getChannelData(0)));
    };
    source.connect(proc);
    proc.connect(ctx.destination);
    setRecording(true);
  }, []);

  const stop = useCallback(async (): Promise<string | null> => {
    const ctx = ctxRef.current;
    procRef.current?.disconnect();
    streamRef.current?.getTracks().forEach((t) => t.stop());
    setRecording(false);
    if (!ctx || chunksRef.current.length === 0) return null;

    const total = chunksRef.current.reduce((n, c) => n + c.length, 0);
    const merged = new Float32Array(total);
    let off = 0;
    for (const c of chunksRef.current) {
      merged.set(c, off);
      off += c.length;
    }
    const down = downsample(merged, ctx.sampleRate, TARGET_RATE);
    await ctx.close();
    ctxRef.current = null;
    return floatToPcm16Base64(down);
  }, []);

  return { recording, start, stop };
}
