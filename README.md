# WhiteboardAdvisor

一款通过 AI「实时画白板 + 语音解说」模拟资深保险/财富经纪人开局规划演示的应用,面向海外华人 HNW 与北美 mass-affluent 人群。

> 核心范式:AI 不以 chat 输出结果,而是以 **streaming 白板 + TTS 同步解说** 作为 primary output。用户用语音输入 rough info,AI 在预定义 zone 骨架上填充并 narrate。

本仓库按 [PRD v0.1](./PRD_WhiteboardAdvisor_v0.1.md) 实现,当前聚焦 **V0.1 全栈最小可用闭环**。

## 技术栈

| 层 | 选型 |
|---|---|
| 前端 | React + Vite + TypeScript + framer-motion |
| 后端 | Python + FastAPI,WebSocket 流式推送 |
| LLM | 百度千帆大模型平台 (ERNIE) |
| 语音 | 百度智能云 ASR / TTS |

## 目录结构

```
backend/          FastAPI 服务
  app/
    main.py       入口 + WebSocket 会话通道
    config.py     双套千帆/百度凭证配置
    models/       数据模型 (User/Session/Zone/...)
    services/     Dialogue Manager / Zone Engine / LLM / 语音
    templates/    规划模板 (family-protection 等)
frontend/         React 客户端
  src/
    zones/        各 zone 的纯函数渲染组件
    components/   白板画布、语音、TTS 播放器
    hooks/        WebSocket / 会话状态
```

## 本地运行

### 后端

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 填入千帆 / 百度语音凭证
uvicorn app.main:app --reload --port 8000
```

健康检查:`curl http://localhost:8000/health`

### 前端

```bash
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173,右上角应显示「已连接」。

## 里程碑

- [x] **M1 全栈骨架** — FastAPI + WebSocket,前端连通
- [ ] **M2 Zone Engine + LLM** — family-protection 模板,文字版闭环
- [ ] **M3 语音闭环** — ASR + TTS + 打断处理
- [ ] **M4 持久化 + 打磨** — session autosave/resume,动画,中英切换

## 范围说明 (V0.1 不做)

不做账号体系(匿名 session)、RAG、broker handoff、PDF 导出、share link。详见 PRD §0 Non-goals。
