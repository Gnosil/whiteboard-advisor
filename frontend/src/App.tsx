import { useCallback, useEffect, useRef, useState } from "react";
import { useSocket, type InboundMessage } from "./hooks/useSocket";
import { useRecorder } from "./hooks/useRecorder";
import { useTtsPlayer } from "./hooks/useTtsPlayer";
import Whiteboard from "./components/Whiteboard";
import type { AiMessage, Lang, ZoneMeta, ZoneStateEntry } from "./lib/types";

export default function App() {
  const [lang, setLang] = useState<Lang>("zh");
  const [zoneMeta, setZoneMeta] = useState<ZoneMeta[]>([]);
  const [zones, setZones] = useState<Record<string, ZoneStateEntry>>({});
  const [focus, setFocus] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<AiMessage[]>([]);
  const [thinking, setThinking] = useState(false);
  const [speechEnabled, setSpeechEnabled] = useState(false);
  const [text, setText] = useState("");
  const startedRef = useRef(false);
  const tts = useTtsPlayer();
  const recorder = useRecorder();

  const onMessage = useCallback((msg: InboundMessage) => {
    switch (msg.type) {
      case "session_started":
        setZoneMeta(msg.zones as ZoneMeta[]);
        setSpeechEnabled(!!msg.speechEnabled);
        break;
      case "asr_result":
        setTranscript((prev) => [...prev, { role: "user", text: msg.text as string }]);
        break;
      case "asr_failed":
        setThinking(false);
        setTranscript((prev) => [...prev, { role: "ai", text: `⚠ ${msg.message}` }]);
        break;
      case "tts_audio":
        tts.enqueue(msg.audio as string);
        break;
      case "thinking":
        setThinking(true);
        break;
      case "zone_update": {
        const zid = msg.zoneId as string;
        setZones((prev) => ({
          ...prev,
          [zid]: {
            id: zid,
            data: msg.data as Record<string, unknown>,
            version: msg.version as number,
            animation: msg.animation as ZoneStateEntry["animation"],
          },
        }));
        setFocus(zid);
        break;
      }
      case "ai_message":
        setThinking(false);
        setTranscript((prev) => [
          ...prev,
          { role: "ai", text: msg.narration as string, nextQuestion: (msg.nextQuestion as string) ?? null },
        ]);
        break;
      case "finalize":
        setThinking(false);
        break;
      case "error":
        setThinking(false);
        setTranscript((prev) => [...prev, { role: "ai", text: `⚠ ${msg.message}` }]);
        break;
    }
  }, []);

  const { status, send } = useSocket(onMessage);

  useEffect(() => {
    if (status === "open" && !startedRef.current) {
      startedRef.current = true;
      send({ type: "start", language: lang });
    }
  }, [status, send, lang]);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const t = text.trim();
    if (!t || thinking) return;
    setTranscript((prev) => [...prev, { role: "user", text: t }]);
    send({ type: "user_utterance", text: t });
    setText("");
  };

  const toggleMic = async () => {
    if (recorder.recording) {
      const audio = await recorder.stop();
      if (audio) {
        setThinking(true);
        send({ type: "audio", data: audio });
      }
    } else {
      tts.stop(); // 打断:用户开口立刻停掉 AI 解说
      await recorder.start();
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <header
        style={{
          padding: "12px 20px",
          borderBottom: "1px solid #232a33",
          display: "flex",
          alignItems: "center",
          gap: 12,
        }}
      >
        <strong style={{ fontSize: 18 }}>WhiteboardAdvisor</strong>
        <span style={{ color: "var(--muted)", fontSize: 13 }}>家庭保障规划</span>
        <div style={{ marginLeft: "auto", display: "flex", gap: 8, alignItems: "center" }}>
          <button
            onClick={() => setLang((l) => (l === "zh" ? "en" : "zh"))}
            style={{
              padding: "4px 10px",
              borderRadius: 6,
              border: "1px solid #2a323d",
              background: "transparent",
              color: "var(--ink)",
              fontSize: 12,
            }}
          >
            {lang === "zh" ? "中文" : "EN"}
          </button>
          <span style={{ fontSize: 13, color: status === "open" ? "#3ddc84" : "#ff7a7a" }}>
            {status === "open" ? "● 已连接" : "○ 连接中"}
          </span>
        </div>
      </header>

      <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
        <main style={{ flex: 1, padding: 20, display: "flex", minHeight: 0 }}>
          {zoneMeta.length > 0 ? (
            <Whiteboard meta={zoneMeta} zones={zones} focus={focus} lang={lang} />
          ) : (
            <div style={{ margin: "auto", color: "var(--muted)" }}>正在加载白板…</div>
          )}
        </main>

        <aside
          style={{
            width: 340,
            borderLeft: "1px solid #232a33",
            display: "flex",
            flexDirection: "column",
            minHeight: 0,
          }}
        >
          <div style={{ flex: 1, overflow: "auto", padding: 16, display: "flex", flexDirection: "column", gap: 10 }}>
            {transcript.length === 0 && (
              <p style={{ color: "var(--muted)", fontSize: 13 }}>
                试着说:「我 52 岁,香港,有三个孩子分别在多伦多、伦敦、上海,资产大概 300 万美金」
              </p>
            )}
            {transcript.map((m, i) => (
              <div key={i} style={{ alignSelf: m.role === "user" ? "flex-end" : "flex-start", maxWidth: "90%" }}>
                <div
                  style={{
                    background: m.role === "user" ? "var(--accent)" : "var(--panel)",
                    color: m.role === "user" ? "#fff" : "var(--ink)",
                    padding: "8px 12px",
                    borderRadius: 12,
                    fontSize: 14,
                    lineHeight: 1.5,
                  }}
                >
                  {m.text}
                </div>
                {m.nextQuestion && (
                  <div style={{ marginTop: 4, fontSize: 13, color: "var(--accent)" }}>❓ {m.nextQuestion}</div>
                )}
              </div>
            ))}
            {thinking && <div style={{ color: "var(--muted)", fontSize: 13 }}>AI 正在思考并作画…</div>}
          </div>

          <form onSubmit={submit} style={{ display: "flex", gap: 8, padding: 16, borderTop: "1px solid #232a33" }}>
            {speechEnabled && (
              <button
                type="button"
                onClick={toggleMic}
                title={recorder.recording ? "点击结束并发送" : "点击说话"}
                style={{
                  padding: "10px 14px",
                  borderRadius: 8,
                  border: "none",
                  background: recorder.recording ? "#ff5a5a" : "#2a323d",
                  color: "#fff",
                  fontSize: 16,
                }}
              >
                {recorder.recording ? "■" : "🎙"}
              </button>
            )}
            <input
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder={lang === "zh" ? "说点什么…" : "Say something…"}
              style={{
                flex: 1,
                padding: "10px 14px",
                borderRadius: 8,
                border: "1px solid #2a323d",
                background: "#0c0f13",
                color: "var(--ink)",
                fontSize: 14,
              }}
            />
            <button
              type="submit"
              disabled={thinking}
              style={{
                padding: "10px 16px",
                borderRadius: 8,
                border: "none",
                background: thinking ? "#2a323d" : "var(--accent)",
                color: "#fff",
                fontSize: 14,
              }}
            >
              发送
            </button>
          </form>
        </aside>
      </div>
    </div>
  );
}
