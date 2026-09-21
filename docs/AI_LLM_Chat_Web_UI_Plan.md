# PLAN — AI LLM Chat Web UI

> **Bối cảnh — đọc trước mọi mục khác.** Tài liệu này được viết như một kế hoạch
> dựng nền tảng chat đa dụng từ số không. Nhưng nó đang được áp vào **hệ thống
> sinh thơ thất ngôn hiện có**, nơi backend, LLM gateway, streaming, RAG, tool
> calling, agent, memory, safety và observability **đã có sẵn và đã có test**.
>
> Vì vậy phạm vi thật của việc cần làm là: **một frontend, nói chuyện với backend
> đang có.** Các Phase 3/4/6/7/8/9/10/11 của tài liệu này không phải việc cần xây
> mới — chúng là mô tả những gì đã chạy. Xem §25 (cấu trúc repo) và §30.
>
> Điều tài liệu gốc KHÔNG lường tới, và là phần khó nhất của giao diện này: bài
> thơ **có thể không được trả về**. Hệ thống kiểm tra luật trước khi trả, và có ba
> trạng thái không tồn tại trong một chat box thường — *hỏi lại*, *không đạt*,
> *chờ người duyệt*. §30 dành cho ba trạng thái đó.

## 1. Mục tiêu dự án

Xây dựng một Web UI cho phép người dùng:

- Chat trực tiếp với LLM.
- Tạo và quản lý nhiều conversation.
- Streaming câu trả lời theo thời gian thực.
- Hiển thị Markdown, Code Block, Table, LaTeX.
- Regenerate / Stop generation.
- Edit và resend message.
- Chọn model.
- Upload file làm context.
- Theo dõi trạng thái LLM.
- Hỗ trợ Tool Calling / Agent ở giai đoạn mở rộng.
- Lưu lịch sử hội thoại.
- Có khả năng mở rộng từ một LLM thành Multi-Model / Agent Chat Platform.

---

# 2. Kiến trúc tổng thể

```text
                         USER
                           │
                           ▼
                ┌────────────────────┐
                │      WEB UI        │
                │ React / Next.js    │
                └─────────┬──────────┘
                          │
                     HTTP / SSE
                          │
                          ▼
                ┌────────────────────┐
                │    API SERVER      │
                │ FastAPI / Node.js  │
                └─────────┬──────────┘
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
   ┌────────────┐  ┌────────────┐  ┌──────────────┐
   │ Chat       │  │ Conversation│  │ File Service │
   │ Service    │  │ Service     │  │              │
   └─────┬──────┘  └─────┬──────┘  └──────┬───────┘
         │               │                │
         └───────────────┼────────────────┘
                         ▼
                 ┌──────────────┐
                 │ Agent / LLM  │
                 │ Orchestrator │
                 └──────┬───────┘
                        │
             ┌──────────┼──────────┐
             ▼          ▼          ▼
          LLM API    RAG       Tools
             │
             ▼
       GPT / Gemini /
       Claude / Local LLM
```

---

# 3. Chia dự án thành các Layer

Đề xuất chia thành 7 layer:

```text
Layer 1 — UI
Layer 2 — Chat State
Layer 3 — API
Layer 4 — LLM Gateway
Layer 5 — Agent / Tool Calling
Layer 6 — Memory / RAG
Layer 7 — Observability
```

Không nên xây Agent/RAG ngay từ đầu.

Thứ tự nên là:

```text
Basic Chat
   ↓
Streaming
   ↓
Conversation
   ↓
Multi-model
   ↓
File Upload
   ↓
Tool Calling
   ↓
Agent
   ↓
RAG
   ↓
Evaluation
   ↓
Production
```

---

# 4. Phase 0 — Requirement & UX Design

## 4.1. Xác định User Flow

### Flow cơ bản

```text
Open Website
      ↓
New Chat
      ↓
Enter Prompt
      ↓
Send
      ↓
Backend
      ↓
LLM
      ↓
Streaming Response
      ↓
Render Response
      ↓
Save Conversation
```

### User Flow nâng cao

