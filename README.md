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
- [x] **M2 Zone Engine + LLM** — family-protection 模板,文字版闭环
- [x] **M3 语音闭环** — 百度 ASR(16k PCM 录音)+ TTS + 打断处理
- [ ] **M4 持久化 + 打磨** — session autosave/resume,动画,中英切换

> 语音需在 `backend/.env` 配 `BAIDU_SPEECH_API_KEY` / `BAIDU_SPEECH_SECRET_KEY`;未配时前端隐藏麦克风、降级为文字。
> LLM 未配 `QIANFAN_API_KEY` 时走 mock 数据跑通流程。

## 知识库 (RAG)

`app/data/knowledge_seed.json` 是人工 curate 的 US/HK 公开规则种子库,`app/services/rag.py`
按 (jurisdiction × query) 关键词召回并注入 LLM prompt,每条带 `source` 可追溯。

`scripts/scrape_sample.py` 是**单页抓取样例**(非全量爬虫):

```bash
python -m scripts.scrape_sample <公开页面URL> --jurisdiction US --category regulation --keywords 遗产税,estate
```

> ⚠️ 全量 carrier/监管数据抓取 + 版权/ToS/法务 review 属本仓库之外的工作,不在 V0.1 范围。
> 使用样例脚本请遵守目标站点 robots.txt 与频率限制。

## 外部对接 TODO(纯软件已就绪,待接真实资源)

- **真实 broker 网络**:当前用 `app/data/brokers_mock.json` 跑通匹配/handoff 软件闭环
- **全量知识爬虫 + 法务**:见上,当前为种子库 + 单页样例
- **React Native 移植**:当前 Web 端;移动端需 Apple/Google 开发者账号
- **云部署**:当前文件持久化;生产需 AWS/Qdrant/Postgres
- **Stripe 真实计费**:Premium 当前为 gating 占位

## 范围说明 (V0.1 不做)

不做账号体系(匿名 session)、大陆合规、账户连接(Plaid)、HNW bespoke 结构化产品。详见 PRD §0 Non-goals。
