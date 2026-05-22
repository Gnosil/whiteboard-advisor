import { useState } from "react";
import { useSocket } from "./hooks/useSocket";

export default function App() {
  const { status, messages, send } = useSocket();
  const [text, setText] = useState("");

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <header
        style={{
          padding: "14px 20px",
          borderBottom: "1px solid #232a33",
          display: "flex",
          alignItems: "center",
          gap: 12,
        }}
      >
        <strong style={{ fontSize: 18 }}>WhiteboardAdvisor</strong>
        <span style={{ color: "var(--muted)", fontSize: 13 }}>v0.1 · 全栈骨架</span>
        <span style={{ marginLeft: "auto", fontSize: 13 }}>
          连接状态:{" "}
          <span style={{ color: status === "open" ? "#3ddc84" : "#ff7a7a" }}>
            {status === "open" ? "已连接" : status === "connecting" ? "连接中" : "已断开"}
          </span>
        </span>
      </header>

      <main style={{ flex: 1, display: "flex", flexDirection: "column", padding: 20, gap: 12 }}>
        <div
          style={{
            flex: 1,
            background: "var(--panel)",
            borderRadius: 12,
            padding: 16,
            overflow: "auto",
            fontFamily: "ui-monospace, monospace",
            fontSize: 13,
          }}
        >
          {messages.length === 0 ? (
            <span style={{ color: "var(--muted)" }}>白板将在这里渲染 —— 当前为 echo 骨架阶段。</span>
          ) : (
            messages.map((m, i) => (
              <div key={i} style={{ marginBottom: 6 }}>
                <span style={{ color: "var(--accent)" }}>{m.type}</span>{" "}
                <span style={{ color: "var(--muted)" }}>{JSON.stringify(m)}</span>
              </div>
            ))
          )}
        </div>

        <form
          style={{ display: "flex", gap: 8 }}
          onSubmit={(e) => {
            e.preventDefault();
            if (!text.trim()) return;
            send({ type: "user_utterance", text });
            setText("");
          }}
        >
          <input
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="输入一条消息测试连接…"
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
            style={{
              padding: "10px 18px",
              borderRadius: 8,
              border: "none",
              background: "var(--accent)",
              color: "#fff",
              fontSize: 14,
            }}
          >
            发送
          </button>
        </form>
      </main>
    </div>
  );
}