```text
User
 │
 ├── New Chat
 │
 ├── Select Model
 │
 ├── Upload File
 │
 ├── Send Prompt
 │
 ├── Stop Generation
 │
 ├── Regenerate
 │
 ├── Edit Message
 │
 ├── Copy Response
 │
 └── Continue Conversation
```

---

# 5. Phase 1 — Thiết kế Web UI

## Layout chính

Đề xuất UI dạng:

```text
┌──────────────────────────────────────────────────────────┐
│                       Header                             │
│  Logo       Model: Gemma ▼                  Settings ⚙  │
├──────────────┬───────────────────────────────────────────┤
│              │                                           │
│ Conversation │                                           │
│              │             Chat Area                     │
│ + New Chat   │                                           │
│              │   User                                     │
│ Chat 001     │   ┌─────────────────────────────┐        │
│ Chat 002     │   │ Hello                       │        │
│ Chat 003     │   └─────────────────────────────┘        │
│              │                                           │
│              │   Assistant                               │
│              │   ┌─────────────────────────────┐        │
│              │   │ Hello! How can I help you?  │        │
│              │   └─────────────────────────────┘        │
│              │                                           │
│              ├───────────────────────────────────────────┤
│              │ 📎  Ask anything...             Send ➤    │
└──────────────┴───────────────────────────────────────────┘
```

---

# 6. Các UI Component

## A. Sidebar

Chức năng:

```text
+ New Chat

Search conversations

Recent
 ├── AI Agent Project
 ├── Poetry Agent
 ├── Computer Vision
 └── Data Quality

Folders
 ├── Research
 ├── Coding
 └── Personal

Settings
```

## B. Header

```text
[Logo]

Model:
[Gemma-4-26B ▼]

[Context: 32K]

[Settings]
```

Nếu Multi-model:

```text
Model
├── GPT
├── Claude
├── Gemini
├── Gemma
└── Local LLM
```

---

# 7. Chat Message Component

Mỗi message nên có structure:

```text
Message
│
├── Role
│   ├── User
│   └── Assistant
│
├── Content
│
├── Timestamp
│
└── Actions
    ├── Copy
    ├── Edit
    ├── Regenerate
    └── Feedback
```

Ví dụ:

```text
USER
────────────────────
Thiết kế một AI Agent cho tôi


ASSISTANT
────────────────────
Được. Chúng ta có thể thiết kế Agent
theo kiến trúc...

[Copy] [Regenerate] [👍] [👎]
```

---

# 8. Message Rendering

LLM không chỉ trả text.

Cần hỗ trợ:

## Markdown

```markdown
# Title

**Bold**

- Item 1
- Item 2
```

## Code

```python
def hello():
    print("Hello")
```

UI:

```text
┌──────────────────────────────────┐
│ Python                     Copy │
├──────────────────────────────────┤
│ def hello():                    │
│     print("Hello")              │
└──────────────────────────────────┘
```

## Table

```text
| Model | Context |
|-------|---------|
| GPT   | ...     |
| Gemma | ...     |
```

## LaTeX

```text
E = mc²
```

## Streaming

```text
Hello
Hello, I
Hello, I can
Hello, I can help
...
```

---

# 9. Chat Input

Input nên có:

```text
┌──────────────────────────────────────────────┐
│ Ask anything...                              │
│                                              │
│                                              │
│ 📎 Attach       / Tools       Model      ➤  │
└──────────────────────────────────────────────┘
```

### Keyboard

```text
Enter
→ Send

Shift + Enter
→ New line

Ctrl + Enter
→ Send (optional)
```

---

# 10. Phase 2 — Frontend Architecture

Nếu làm dự án AI nghiêm túc, đề xuất:

```text
Frontend
│
├── app/
│
├── components/
│   ├── chat/
│   │   ├── ChatWindow
│   │   ├── ChatMessage
│   │   ├── ChatInput
│   │   └── MessageActions
│   │
│   ├── sidebar/
│   │   ├── Sidebar
│   │   ├── ConversationList
│   │   └── ConversationItem
│   │
│   ├── model/
│   │   └── ModelSelector
│   │
│   └── common/
│
├── hooks/
│   ├── useChat
│   ├── useStreaming
│   └── useConversation
│
├── services/
│   ├── chatApi
│   ├── conversationApi
│   └── fileApi
│
├── stores/
│   └── chatStore
│
├── types/
│
└── utils/
```

