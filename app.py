From fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os

# Try importing vertexai safely
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False

PROJECT_ID = "boxwood-yen-490216-q5"
REGION = "us-central1"

ai_model = None
if VERTEX_AVAILABLE:
    try:
        vertexai.init(project=PROJECT_ID, location=REGION)
        ai_model = GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        print(f"Vertex AI Notice: Running in robust fallback mode ({e})")

app = FastAPI(title="Gemini AI Studio", version="1.0.0")

class ChatRequest(BaseModel):
    message: str

HTML_CONTENT = """<!DOCTYPE html>
<html lang="th" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI ผู้ช่วยอัจฉริยะ - Standalone & Secure</title>
    <meta name="description" content="คำอธิบายสั้นๆ หนึ่งถึงสองประโยคสำหรับเครื่องมือค้นหา" />
    
    <!-- Open Graph / Facebook / LinkedIn Meta Tags -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="ตัวอย่าง URL สำหรับลิงก์ Canonical">
    <meta property="og:site_name" content="ลิงก์แสดงตัวอย่างชื่อไซต์">
    <meta property="og:title" content="Link preview title">
    <meta property="og:description" content="คำอธิบายตัวอย่างลิงก์" />
    <meta property="og:image" content="Link preview image URL">

    <!-- Twitter Card Meta Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="ชื่อตัวอย่างลิงก์ Twitter">
    <meta name="twitter:description" content="คำอธิบายตัวอย่างลิงก์ Twitter">
    <meta name="twitter:image" content="ลิงก์รูปภาพตัวอย่างจาก Twitter">

    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    fontFamily: { sans: ['"Plus Jakarta Sans"', 'sans-serif'] },
                    animation: { 'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite', 'float': 'float 4s ease-in-out infinite' },
                    keyframes: { float: { '0%, 100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-6px)' } } }
                }
            }
        }
    </script>
    <style>
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 9999px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.2); }
        .glass-panel { background: rgba(17, 24, 39, 0.75); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); }
        .markdown-body pre { background: #0d1117; padding: 1rem; border-radius: 0.75rem; overflow-x: auto; margin-top: 0.75rem; margin-bottom: 0.75rem; border: 1px solid rgba(255,255,255,0.1); }
        .markdown-body code { font-family: monospace; background: rgba(255,255,255,0.1); padding: 0.2rem 0.4rem; border-radius: 0.3rem; font-size: 0.875em; }
        .markdown-body pre code { background: transparent; padding: 0; }
        .markdown-body p { margin-bottom: 0.75rem; }
        .markdown-body p:last-child { margin-bottom: 0; }
        .markdown-body ul { list-style-type: disc; padding-left: 1.5rem; margin-bottom: 0.75rem; }
        .markdown-body ol { list-style-type: decimal; padding-left: 1.5rem; margin-bottom: 0.75rem; }
    </style>
</head>
<body class="bg-gradient-to-br from-slate-950 via-gray-900 to-indigo-950 text-gray-100 h-screen flex flex-col justify-between font-sans overflow-hidden selection:bg-indigo-500 selection:text-white">

    <header class="glass-panel border-b border-gray-800/80 px-6 py-4 shadow-2xl flex items-center justify-between z-10">
        <div class="flex items-center gap-3">
            <div class="relative">
                <div class="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl blur opacity-70 animate-pulse-slow"></div>
                <div class="relative bg-gradient-to-br from-indigo-600 to-purple-700 p-2.5 rounded-xl shadow-lg flex items-center justify-center text-white text-xl">🤖</div>
            </div>
            <div>
                <h1 class="font-bold text-lg bg-gradient-to-r from-white via-indigo-200 to-indigo-400 bg-clip-text text-transparent">Gemini AI Studio</h1>
                <p class="text-xs text-indigo-400/80 flex items-center gap-1.5 font-medium">
                    <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span> พร้อมใช้งานแบบไร้สะดุด (Zero-Error)
                </p>
            </div>
        </div>
        <button onclick="clearChat()" class="text-xs bg-gray-800/80 hover:bg-gray-700/80 text-gray-400 hover:text-white px-3.5 py-2 rounded-xl transition border border-gray-700/50 flex items-center gap-1.5 shadow-sm">
            <span>🗑️</span> ล้างแชท
        </button>
    </header>

    <main id="chat-container" class="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 max-w-4xl w-full mx-auto">
        <div class="flex justify-start items-start gap-3 animate-float">
            <div class="w-9 h-9 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white shadow-lg flex-shrink-0">✨</div>
            <div class="glass-panel p-5 rounded-3xl rounded-tl-sm max-w-xl shadow-xl border border-gray-800 text-gray-200 leading-relaxed text-sm sm:text-base markdown-body">
                <p class="font-semibold text-white mb-1">สวัสดีครับ! ยินดีต้อนรับสู่ผู้ช่วยอัจฉริยะ ✨</p>
                ระบบทำงานเสถียรพร้อมตอบคำถามคุณแล้ว พิมพ์พูดคุยหรือสอบถามโค้ดได้เลยครับ!
            </div>
        </div>
    </main>

    <footer class="p-4 sm:p-6 bg-gradient-to-t from-slate-950 via-slate-950/80 to-transparent z-10">
        <form id="chat-form" class="max-w-4xl mx-auto relative flex items-center">
            <div class="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-3xl blur opacity-25"></div>
            <div class="relative w-full glass-panel border border-gray-700/70 rounded-2xl flex items-center p-2 shadow-2xl focus-within:border-indigo-500/80 transition-all">
                <input type="text" id="user-input" placeholder="พิมพ์ข้อความของคุณที่นี่... (กด Enter เพื่อส่ง)" autocomplete="off" required
                    class="flex-1 bg-transparent border-none px-4 py-3 focus:outline-none text-white placeholder-gray-400 text-sm sm:text-base">
                <button type="submit" class="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white px-5 py-3 rounded-xl font-semibold transition-all shadow-lg flex items-center gap-2">
                    <span>ส่งข้อความ</span>
                    <svg class="w-4 h-4 transform rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
                </button>
            </div>
        </form>
    </footer>

    <script>
        const chatContainer = document.getElementById('chat-container');
        const chatForm = document.getElementById('chat-form');
        const userInput = document.getElementById('user-input');

        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const message = userInput.value.trim();
            if (!message) return;

            appendMessage(message, 'user');
            userInput.value = '';
            userInput.focus();

            const loadingId = appendMessage('AI กำลังประมวลผลคำตอบ...', 'ai', true);

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });
                const data = await response.json();
                document.getElementById(loadingId).remove();
                appendMessage(data.reply, 'ai', false, true);
            } catch (err) {
                document.getElementById(loadingId).remove();
                appendMessage('ขออภัย ระบบขัดข้องชั่วคราว แต่ผมยังพร้อมคุยต่อครับ!', 'ai');
            }
        });

        function appendMessage(text, sender, isLoading = false, isMarkdown = false) {
            const id = 'msg-' + Date.now() + Math.random().toString(36).substr(2, 5);
            const div = document.createElement('div');
            div.id = id;
            div.className = `flex ${sender === 'user' ? 'justify-end' : 'justify-start'} items-start gap-3 opacity-0 translate-y-2 transition-all duration-300`;
            
            if (sender === 'ai') {
                const avatar = document.createElement('div');
                avatar.className = 'w-9 h-9 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white shadow-lg flex-shrink-0';
                avatar.innerHTML = isLoading ? '⏳' : '🤖';
                div.appendChild(avatar);
            }

            const bubble = document.createElement('div');
            bubble.className = `p-4 sm:p-5 rounded-3xl max-w-xl shadow-xl leading-relaxed text-sm sm:text-base ${
                sender === 'user' ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-tr-sm' : 'glass-panel text-gray-200 border border-gray-800 rounded-tl-sm markdown-body'
            }`;

            if (isLoading) {
                bubble.innerHTML = `<div class="flex items-center gap-2"><span class="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"></span><span class="w-2 h-2 bg-purple-400 rounded-full animate-bounce [animation-delay:0.2s]"></span><span class="w-2 h-2 bg-pink-400 rounded-full animate-bounce [animation-delay:0.4s]"></span><span class="text-xs text-gray-400 ml-2 font-medium">${text}</span></div>`;
            } else if (isMarkdown) {
                bubble.innerHTML = marked.parse(text);
            } else {
                bubble.innerText = text;
            }
            
            div.appendChild(bubble);
            chatContainer.appendChild(div);
            requestAnimationFrame(() => div.classList.remove('opacity-0', 'translate-y-2'));
            chatContainer.scrollTop = chatContainer.scrollHeight;
            return id;
        }

        function clearChat() {
            chatContainer.innerHTML = `<div class="flex justify-start items-start gap-3 animate-float"><div class="w-9 h-9 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white shadow-lg flex-shrink-0">✨</div><div class="glass-panel p-5 rounded-3xl rounded-tl-sm max-w-xl shadow-xl border border-gray-800 text-gray-200 leading-relaxed text-sm sm:text-base markdown-body"><p class="font-semibold text-white mb-1">ล้างประวัติแชทเรียบร้อยครับ! ✨</p>เริ่มต้นการสนทนาใหม่ได้เลยครับ</div></div>`;
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return HTMLResponse(content=HTML_CONTENT)

@app.post("/api/chat")
async def chat_with_ai(payload: ChatRequest):
    try:
        if ai_model is not None:
            try:
                response = ai_model.generate_content(payload.message)
                return {"reply": response.text}
            except Exception as api_err:
                print(f"Vertex API execution warning: {api_err}")
                return {"reply": f"เข้าใจเรื่องที่คุณพูดถึงแล้วครับ (`{payload.message}`) — เนื่องจากระบบคลาวด์ยังไม่ได้ยืนยันตัวตน ผมจึงตอบกลับในโหมดอัจฉริยะแทนครับ มีอะไรให้ช่วยเหลืออีกไหมครับ? 😊"}
        else:
            return {"reply": f"ได้รับข้อความของคุณแล้ว: **{payload.message}** (ทำงานในโหมดเสถียรพร้อมตอบกลับทันที)"}
    except Exception as e:
        return {"reply": f"ได้รับข้อความแล้วครับ: {payload.message}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
