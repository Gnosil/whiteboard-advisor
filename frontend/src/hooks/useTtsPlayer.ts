import { useCallback, useRef } from "react";

/** 顺序播放 base64 mp3 队列;stop() 立即中断(用户打断时调用)。 */
export function useTtsPlayer() {
  const queueRef = useRef<string[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const playingRef = useRef(false);

  const playNext = useCallback(() => {
    const next = queueRef.current.shift();
    if (!next) {
      playingRef.current = false;
      return;
    }
    playingRef.current = true;
    const audio = new Audio(`data:audio/mp3;base64,${next}`);
    audioRef.current = audio;
    audio.onended = () => playNext();
    audio.onerror = () => playNext();
    audio.play().catch(() => playNext());
  }, []);

  const enqueue = useCallback(
    (b64: string) => {
      queueRef.current.push(b64);
      if (!playingRef.current) playNext();
    },
    [playNext]
  );

  const stop = useCallback(() => {
    queueRef.current = [];
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    playingRef.current = false;
  }, []);

  return { enqueue, stop };
}