### Stack đề xuất

```text
Next.js
React
TypeScript
Tailwind CSS
shadcn/ui
Zustand
```

---

# 11. Phase 3 — Backend

Backend chịu trách nhiệm:

```text
Frontend
    │
    ▼
POST /api/chat
    │
    ▼
Chat Service
    │
    ├── Validate request
    ├── Load conversation
    ├── Build messages
    ├── Select model
    ├── Call LLM
    ├── Stream tokens
    └── Save response
```

API cơ bản:

```text
POST   /api/chat
GET    /api/conversations
POST   /api/conversations
GET    /api/conversations/{id}
DELETE /api/conversations/{id}

POST   /api/files
GET    /api/models
```

---

# 12. Chat API Design

## Request

```json
{
  "conversation_id": "conv_001",
  "model": "gemma-4-26b",
  "message": "Hello AI",
  "stream": true
}
```

## Response streaming

```text
data: {"type":"start"}

data: {"type":"token","content":"Hello"}

data: {"type":"token","content":"!"}

data: {"type":"token","content":" How"}

data: {"type":"token","content":" can"}

data: {"type":"token","content":" I help?"}

data: {"type":"done"}
```

---

# 13. SSE hay WebSocket?

Đối với Chat LLM:

### MVP

```text
SSE
```

là đủ.

Architecture:

```text
Browser
   │
   │ SSE
   ▼
FastAPI
   │
   ▼
LLM
```

WebSocket chỉ nên cân nhắc khi cần:

- Realtime collaboration.
- Voice.
- Realtime agent state.
- Multi-user interaction.
- Bidirectional streaming phức tạp.

---

# 14. Phase 4 — LLM Gateway

Không nên để API server gọi trực tiếp từng model ở mọi nơi.

Tạo:

```text
LLM Gateway
```

Ví dụ:

```text
LLM Gateway
│
├── OpenAI Adapter
├── Gemini Adapter
├── Claude Adapter
├── Ollama Adapter
└── vLLM Adapter
```

Interface thống nhất:

```text
generate()
stream()
count_tokens()
get_model_info()
```

Khi đó UI chỉ cần:

```text
model = "gemma-4-26b"
```

Backend tự biết phải gọi provider nào.

---

# 15. Phase 5 — Conversation Management

Database:

```text
User
 │
 └── Conversations
       │
       ├── Conversation
       │      ├── Message
       │      ├── Message
       │      └── Message
       │
       └── Conversation
```

## conversations

```text
conversations
----------------
id
user_id
title
model
created_at
updated_at
```

## messages

```text
messages
----------------
id
conversation_id
role
content
token_count
created_at
```

---

# 16. Phase 6 — Context Management

Đây là phần rất quan trọng đối với LLM Chat.

Không nên:

```text
Conversation 500 messages
        ↓
Gửi toàn bộ cho LLM
```

Thay vào đó:

```text
Conversation
      │
      ├── System Prompt
      │
      ├── Summary
      │
      ├── Recent Messages
      │
      └── Relevant Context
             ↓
         LLM Context
```

Ví dụ:

```text
System Prompt
+
Conversation Summary
+
Last 10 messages
+
Relevant retrieved messages
+
Current user message
```

---

# 17. Phase 7 — File Upload

Cho phép:

```text
PDF
TXT
DOCX
CSV
JSON
MD
```

Flow:

```text
Upload
  ↓
File Parser
  ↓
Chunking
  ↓
Embedding
  ↓
Vector DB
  ↓
Retriever
  ↓
LLM
```

Sau này có thể biến Chat UI thành:

> Chat with your documents

---

# 18. Phase 8 — Tool Calling

Khi Chat cơ bản ổn định mới thêm Tool.

Architecture:

```text
User
 ↓
LLM
 ↓
Need Tool?
 ├── NO → Final Answer
 │
 └── YES
       ↓
    Tool Call
       ↓
    Tool Execute
       ↓
    Tool Result
       ↓
    LLM
       ↓
 Final Response
```

Ví dụ:

