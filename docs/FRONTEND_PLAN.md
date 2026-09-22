# FRONTEND PLAN — AI LLM CHAT WEB UI

## Professional · Soft Pink · Friendly · Cute Micro-interactions

---

## Mục lục

1. [Frontend Vision](#1-frontend-vision)
2. [Design Goals](#2-design-goals)
3. [Design Language](#3-design-language)
4. [Color System](#4-color-system)
5. [Pink Usage Rule](#5-pink-usage-rule)
6. [Dark Mode](#6-dark-mode)
7. [Typography](#7-typography)
8. [Main Layout](#8-main-layout)
9. [Component Architecture](#9-component-architecture)
10. [Header](#10-header)
11. [Sidebar](#11-sidebar)
12. [New Chat Button](#12-new-chat-button)
13. [Welcome Screen](#13-welcome-screen)
14. [Message Design](#14-message-design)
15. [Assistant Avatar](#15-assistant-avatar)
16. [AI Thinking State](#16-ai-thinking-state)
17. [Streaming UI](#17-streaming-ui)
18. [Chat Input](#18-chat-input)
19. [Send Button](#19-send-button)
20. [Cute Micro-interactions](#20-cute-micro-interactions)
21. [Animation System](#21-animation-system)
22. [Animation Rules](#22-animation-rules)
23. [Empty State](#23-empty-state)
24. [Error State](#24-error-state)
25. [Network State](#25-network-state)
26. [Markdown Renderer](#26-markdown-renderer)
27. [Code Block](#27-code-block)
28. [Responsive Design](#28-responsive-design)
29. [Accessibility](#29-accessibility)
30. [Design System](#30-design-system)
31. [Shadow](#31-shadow)
32. [Gradient](#32-gradient)
33. [Recommended Frontend Stack](#33-recommended-frontend-stack)
34. [Frontend Folder Structure](#34-frontend-folder-structure)
35. [Frontend State Architecture](#35-frontend-state-architecture)
36. [Chat State Flow](#36-chat-state-flow)
37. [Message Lifecycle](#37-message-lifecycle)
38. [Component State Matrix](#38-component-state-matrix)
39. [Phase 1 — Design System](#39-phase-1--design-system)
40. [Phase 2 — App Shell](#40-phase-2--app-shell)
41. [Phase 3 — Chat UI](#41-phase-3--chat-ui)
42. [Phase 4 — Markdown & Code](#42-phase-4--markdown--code)
43. [Phase 5 — Streaming](#43-phase-5--streaming)
44. [Phase 6 — Conversation](#44-phase-6--conversation)
45. [Phase 7 — Model Selector](#45-phase-7--model-selector)
46. [Phase 8 — File Upload](#46-phase-8--file-upload)
47. [Phase 9 — Tool / Agent UI](#47-phase-9--tool--agent-ui)
48. [Phase 10 — Settings](#48-phase-10--settings)
49. [Phase 11 — Accessibility & Performance](#49-phase-11--accessibility--performance)
50. [Phase 12 — Testing](#50-phase-12--testing)
51. [Frontend Quality Checklist](#51-frontend-quality-checklist)
52. [Definition of Done — Frontend MVP](#52-definition-of-done--frontend-mvp)
53. [Recommended MVP Screens](#53-recommended-mvp-screens)
54. [Development Priority](#54-development-priority)
55. [Final Frontend Architecture](#55-final-frontend-architecture)
56. [Core Design Philosophy](#56-core-design-philosophy)

---

## 1. Frontend Vision

Frontend được xây dựng không chỉ như một "Chat Box", mà là một:

> **AI Workspace — nơi người dùng có thể trò chuyện, làm việc và tương tác với LLM.**

Design Direction:

```text
Professional AI Workspace
          +
       Soft Pink
          +
     Minimal UI
          +
 Friendly Micro-interactions
          +
    Cute Animation
          +
      Excellent UX
```

Nguyên tắc quan trọng:

> **Cute in interaction, professional in structure.**

Không biến giao diện thành quá nhiều màu hồng hoặc quá "trẻ con". Pink nên đóng vai trò **Accent Color**, trong khi nền và typography vẫn giữ tính trung tính.

---

## 2. Design Goals

### 2.1. Visual Goals

UI phải:

- Clean.
- Modern.
- Soft.
- Friendly.
- Dễ đọc trong thời gian dài.
- Có hierarchy rõ ràng.
- Ít màu nhưng có điểm nhấn.
- Animation nhẹ và có mục đích.

### 2.2. UX Goals

Người dùng phải hiểu ngay:

```text
Tôi đang ở conversation nào?
          ↓
Tôi đang sử dụng model nào?
          ↓
Tôi nhập prompt ở đâu?
          ↓
AI đang làm gì?
          ↓
Tôi có thể thao tác gì với response?
```

### 2.3. Animation Goals

Animation phải:

```text
Fast
Smooth
Subtle
Friendly
Purposeful
```

Không nên:

```text
❌ Animation quá lâu
❌ Animation liên tục
❌ Animation gây phân tâm
❌ Animation làm chậm thao tác
❌ Animation xuất hiện ở mọi component
```

---

## 3. Design Language

### 3.1. Visual Personality

Sản phẩm nên tạo cảm giác:

```text
First Impression
        ↓
"Đây là một AI Platform chuyên nghiệp"

Interaction
        ↓
"UI này thân thiện và khá cute"
```

### 3.2. Design Keywords

```text
Soft
Clean
Smart
Friendly
Elegant
Minimal
Playful
Professional
```

---

## 4. Color System

### 4.1. Primary Pink

Đề xuất sử dụng Soft Pink / Rose Pink.

| Token        | Hex       |
| ------------ | --------- |
| Primary Pink | `#EC4899` |
| Pink Hover   | `#DB2777` |
| Pink Dark    | `#BE185D` |
| Light Pink   | `#FCE7F3` |
| Soft Pink    | `#FDF2F8` |

### 4.2. Neutral

| Token             | Hex       |
| ----------------- | --------- |
| Background        | `#FFFDFE` |
| Surface           | `#FFFFFF` |
| Surface Secondary | `#FAF8FA` |
| Border            | `#F1E8EE` |
| Text Primary      | `#27232A` |
| Text Secondary    | `#6B6470` |
| Text Muted        | `#9A929D` |

### 4.3. Semantic

| Token   | Hex       |
| ------- | --------- |
| Success | `#22C55E` |
| Warning | `#F59E0B` |
| Error   | `#EF4444` |
| Info    | `#3B82F6` |

---

## 5. Pink Usage Rule

Không sử dụng Pink cho toàn bộ giao diện.

**Nên dùng Pink cho:**

```text
Primary Button
Active Item
Focus State
Selected Model
AI Avatar
Links
Progress
Important Highlight
Cute Animation
```

**Không nên dùng Pink cho:**

```text
Toàn bộ background
Toàn bộ text
Tất cả card
Tất cả button
```

Tỷ lệ trực quan nên hướng tới:

```text
Neutral / White / Gray
        ~80–90%

Pink / Accent
        ~10–20%
```

---

## 6. Dark Mode

Dark Mode cần được thiết kế ngay từ đầu.

| Token      | Light     | Dark      |
| ---------- | --------- | --------- |
| Background | `#FFFDFE` | `#171318` |
| Surface    | `#FFFFFF` | `#211B21` |
| Surface 2  | —         | `#29212A` |
| Text       | `#27232A` | `#F9F5F8` |
| Muted      | —         | `#B9AEB8` |
| Primary    | `#EC4899` | `#F472B6` |

Dark Mode vẫn giữ Pink nhưng tránh màu quá sáng gây chói.

---

## 7. Typography

Đề xuất:

- **Primary Font:** Inter
- Hoặc: **Plus Jakarta Sans**
- Nếu muốn giao diện mềm mại hơn: **Nunito Sans**
- **Code:** JetBrains Mono

### Typography Scale

| Level   | Size    |
| ------- | ------- |
| H1      | 24–28px |
| H2      | 20–24px |
| H3      | 16–18px |
| Body    | 14–16px |
| Caption | 12–13px |
| Code    | 13–14px |

### Font Weight

| Element | Weight  |
| ------- | ------- |
| Heading | 600–700 |
| Body    | 400–450 |
| Button  | 500–600 |

---

## 8. Main Layout

Desktop:

```text
┌──────────────────────────────────────────────────────────────┐
│                         TOP BAR                              │
├───────────────┬──────────────────────────────────────────────┤
│               │                                              │
│   SIDEBAR     │                  CHAT AREA                   │
│               │                                              │
│ + New Chat    │                                              │
│               │          Welcome / Messages                  │
│ Search        │                                              │
│               │                                              │
│ Recent        │                                              │
│ ├─ Chat 01    │                                              │
│ ├─ Chat 02    │                                              │
│ └─ Chat 03    │                                              │
│               │                                              │
│ Projects      │                                              │
│               │                                              │
│ Settings      │                                              │
│               │                                              │
├───────────────┴──────────────────────────────────────────────┤
│                         CHAT INPUT                           │
└──────────────────────────────────────────────────────────────┘
```

---

## 9. Component Architecture

```text
App
│
├── AppShell
│
├── Header
│
├── Sidebar
│   ├── NewChatButton
│   ├── SearchConversation
│   ├── ConversationList
│   ├── ProjectList
│   └── UserMenu
│
├── ChatPage
│   ├── ChatHeader
│   ├── WelcomeScreen
│   ├── MessageList
│   │   ├── UserMessage
│   │   └── AssistantMessage
│   │
│   └── ChatInput
│       ├── AttachmentButton
│       ├── PromptInput
│       ├── ToolButton
│       ├── ModelSelector
│       └── SendButton
│
└── Settings
```

---

## 10. Header

Header nên tối giản.

```text
┌──────────────────────────────────────────────────────────────┐
│ ✨ AI Chat       [Gemma 4 ▼]             ⚙  ◯ Profile        │
└──────────────────────────────────────────────────────────────┘
```

### Thành phần

#### Logo

Có thể sử dụng `✦ AI Chat` hoặc logo icon riêng.

#### Model Selector

```text
[ ✨ Gemma 4 ▼ ]
```

Dropdown:

```text
Gemma 4
GPT
Claude
Gemini
Local LLM
```

Có thể hiển thị:

```text
Gemma 4
Google / Local
Context: 32K
```

---

## 11. Sidebar

Sidebar quản lý conversation.

```text
┌───────────────────────┐
│ ✨ AI Chat            │
│                       │
│ ＋ New Chat           │
│                       │
│ 🔍 Search             │
│                       │
│ Recent                │
│                       │
│ 💬 AI Agent           │
│ 💬 Poetry Project     │
│ 💬 Computer Vision    │
│ 💬 Data Quality       │
│                       │
│ Projects              │
│                       │
│ 📁 Research           │
│ 📁 Coding             │
│                       │
│                       │
│ ⚙ Settings            │
│ 👤 Profile            │
└───────────────────────┘
```

### Sidebar Behavior

| Device  | Behavior |
| ------- | -------- |
| Desktop | Expanded |
| Tablet  | Compact  |
| Mobile  | Drawer   |

---

## 12. New Chat Button

Đây là CTA chính.

```text
┌──────────────────────┐
│ ＋  New Chat         │
└──────────────────────┘
```

| State  | Style                                  |
| ------ | -------------------------------------- |
| Normal | `background: #EC4899`, `color: white`  |
| Hover  | `scale: 1.02` + soft pink shadow       |
| Click  | `scale: 0.98`                          |

---

## 13. Welcome Screen

Khi chưa có message:

```text
                 ✨

          Hello, I'm your AI

      What would you like to
           work on today?

 ┌────────────┐  ┌────────────┐
 │ ✨ Explore │  │ 💻 Coding  │
 └────────────┘  └────────────┘

 ┌────────────┐  ┌────────────┐
 │ 📚 Research│  │ 💡 Ideas   │
 └────────────┘  └────────────┘
```

### Cute Animation

Icon chính có thể float nhẹ lên xuống:

```text
       ✨
       ↑
       ↓
       ↑
```

Animation:

```text
duration: 2–3s
ease-in-out
infinite
```

Animation phải rất nhẹ.

---

## 14. Message Design

### User Message

```text
                    User

                    ┌───────────────────┐
                    │ Hello AI          │
                    └───────────────────┘
```

User bubble có thể dùng **Soft Pink**, nhưng tránh Pink quá đậm.

### Assistant Message

```text
┌────┐
│ ✨ │  Assistant
└────┘

Hello! How can I help you today?

[Copy] [Regenerate] [👍] [👎]
```

Assistant message nên rộng và thoáng hơn User message.

---

## 15. Assistant Avatar

Có thể dùng `✨` hoặc logo AI.

| State      | Style          |
| ---------- | -------------- |
| Idle       | `opacity: 0.8` |
| Generating | soft pulse     |

Không nên cho avatar xoay liên tục.

---

## 16. AI Thinking State

Thay vì `Loading...`, dùng:

```text
✨ Thinking...
```

hoặc:

```text
AI is thinking ···
```

Animation:

```text
AI is thinking
AI is thinking.
AI is thinking..
AI is thinking...
```

Hoặc `● ● ●` với từng dot xuất hiện tuần tự.

---

## 17. Streaming UI

Khi LLM stream:

```text
Assistant

Hello! I can help you with...
                         ▌
```

- Cursor: **blink**
- Khi response hoàn thành: **cursor disappears**

---

## 18. Chat Input

Đây là component quan trọng nhất.

```text
┌──────────────────────────────────────────────────────────┐
│ Ask anything...                                          │
│                                                          │
│ 📎       / Tool                  Gemma 4          ➤      │
└──────────────────────────────────────────────────────────┘
```

### State

| State      | Behavior                                    |
| ---------- | ------------------------------------------- |
| Idle       | Placeholder `Ask anything...`               |
| Focus      | border → pink, shadow → soft pink           |
| Typing     | normal                                      |
| Generating | `[ Stop ] ■`                                |

---

## 19. Send Button

| State      | Style        |
| ---------- | ------------ |
| Normal     | `➤`          |
| Hover      | `scale 1.05` |
| Click      | `scale 0.95` |
| Generating | `■`          |

Stop button phải dễ nhận biết và dễ click.

---

## 20. Cute Micro-interactions

Đây là nơi tạo personality cho sản phẩm.

### 20.1. Button Hover

```text
Normal
   ↓
Hover
   ↓
scale 1.02
+
soft shadow
```

### 20.2. Message Appearance

Message mới:

```text
opacity: 0      →  opacity: 1
translateY: 6px →  translateY: 0
```

Duration: **150–250ms**

### 20.3. Sidebar Item

| State    | Style                                              |
| -------- | -------------------------------------------------- |
| Hover    | `background → #FDF2F8`                             |
| Selected | `background → #FCE7F3` + left indicator → Pink     |

### 20.4. Copy Success

```text
Copy
 ↓
✓ Copied!
```

Có thể thêm một sparkle nhỏ `✦`, nhưng chỉ xuất hiện trong khoảng **300–500ms**.

---

## 21. Animation System

Tạo animation tokens ngay từ đầu.

| Token  | Duration |
| ------ | -------- |
| Fast   | 150ms    |
| Normal | 200ms    |
| Medium | 300ms    |
| Slow   | 500ms    |

Animations:

```text
fadeIn
slideUp
scaleIn
softPulse
float
shimmer
```

Easing:

```text
ease-out
ease-in-out
```

---

## 22. Animation Rules

**Nên animation:**

```text
Button
Message
AI Status
Copy Success
Modal
Sidebar
Welcome Illustration
```

**Không nên animation:**

```text
❌ Background liên tục
❌ Text nhấp nháy
❌ Gradient chuyển động liên tục
❌ Card bounce liên tục
❌ Mọi component đều animate
```

Nguyên tắc:

> **Animation phải giải thích trạng thái hoặc tạo feedback.**

---

## 23. Empty State

Conversation trống:

```text
              🌸

        Start a new idea

    Ask me anything. I'm here
         to help you explore.

       [ Start Chatting ]
```

Visual có thể dùng: `✨` `🌸` `💗` `🌷` — nhưng nên chọn một visual language nhất quán.

---

## 24. Error State

Không nên chỉ hiển thị:

```text
500 Internal Server Error
```

Nên hiển thị:

```text
Oops! Something went wrong 💗

I couldn't complete that response.

[ Try Again ]
```

Technical detail có thể nằm bên dưới:

```text
Error ID: xxx
```

---

## 25. Network State

Khi mất kết nối:

```text
┌──────────────────────────────────┐
│ ⚠ Connection interrupted         │
│ Reconnecting...                  │
└──────────────────────────────────┘
```

Khi reconnect:

```text
✓ Connected
```

Sau đó tự động ẩn notification.

---

## 26. Markdown Renderer

Assistant response cần hỗ trợ:

- Markdown
- Code
- Table
- Quote
- List
- Link
- LaTeX

---

## 27. Code Block

```text
┌────────────────────────────────────┐
│ Python                    Copy     │
├────────────────────────────────────┤
│ def hello():                       │
│     print("Hello")                 │
└────────────────────────────────────┘
```

Features:

- Language label
- Syntax highlighting
- Copy
- Horizontal scroll
- Line wrapping option

Copy feedback:

```text
Copy
 ↓
✓ Copied
```

---

## 28. Responsive Design

### Desktop

```text
Sidebar: 260–300px
Chat: flexible
Input: max-width ~900px
```

### Tablet

```text
Sidebar: 220–260px
```

### Mobile

```text
Sidebar → Drawer
Header
   ↓
Chat
   ↓
Input
```

```text
┌──────────────────────┐
│ ☰   AI Chat    ⚙     │
├──────────────────────┤
│                      │
│     Chat Messages    │
│                      │
│                      │
├──────────────────────┤
│ 📎 Ask...       ➤    │
└──────────────────────┘
```

---

## 29. Accessibility

Frontend phải hỗ trợ:

- Keyboard navigation.
- Focus state rõ ràng.
- Screen reader labels.
- `aria-label` cho icon button.
- Color contrast phù hợp.
- Không dùng màu sắc làm tín hiệu duy nhất.
- Reduced motion.

Nếu người dùng bật `prefers-reduced-motion` thì giảm hoặc tắt các animation không cần thiết.

---

## 30. Design System

Tạo Design System ngay từ đầu:

```text
design-system/
│
├── colors
├── typography
├── spacing
├── radius
├── shadows
├── animation
└── components
```

### Border Radius

Friendly nhưng vẫn professional:

| Component   | Radius  |
| ----------- | ------- |
| Button      | 10–12px |
| Input       | 14–18px |
| Card        | 16–20px |
| Chat Bubble | 14–18px |
| Modal       | 20px    |

Không nên biến tất cả thành pill.

---

## 31. Shadow

Sử dụng shadow nhẹ:

| Element     | Shadow         |
| ----------- | -------------- |
| Card        | soft shadow    |
| Input focus | pink glow nhẹ  |
| Modal       | medium shadow  |

Không dùng shadow quá đậm.

---

## 32. Gradient

Gradient chỉ nên dùng cho:

- Logo.
- Welcome illustration.
- CTA đặc biệt.
- Highlight.

Ví dụ:

```text
Pink
   ↓
Rose
   ↓
Soft Purple
```

Không dùng gradient cho toàn bộ background.

---

## 33. Recommended Frontend Stack

| Category         | Technology                                      |
| ---------------- | ----------------------------------------------- |
| Core             | Next.js, React, TypeScript                      |
| Styling          | Tailwind CSS                                    |
| UI Components    | shadcn/ui                                       |
| Icons            | Lucide React                                    |
| State Management | Zustand                                         |
| Animation        | Framer Motion                                   |
| Markdown         | react-markdown, remark-gfm, rehype-highlight    |
| Form             | React Hook Form                                 |
| Validation       | Zod                                             |

---

## 34. Frontend Folder Structure

```text
frontend/
│
├── app/
│   ├── page.tsx
│   ├── chat/
│   │   └── [conversationId]/
│   │       └── page.tsx
│   │
│   ├── settings/
│   │   └── page.tsx
│   │
│   └── layout.tsx
│
├── components/
│   ├── chat/
│   │   ├── ChatWindow.tsx
│   │   ├── ChatHeader.tsx
│   │   ├── MessageList.tsx
│   │   ├── UserMessage.tsx
│   │   ├── AssistantMessage.tsx
│   │   ├── ChatInput.tsx
│   │   ├── StreamingMessage.tsx
│   │   └── MessageActions.tsx
│   │
│   ├── sidebar/
│   │   ├── Sidebar.tsx
│   │   ├── NewChatButton.tsx
│   │   ├── ConversationList.tsx
│   │   └── ConversationItem.tsx
│   │
│   ├── model/
│   │   └── ModelSelector.tsx
│   │
│   ├── markdown/
│   │   ├── MarkdownRenderer.tsx
│   │   └── CodeBlock.tsx
│   │
│   ├── common/
│   │   ├── Button.tsx
│   │   ├── Modal.tsx
│   │   └── Tooltip.tsx
│   │
│   └── animations/
│       ├── FadeIn.tsx
│       ├── SlideUp.tsx
│       └── FloatingIcon.tsx
│
├── hooks/
│   ├── useChat.ts
│   ├── useStreaming.ts
│   ├── useConversation.ts
│   └── useMediaQuery.ts
│
├── stores/
│   ├── chatStore.ts
│   ├── uiStore.ts
│   └── modelStore.ts
│
├── services/
│   ├── chatApi.ts
│   ├── conversationApi.ts
│   ├── fileApi.ts
│   └── modelApi.ts
│
├── lib/
│   ├── api.ts
│   ├── markdown.ts
│   └── utils.ts
│
├── types/
│   ├── chat.ts
│   ├── message.ts
│   ├── model.ts
│   └── conversation.ts
│
├── styles/
│   └── globals.css
│
└── public/
    ├── icons/
    └── illustrations/
```

---

## 35. Frontend State Architecture

State nên được tách thành:

```text
UI State
│
├── Sidebar open/close
├── Theme
├── Modal
└── Selected model

Chat State
│
├── Messages
├── Streaming
├── Generating
└── Error

Conversation State
│
├── Current conversation
├── Conversation list
└── Search

User State
│
├── Profile
└── Preferences
```

Không nên đưa tất cả vào một global store duy nhất.

---

## 36. Chat State Flow

```text
User types
     ↓
ChatInput
     ↓
useChat()
     ↓
chatStore
     ↓
POST /api/chat
     ↓
SSE Stream
     ↓
useStreaming()
     ↓
Update message
     ↓
AssistantMessage
     ↓
MarkdownRenderer
```

---

## 37. Message Lifecycle

```text
IDLE
 │
 ▼
SUBMITTING
 │
 ▼
STREAMING
 │
 ├── token
 ├── token
 ├── token
 │
 ▼
COMPLETED
```

Error:

```text
SUBMITTING
    ↓
ERROR
```

User stop:

```text
STREAMING
    ↓
STOPPED
```

---

## 38. Component State Matrix

Mỗi component quan trọng phải xác định:

```text
Default
Hover
Focus
Active
Disabled
Loading
Streaming
Success
Error
Empty
```

Ví dụ **Send Button**:

| State      | Style        |
| ---------- | ------------ |
| Default    | Pink         |
| Hover      | Darker Pink  |
| Active     | Scale Down   |
| Disabled   | Gray         |
| Generating | Stop         |
| Error      | Retry        |

---

## 39. Phase 1 — Design System

**Tasks**

- [ ] Define color tokens.
- [ ] Define typography.
- [ ] Define spacing.
- [ ] Define border radius.
- [ ] Define shadows.
- [ ] Define animation tokens.
- [ ] Setup Tailwind theme.
- [ ] Setup dark mode.

**Output:** Reusable Design System

---

## 40. Phase 2 — App Shell

**Tasks**

- [ ] Create AppShell.
- [ ] Create Header.
- [ ] Create Sidebar.
- [ ] Create responsive layout.
- [ ] Create theme switcher.

**Output:** Working Application Shell

---

## 41. Phase 3 — Chat UI

**Tasks**

- [ ] Welcome Screen.
- [ ] Message List.
- [ ] User Message.
- [ ] Assistant Message.
- [ ] Chat Input.
- [ ] Send Button.
- [ ] Stop Button.
- [ ] Message Actions.

**Output:** Static Chat UI

---

## 42. Phase 4 — Markdown & Code

**Tasks**

- [ ] Markdown renderer.
- [ ] Syntax highlighting.
- [ ] Copy code.
- [ ] Table rendering.
- [ ] LaTeX.
- [ ] Link handling.

**Output:** Production-quality Message Renderer

---

## 43. Phase 5 — Streaming

**Tasks**

- [ ] SSE client.
- [ ] Streaming state.
- [ ] Token append.
- [ ] Cursor animation.
- [ ] Stop generation.
- [ ] Error handling.

**Output:** Real-time AI Chat

---

## 44. Phase 6 — Conversation

**Tasks**

- [ ] Conversation list.
- [ ] Create conversation.
- [ ] Rename conversation.
- [ ] Delete conversation.
- [ ] Search conversation.
- [ ] Load conversation.

**Output:** Persistent Chat Workspace

---

## 45. Phase 7 — Model Selector

**Tasks**

- [ ] Model dropdown.
- [ ] Model metadata.
- [ ] Model availability state.
- [ ] Context window display.
- [ ] Provider indicator.

---

## 46. Phase 8 — File Upload

**Tasks**

- [ ] Drag & drop.
- [ ] File picker.
- [ ] Upload progress.
- [ ] File preview.
- [ ] Remove attachment.
- [ ] Upload error.

UI:

```text
┌───────────────────────────────┐
│ 📄 research.pdf               │
│ 2.4 MB                  ✓     │
└───────────────────────────────┘
```

---

## 47. Phase 9 — Tool / Agent UI

Khi Backend hỗ trợ Tool Calling:

```text
Assistant

Working on it...

✓ Search
✓ Retrieve document
⟳ Analyze
```

Tool event nên được hiển thị dưới dạng **compact activity card**, không chiếm quá nhiều diện tích.

Ví dụ:

```text
┌──────────────────────────────────┐
│ ✨ AI Activity                   │
│                                  │
│ ✓ Search                         │
│ ✓ Read document                  │
│ ⟳ Analyze                        │
└──────────────────────────────────┘
```

---

## 48. Phase 10 — Settings

```text
Appearance
├── Light
├── Dark
└── System

Chat
├── Enter to send
├── Show timestamps
└── Auto-scroll

Model
├── Default model
└── Temperature

Privacy
├── Clear conversations
└── Data settings
```

---

## 49. Phase 11 — Accessibility & Performance

### Accessibility

- [ ] Keyboard navigation.
- [ ] ARIA labels.
- [ ] Focus management.
- [ ] Reduced motion.
- [ ] Contrast check.

### Performance

- [ ] Virtualize long message lists nếu cần.
- [ ] Lazy load heavy components.
- [ ] Optimize Markdown rendering.
- [ ] Avoid unnecessary global state updates.
- [ ] Debounce conversation search.
- [ ] Optimize animations bằng `transform` và `opacity`.

---

## 50. Phase 12 — Testing

### Unit Test

- Component
- Hook
- Utility
- State

### Integration Test

- Chat Input → API
- SSE → Message State
- Conversation → UI

### E2E Test

```text
Open App
    ↓
New Chat
    ↓
Type Prompt
    ↓
Send
    ↓
Streaming
    ↓
Response
    ↓
Reload
    ↓
Conversation remains
```

---

## 51. Frontend Quality Checklist

### Visual

- [ ] Pink palette nhất quán.
- [ ] Không quá nhiều màu.
- [ ] Typography rõ ràng.
- [ ] Spacing nhất quán.
- [ ] Icons cùng một style.
- [ ] Animation đồng nhất.

### UX

- [ ] Người dùng biết AI đang làm gì.
- [ ] Send/Stop dễ sử dụng.
- [ ] Error message dễ hiểu.
- [ ] Conversation dễ tìm.
- [ ] Mobile usable.

### Technical

- [ ] TypeScript strict.
- [ ] Component reusable.
- [ ] State tách biệt.
- [ ] API layer tách khỏi UI.
- [ ] Responsive.
- [ ] Accessibility.
- [ ] Error boundary.
- [ ] Loading state.

---

## 52. Definition of Done — Frontend MVP

Frontend MVP hoàn thành khi:

- [ ] Responsive Desktop / Tablet / Mobile.
- [ ] Light Mode.
- [ ] Dark Mode.
- [ ] Pink Design System.
- [ ] Sidebar.
- [ ] New Chat.
- [ ] Conversation List.
- [ ] Chat Area.
- [ ] Welcome Screen.
- [ ] User Message.
- [ ] Assistant Message.
- [ ] Markdown.
- [ ] Code Highlight.
- [ ] Copy.
- [ ] Regenerate.
- [ ] Streaming.
- [ ] Stop Generation.
- [ ] Error State.
- [ ] Loading State.
- [ ] Model Selector.
- [ ] Cute Micro-interactions.
- [ ] Reduced Motion.
- [ ] Mobile Navigation.
- [ ] Basic Accessibility.
- [ ] E2E Chat Flow.

---

## 53. Recommended MVP Screens

Chỉ cần triển khai 5 màn hình chính:

1. Welcome / New Chat
2. Chat Conversation
3. Conversation Search
4. Settings
5. Profile / User Menu

Sau MVP:

6. File / Knowledge
7. Tool Activity
8. Agent Run
9. Model Management
10. Evaluation / Analytics

---

## 54. Development Priority

| Priority | Nhóm               | Hạng mục                                                                                   |
| -------- | ------------------ | ------------------------------------------------------------------------------------------ |
| **P0**   | Core UX            | App Shell, Sidebar, Chat, Input, Message                                                   |
| **P1**   | AI Interaction     | Streaming, Stop, Regenerate, Markdown                                                      |
| **P2**   | Personal Workspace | Conversations, Search, Model Selector, Settings                                            |
| **P3**   | Personality        | Cute Animation, Micro-interactions, Welcome Illustration, Friendly Empty/Error State       |
| **P4**   | Advanced AI        | File Upload, RAG, Tool Calling, Agent                                                      |
| **P5**   | Production         | Accessibility, Performance, Testing, Monitoring                                            |

---

## 55. Final Frontend Architecture

```text
                         FRONTEND
                            │
                ┌───────────┴───────────┐
                │                       │
             UI Layer              State Layer
                │                       │
       ┌────────┼────────┐       ┌──────┼──────┐
       │        │        │       │      │      │
      Chat    Sidebar  Settings  Chat   UI   Model
       │                         State  State State
       └────────────┬──────────────────────────┘
                    │
                    ▼
               Service Layer
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Chat API  File API  Model API
          │         │         │
          └─────────┼─────────┘
                    ▼
                 Backend
                    │
                    ▼
               LLM Gateway
```

---

## 56. Core Design Philosophy

Frontend phải tuân theo 5 nguyên tắc:

1. **SIMPLE** — Người dùng không cần học cách sử dụng UI.
2. **CLEAR** — Trạng thái của AI luôn rõ ràng.
3. **FRIENDLY** — Error, Loading và Empty State đều có personality.
4. **PROFESSIONAL** — Cute nhưng không childish.
5. **SCALABLE** — UI hiện tại phải sẵn sàng cho RAG, Tool Calling và Agent trong tương lai.

### Design Statement

> **Clean UI → Clear Interaction → Soft Pink → Cute Micro-animation → Professional AI Experience**

### Final Product Feeling

```text
┌───────────────────────────────────────────┐
│                                           │
│               ✨ AI Chat                  │
│                                           │
│        Professional AI Workspace          │
│                    +                      │
│                Soft Pink                  │
│                    +                      │
│          Friendly Interaction             │
│                    +                      │
│             Cute Animation                │
│                                           │
└───────────────────────────────────────────┘
```

**Mục tiêu cuối cùng:** Người dùng nhìn vào cảm thấy đây là một **AI product chuyên nghiệp**, nhưng trong quá trình sử dụng lại có cảm giác **nhẹ nhàng, thân thiện và có personality**.
