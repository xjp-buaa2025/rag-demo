# 学习路线图：FastAPI + React + LangChain

> **目标**：将当前 `app.py`（Gradio 单文件）逐步重构为 FastAPI 后端 + React 前端 + LangChain 智能体的生产级架构。
> **起点**：刚入门，每天学一点，边学边改造本项目。

---

## 整体架构目标

```
┌─────────────────────────────────────────────┐
│               React 前端 (Vite)              │
│  知识库管理页 │ RAG问答页 │ BOM装配页         │
└──────────────────┬──────────────────────────┘
                   │ HTTP / SSE (流式)
┌──────────────────▼──────────────────────────┐
│              FastAPI 后端                    │
│  /api/ingest  /api/chat  /api/bom  /api/eval │
│  ↕ ChromaDB    ↕ Neo4j    ↕ LangChain Agent  │
└─────────────────────────────────────────────┘
```

---

## 第一阶段：FastAPI 后端（第 1-2 周）

> **为什么先学 FastAPI**：它是 Python 的，跟你现有代码语言一致，改造成本最低。先把 `app.py` 里的逻辑搬到 FastAPI，再学前端会顺很多。

### Week 1：FastAPI 核心

| 天 | 主题 | 对应本项目的落地点 |
|----|------|--------------------|
| Day 1 | 路由、请求体、响应体（`@app.get/post`、`BaseModel`） | 把 `retrieve()` 函数包成 `/api/search` 接口 |
| Day 2 | 异步（`async def`）、依赖注入（`Depends`） | ChromaDB / Neo4j 连接池用 `Depends` 管理 |
| Day 3 | **SSE 流式响应**（`StreamingResponse` + `EventSourceResponse`） | 把 LLM stream 输出改成 SSE，替代 Gradio yield |
| Day 4 | 文件上传（`UploadFile`） | BOM Excel 上传接口 `/api/bom/ingest` |
| Day 5 | 错误处理（`HTTPException`）、后台任务（`BackgroundTasks`） | 入库操作改为后台任务，接口立即返回 task_id |

**必读资源**：
- 官方文档 Tutorial（跟着敲一遍）：https://fastapi.tiangolo.com/tutorial/
- 中文版（同步官方）：https://fastapi.tiangolo.com/zh/tutorial/

**本周产出**：新建 `backend/main.py`，包含以下接口：
```
POST /api/ingest          文档入库
POST /api/chat            RAG 问答（SSE 流式）
POST /api/bom/ingest      BOM 入库
POST /api/bom/chat        装配问答（SSE 流式）
GET  /api/status          系统状态（ChromaDB 条数、Neo4j 状态）
```

### Week 2：FastAPI 工程化

| 天 | 主题 |
|----|------|
| Day 6 | 项目结构拆分：`routers/`、`services/`、`schemas/` |
| Day 7 | CORS 配置（允许 React 跨域调用） |
| Day 8 | `lifespan` 事件（替代全局初始化代码，管理 ChromaDB/Neo4j 连接） |
| Day 9 | 用 `pydantic-settings` 管理 `.env` 配置 |
| Day 10 | 用 `pytest` + `httpx` 写接口测试 |

**本周产出**：后端结构清晰，`.env` 配置化，所有接口可用 Swagger UI（`/docs`）直接测试。

---

## 第二阶段：React 前端（第 3-4 周）

> **为什么用 React + Vite**：比 Gradio 灵活 100 倍，组件化开发，UI 随便定制。Vite 是目前最快的 React 开发工具链。

### Week 3：React 核心

| 天 | 主题 | 对应本项目 |
|----|------|-----------|
| Day 1 | JSX、组件、Props、useState | 做一个最简单的"问答输入框 + 答案显示"组件 |
| Day 2 | useEffect、fetch 调用后端 API | 调用 `/api/status` 显示知识库状态 |
| Day 3 | **SSE 消费**（`EventSource` API） | 接收 LLM 流式输出，打字机效果 |
| Day 4 | 列表渲染、条件渲染、表单受控组件 | 历史对话列表、文件上传表单 |
| Day 5 | React Router（多页面路由） | RAG问答页 / BOM装配页 / 知识库管理页 分离 |