```text
User:
"Tìm thời tiết Hà Nội"

LLM
 ↓
weather_tool()

Tool
 ↓
24°C, cloudy

LLM
 ↓
"Hà Nội hiện tại..."
```

---

# 19. Phase 9 — Agent Layer

Sau Tool Calling mới xây Agent.

```text
                    Agent
                      │
              ┌───────┴───────┐
              ▼               ▼
           Planner          Memory
              │
              ▼
           Tool Router
              │
      ┌───────┼────────┐
      ▼       ▼        ▼
   Search    Code     RAG
      │       │        │
      └───────┼────────┘
              ▼
          Final Answer
```

UI cần hiển thị Agent state:

```text
Assistant

Thinking...
✓ Search documents
✓ Analyze data
⟳ Generate answer
```

Không nhất thiết phải expose toàn bộ internal reasoning; chỉ hiển thị tool/status events cần thiết cho UX.

---

# 20. Phase 10 — Safety

AI Chat UI cần có:

```text
Input
 ↓
Input Validation
 ↓
Prompt Injection Detection
 ↓
LLM
 ↓
Output Validation
 ↓
PII Detection
 ↓
Response
```

Các vấn đề cần test:

```text
Prompt Injection
Jailbreak
PII Leakage
Unsafe Tool Call
Malicious File
Data Exfiltration
Context Injection
```

---

# 21. Phase 11 — Observability

Không chỉ log backend.

Cần track:

```text
Request
│
├── Model
├── Latency
├── TTFT
├── Input tokens
├── Output tokens
├── Total tokens
├── Cost
├── Tool calls
├── Errors
└── User feedback
```

Các metric quan trọng:

### TTFT

```text
Time To First Token
```

### Generation Latency

```text
Request → Final Token
```

### Token Throughput

```text
tokens / second
```

### Error Rate

```text
failed_requests / total_requests
```

---

# 22. Phase 12 — Testing

## Frontend

```text
Component Test
Integration Test
E2E Test
```

## Backend

```text
Unit Test
API Test
Streaming Test
LLM Gateway Test
```

## AI

```text
Prompt Test
Hallucination Test
Tool Calling Test
RAG Test
Safety Test
```

---

# 23. Phase 13 — MVP Scope

Đừng làm tất cả ngay.

MVP nên chỉ gồm:

```text
┌─────────────────────────────┐
│           MVP               │
├─────────────────────────────┤
│                             │
│ ✓ Chat UI                   │
│ ✓ New Chat                  │
│ ✓ Conversation History      │
│ ✓ Markdown                  │
│ ✓ Code Highlight            │
│ ✓ Streaming                 │
│ ✓ Stop Generation           │
│ ✓ Regenerate                │
│ ✓ Copy                      │
│ ✓ Model Selection           │
│ ✓ Backend API               │
│ ✓ Database                  │
│                             │
└─────────────────────────────┘
```

Chưa cần:

```text
✗ RAG
✗ Agent
✗ Tool Calling
✗ Multi-agent
✗ Voice
✗ Complex Memory
```

---

# 24. Roadmap đề xuất

**Safety KHÔNG nằm ở Phase 11.** Tài liệu gốc xếp Safety sau Agent và Memory, tức
là hệ thống sẽ phát chữ ra cho người dùng suốt mười phase trước khi có rào chắn
đầu ra nào. Với một hệ thống sinh thơ thì còn nặng hơn: thứ được kiểm không chỉ là
an toàn nội dung mà là **luật thơ** — và nếu kiểm luật chỉ được nối vào ở cuối,
thì trong suốt thời gian trước đó giao diện đã trả về thơ SAI LUẬT như thể đúng.

Một rào chắn nối sau còn khó hơn nối từ đầu: lúc đó streaming đã phát thẳng từng
mẩu ra SSE, và chèn kiểm duyệt vào giữa buộc phải đổi lại giao diện phía client.
Chính lỗi đó đã xảy ra trong repo này — `stream=true` từng đi vòng qua toàn bộ
output rails, tức là *bật stream là tắt rào chắn* — xem chú thích trong
`src/entrypoints/api/routers/chat.py`.

Thứ tự đã sửa:

