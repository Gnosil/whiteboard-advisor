import { useEffect, useRef, useState, useCallback } from "react";

export type SocketStatus = "connecting" | "open" | "closed";

export interface InboundMessage {
  type: string;
  [key: string]: unknown;
}

export function useSocket(onMessage: (msg: InboundMessage) => void, path = "/ws/session") {
  const wsRef = useRef<WebSocket | null>(null);
  const cbRef = useRef(onMessage);
  cbRef.current = onMessage;
  const [status, setStatus] = useState<SocketStatus>("connecting");

  useEffect(() => {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${proto}://${location.host}${path}`);
    wsRef.current = ws;

    ws.onopen = () => setStatus("open");
    ws.onclose = () => setStatus("closed");
    ws.onmessage = (ev) => {
      try {
        cbRef.current(JSON.parse(ev.data) as InboundMessage);
      } catch {
        // ignore non-JSON frames
      }
    };

    return () => ws.close();
  }, [path]);

  const send = useCallback((data: unknown) => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(data));
  }, []);

  return { status, send };
}
