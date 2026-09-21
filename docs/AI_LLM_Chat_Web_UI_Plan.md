# PLAN — AI LLM Chat Web UI

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

```text
Phase 0
Requirement
      ↓
Phase 1
UI/UX
      ↓
Phase 2
Frontend
      ↓
Phase 3
Backend
      ↓
Phase 4
LLM Gateway
      ↓
Phase 5
Streaming
      ↓
Phase 6
Conversation + DB
      ↓
──── MVP ────
      ↓
Phase 7
File + RAG
      ↓
Phase 8
Tool Calling
      ↓
Phase 9
Agent
      ↓
Phase 10
Memory
      ↓
Phase 11
Safety
      ↓
Phase 12
Evaluation
      ↓
Phase 13
Deployment
```

---

# 25. Cấu trúc Repository

```text
ai-chat-platform/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── hooks/
│   ├── services/
│   ├── stores/
│   ├── types/
│   └── utils/
│
├── backend/
│   ├── api/
│   ├── services/
│   │   ├── chat/
│   │   ├── conversation/
│   │   ├── file/
│   │   └── agent/
│   │
│   ├── llm/
│   │   ├── base.py
│   │   ├── openai.py
│   │   ├── gemini.py
│   │   ├── claude.py
│   │   └── local.py
│   │
│   ├── tools/
│   ├── memory/
│   ├── rag/
│   ├── models/
│   └── database/
│
├── evaluation/
│
├── tests/
│
├── docker/
│
├── docs/
│
├── .env.example
├── docker-compose.yml
└── README.md
```

---

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