```text
Phase 0  Requirement
      ↓
Phase 1  UI/UX
      ↓
Phase 2  Frontend
      ↓
Phase 3  Backend
      ↓
Phase 4  LLM Gateway
      ↓
Phase 5  Streaming ─┬─ Phase 5b  SAFETY + KIỂM LUẬT   ← đi CÙNG streaming
                    │  (rào chắn đầu vào/đầu ra, kiểm
                    │   luật thơ, ba trạng thái §30)
      ↓─────────────┘
Phase 6  Conversation + DB
      ↓
──── MVP ────
      ↓
Phase 7  File + RAG
      ↓
Phase 8  Tool Calling
      ↓
Phase 9  Agent
      ↓
Phase 10 Memory
      ↓
Phase 11 Evaluation
      ↓
Phase 12 Deployment
```

Nguyên tắc: **không có đường nào phát chữ ra người dùng mà không đi qua rào chắn.**
Thêm một đường phát mới (stream, tool output, agent trace) là thêm một chỗ phải nối
rào — không phải một việc để lại sau.

---

# 25. Cấu trúc Repository

**Không tạo repo mới, không tạo thư mục `backend/`.** Backend là repo hiện tại.
Dựng lại `backend/api/`, `backend/llm/`, `backend/rag/`, `backend/memory/`,
`backend/database/` như cây thư mục gốc của tài liệu này đề xuất nghĩa là viết lại
lần thứ hai những thứ đã có và đã qua kiểm thử — và bản thứ hai sẽ lệch dần khỏi
bản thứ nhất, vì chỉ một trong hai được chạy thật.

Đối chiếu cây thư mục gốc với thứ đã tồn tại:

| Tài liệu đề xuất | Đã có trong repo này |
|---|---|
| `backend/api/` | `src/entrypoints/api/` |
| `backend/llm/{openai,claude,gemini}.py` | `src/adapters/llm/` + `configs/models.yaml` |
| `backend/services/chat/` | `src/application/` |
| `backend/services/conversation/` | `src/entrypoints/api/routers/conversations.py` |
| `backend/rag/` | `src/adapters/retrieval/` |
| `backend/memory/` | `src/adapters/persistence/` |
| `backend/tools/` | `src/application/tools/` |
| `backend/database/` | `src/adapters/persistence/sql/` + `migrations/` |
| `evaluation/` | `evals/` |

Phần THẬT SỰ cần thêm chỉ là một thư mục:

```text
frontend/
├── app/            # route, layout
├── components/     # Sidebar, Header, MessageList, ChatInput, …
├── hooks/          # useChat, useStream, useConversations
├── services/       # gọi API backend — nơi DUY NHẤT biết URL backend
├── stores/         # trạng thái hội thoại phía client
├── types/          # sinh từ /openapi.json, không chép tay
└── utils/
```

`types/` sinh từ `GET /openapi.json` của backend, **không gõ tay**. Gõ tay thì mỗi
lần backend đổi hợp đồng, frontend vẫn biên dịch xanh rồi hỏng lúc chạy.

# 26. Kiến trúc cuối cùng

Mục tiêu dài hạn:

```text
                         AI CHAT PLATFORM
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
          Chat UI            Agent UI           File UI
             │                  │                  │
             └──────────────────┼──────────────────┘
                                ▼
                         Chat Orchestrator
                                │
                 ┌──────────────┼──────────────┐
                 ▼              ▼              ▼
              Memory           RAG            Tools
                 │              │              │
                 └──────────────┼──────────────┘
                                ▼
                           LLM Gateway
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
           Cloud LLM        Local LLM         Custom Model
```

---

# 27. Nguyên tắc kiến trúc quan trọng

## 27.1. UI không nên phụ thuộc trực tiếp vào LLM

UI chỉ nên biết các thao tác:

```text
sendMessage()
streamMessage()
stopGeneration()
regenerate()
```

Backend/LLM Gateway chịu trách nhiệm:

```text
Prompt
→ Context
→ Model
→ Tool
→ Agent
→ Streaming
→ Response
```

## 27.2. Tách LLM Provider khỏi Web UI

Có thể thay đổi:

```text
Gemma
  ↓
GPT
  ↓
Claude
  ↓
Gemini
  ↓
Ollama / vLLM
```

mà không phải viết lại Web UI.