**工具链**：
```bash
npm create vite@latest frontend -- --template react
cd frontend && npm install
npm run dev   # 启动开发服务器 http://localhost:5173
```

**推荐 UI 组件库**（选一个，别纠结）：
- **Ant Design**：中文文档完善，企业级，https://ant.design/
- **shadcn/ui**：现代简洁，Copy-paste 风格，适合定制

### Week 4：React 工程化 + 与 FastAPI 联调

| 天 | 主题 |
|----|------|
| Day 6 | Axios 封装（统一 baseURL、错误拦截） |
| Day 7 | 全局状态管理（`Context` 或 `Zustand`） |
| Day 8 | 流式聊天组件完整实现（含"停止生成"按钮） |
| Day 9 | 文件拖拽上传组件 + 进度条 |
| Day 10 | Vite proxy 配置，开发环境无跨域联调 FastAPI |

**本周产出**：完整替换 Gradio，React 前端 + FastAPI 后端完整跑通。

---

## 第三阶段：LangChain 智能体（第 5-6 周）

> **为什么现在才学 LangChain**：LangChain 的价值在于编排复杂的多步骤 Agent，等你有了 FastAPI 后端基础，把 LangChain 作为一个 service 集成进来会非常自然。

### Week 5：LangChain 核心概念

| 天 | 主题 | 对应本项目 |
|----|------|-----------|
| Day 1 | LCEL（LangChain Expression Language）：`chain = prompt \| llm \| parser` | 重写当前 `assembly_chat()` 的 prompt 拼接逻辑 |
| Day 2 | `ChatPromptTemplate`、`MessagesPlaceholder`（对话历史） | 给 RAG 问答加多轮对话记忆 |
| Day 3 | `RunnableWithMessageHistory`（会话记忆管理） | 每个用户 session 独立记忆 |
| Day 4 | Tool 定义（`@tool` 装饰器） | 把 `_query_bom_text()`、`retrieve()` 包成 Tool |
| Day 5 | ReAct Agent（`create_react_agent`） | 让 Agent 自己决定何时查 BOM、何时查知识库 |

### Week 6：LangChain 进阶

| 天 | 主题 |
|----|------|
| Day 6 | LangChain Retriever 接口（把 ChromaDB 接入标准 Retriever） |
| Day 7 | `ConversationalRetrievalChain` → 完整 RAG 对话链 |
| Day 8 | Agent 流式输出（`astream_events`）→ 接入 FastAPI SSE |
| Day 9 | LangSmith 接入（可选，Agent 调试利器） |
| Day 10 | 为 Isaac Sim 集成预留 Tool 接口 |

---

## 项目改造路径（渐进式，不破坏现有功能）

```
当前状态                    改造步骤                      目标状态
app.py (Gradio)    →    Step 1: 新建 backend/          FastAPI 后端
                              把业务逻辑搬过来
                   →    Step 2: 新建 frontend/          React 前端
                              Gradio 保留作备用
                   →    Step 3: 用 LangChain            LangChain Agent
                              重写 assembly_chat()
                   →    Step 4: 删除 app.py             生产级架构
```

**每步可独立验证，随时可以回退。**

---

## 推荐学习资源

### FastAPI
- 官方文档（最权威）：https://fastapi.tiangolo.com/zh/
- B站视频：搜索"FastAPI 教程"，选播放量高的

### React
- React 官方新文档（hooks 时代）：https://react.dev/learn
- B站：搜索"React 18 入门"

### LangChain
- 官方文档：https://python.langchain.com/docs/introduction/
- LangChain 中文文档：https://python.langchain.com.cn/

### 综合实战（强烈推荐）
- **Full Stack FastAPI + React 模板**：https://github.com/fastapi/full-stack-fastapi-template
  直接 clone 下来看项目结构，比任何教程都直观

---

## 每日学习节奏建议

```
30 min  读文档 / 看视频（理论）
60 min  在本项目里写代码实践（最重要）
15 min  记录遇到的问题和解决方法
```

**原则**：每天学完立刻在 rag-demo 里找一个对应点实践，不要学完一整章再动手。

---

## 本阶段不需要学的（避免分心）

- TypeScript（先用 JS，稳定后再迁移）
- Redux（Zustand 够用了）
- Docker/K8s（项目稳定后再考虑）
- LangGraph（LangChain 熟了再进阶）