## 27.3. Xây từ đơn giản đến phức tạp

Ưu tiên:

```text
MVP Chat
    ↓
Streaming
    ↓
Conversation
    ↓
Multi-model
    ↓
RAG
    ↓
Tool Calling
    ↓
Agent
    ↓
Evaluation
    ↓
Production
```

---

# 28. Definition of Done cho MVP

MVP được xem là hoàn thành khi:

- [ ] Người dùng mở được Web UI.
- [ ] Có thể tạo conversation mới.
- [ ] Có thể gửi message.
- [ ] LLM trả lời bằng streaming.
- [ ] Có thể stop generation.
- [ ] Có thể regenerate response.
- [ ] Có thể copy response.
- [ ] Markdown render chính xác.
- [ ] Code block có syntax highlighting.
- [ ] Conversation được lưu vào database.
- [ ] Có thể mở lại conversation cũ.
- [ ] Có thể chọn model.
- [ ] Backend không phụ thuộc cứng vào một provider.
- [ ] Có error handling cơ bản.
- [ ] Có logging.
- [ ] Có test cho các flow chính.
- [ ] Có Docker setup cho local deployment.

Ba mục dưới đây **không có trong bản gốc** và không được bỏ. Chúng không phải
"tính năng nâng cao" — thiếu chúng thì MVP không đưa ra ngoài máy cá nhân được:

- [ ] **Xác thực.** Mọi đường đều theo tenant của khoá API, `user_id`/`tenant_id`
      **không bao giờ** lấy từ thân request. §15 của tài liệu này có cột `user_id`
      nhưng không mục nào nói ai xác minh nó; một `user_id` do client tự khai thì
      mọi cô lập ở tầng dưới đều vô nghĩa. Ghim bằng test: hội thoại của tenant A
      trả 404 cho tenant B — không phải 403, vì 403 xác nhận id đó có thật.
- [ ] **Trần ngân sách theo tenant.** Một vòng lặp regenerate để chạy qua đêm là đủ
      để tạo hoá đơn không giới hạn. Sinh thơ ở đây là **best-of-16 mỗi khổ**, nên
      một yêu cầu 12 dòng tốn gấp hàng chục lần một lượt chat thường — trần ngân
      sách ở đây không phải đề phòng lạm dụng, nó là chi phí vận hành bình thường.
- [ ] **Trần dung lượng file upload.** §17 mô tả upload file nhưng không nêu giới
      hạn nào. Không có trần thì một file duy nhất làm hết đĩa, và phần trích xuất
      văn bản là nơi nhận dữ liệu do người ngoài kiểm soát — cần trần cả **dung
      lượng, số trang, và thời gian xử lý**, vì một file nhỏ vẫn có thể là bom nén.

---

# 29. Kết luận

Kiến trúc nên được phát triển theo tư duy:

```text
                AI CHAT PLATFORM

                    Web UI
                      ↓
                 Chat State
                      ↓
                  API Layer
                      ↓
                LLM Gateway
                      ↓
          ┌───────────┼───────────┐
          ↓           ↓           ↓
        Memory       RAG        Tools
          │           │           │
          └───────────┼───────────┘
                      ↓
                    Agent
                      ↓
                    LLM
```

Mục tiêu cuối cùng không chỉ là xây một "chat box", mà là xây một **AI Chat Platform có khả năng mở rộng** từ:

```text
Single LLM Chat
       ↓
Multi-Model Chat
       ↓
Chat with Files
       ↓
Tool Calling
       ↓
AI Agent
       ↓
RAG + Memory
       ↓
Evaluation + Safety
       ↓
Production AI Platform
```

Nguyên tắc cốt lõi:

> **Build the Chat UI first, decouple the LLM layer, then progressively add RAG, Tools, Agents, Memory, Evaluation and Safety.**

---

# 30. Ba trạng thái đặc thù của hệ sinh thơ

Một chat box thường có hai trạng thái: *đang trả lời* và *đã trả lời*. Hệ thống này
có ba trạng thái nữa, và tất cả đều **trước** khi người dùng thấy bài thơ. Nếu
giao diện không dựng sẵn chỗ cho chúng, mỗi trạng thái sẽ hiện ra như một lỗi đỏ —
trong khi cả ba đều là hệ thống đang làm đúng việc của nó.

## 30.1. *Hỏi lại* — chưa đủ thông tin

Hệ thống **không đoán** khi thiếu thông tin: thiếu chủ đề, thiếu số dòng, hoặc số
dòng không phải bội của 4 thì nó hỏi lại thay vì tự chọn hộ.

- Backend trả về **danh sách câu hỏi**, không phải một chuỗi lỗi.
- UI dựng một khối hỏi lại ngay trong luồng chat, có nút gợi ý sẵn cho các lựa
  chọn thường gặp (8 dòng · 12 dòng · 16 dòng), và vẫn cho gõ tự do.
- Trả lời xong thì **tiếp tục yêu cầu cũ**, không bắt người dùng gõ lại từ đầu.

Đừng hiển thị cái này như lỗi. Người dùng không làm sai gì cả.

## 30.2. *Không đạt* — bài thơ trượt kiểm luật

Đây là trạng thái quan trọng nhất và cũng dễ làm sai nhất. Khi kiểm luật không qua,
**hệ thống không trả bài thơ ra**. Cám dỗ lớn nhất khi dựng UI là "cứ hiện ra kèm
cảnh báo" — làm vậy là phá bỏ toàn bộ lý do kiểm luật tồn tại: người dùng sẽ chép
bài thơ sai luật đi dùng, và dòng cảnh báo không đi theo.

Hai cờ phải hiện **tách nhau**, vì chúng khác hẳn nhau về hệ quả:

| Cờ | Nghĩa | Khi trượt |
|---|---|---|
| `dat_luat` | Đúng luật thất ngôn (thanh, vần, niêm, đối) | **Không trả bài.** Đây là ràng buộc cứng. |
| `dat_chat_luong` | Đạt chuẩn chất lượng của dự án | Vẫn trả bài, kèm ghi chú. Đây là thang đo, không phải luật. |

UI cần:

- Nêu **trượt ở tầng nào** (tầng 1–7) và **dòng nào, tiếng thứ mấy** — báo "không
  đạt" trống rỗng thì người dùng không biết phải yêu cầu lại thế nào.
- Nút **thử lại**, ghi rõ rằng mỗi lần thử là một lượt sinh mới (xem trần ngân
  sách, §28).
- **Đừng** đếm ngược hay hứa thời gian. Sinh thơ ở đây là best-of-16 mỗi khổ và
  chạy lâu hơn hẳn một lượt chat thường — đó là điều đã được chọn có chủ ý, đổi
  thời gian lấy đúng luật. Nói thẳng điều đó với người dùng thay vì giấu nó sau
  một thanh tiến trình giả.

## 30.3. *Chờ người duyệt* — HITL

Khi phân loại chủ đề cho kết quả `REVIEW`, yêu cầu **vẫn được xử lý** nhưng bị đánh
dấu để người thật xem lại. Chặn ngay ở đây là biến bộ lọc thành bộ kiểm duyệt.

UI cần một trạng thái thứ ba, **không phải lỗi và cũng không phải xong**: đã nhận,
đang chờ duyệt, và người dùng đóng tab rồi quay lại vẫn thấy được. Nghĩa là trạng
thái này phải nằm trong cơ sở dữ liệu của hội thoại, không phải trong bộ nhớ trình
duyệt.

## 30.4. Streaming và ba trạng thái này

Cả ba trạng thái đều **mâu thuẫn với streaming từng chữ**. Không thể phát dần một
bài thơ rồi mới phát hiện nó sai luật — chữ đã ra rồi.

Với luồng sinh thơ, streaming nên dừng ở mức **tiến trình**, không phải nội dung:

```text
  ✓ Đã hiểu yêu cầu (12 dòng · chủ đề: mùa thu)
  ✓ Khổ 1/3 — đạt luật (chọn từ 16 bản)
  ⟳ Khổ 2/3 — đang sinh…
    Khổ 3/3
```

Người dùng thấy hệ thống đang chạy, nhưng không thấy chữ nào cho tới khi cả bài
qua kiểm. Với luồng chat thường thì giữ nguyên streaming từng chữ như §8.

