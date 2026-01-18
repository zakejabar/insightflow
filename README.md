# 🧠 InsightFlow V2: Advanced Agentic Research Engine

> **"Digital assistants that help college students or professionals with their research."**

InsightFlow is a **Production-Grade Cognitive Agent** designed for deep, autonomous research. Unlike linear RAG systems, it uses a **Cyclic State Machine (LangGraph)** to plan, research, critique its own findings, and self-correct—mimicking a senior human researcher.

---

## ✨ Key Features

- 🔄 **Self-Correcting Loop**: Agent critiques its own work and refines searches automatically
- 🎓 **Academic Mode**: Filters for peer-reviewed papers with citation impact (Semantic Scholar)
- 🌍 **Web Mode**: Deep scraping + Tavily search for market research
- 👁️ **Transparent UI**: Real-time logs show the agent's thought process
- 🛡️ **Anti-Hallucination**: Strict constraints prevent fabricated citations
- ⚡ **Production-Ready**: Type-safe (Pydantic), rate-limit resilient, graceful error handling

---

## 🚀 The "Agentic" Difference

Most AI wrappers are linear (`Input -> Search -> Answer`). InsightFlow is **Cyclic**.

### 1. 🧠 Cognitive Architecture (The Loop)
The agent doesn't just fetch data; it **thinks**.
- **Planner**: Breaks vague queries ("Future of AI") into specific executable strategies.
- **Gatherer**: Context-aware routing.
    - *Web Mode*: Uses **Tavily** + **Deep Scraping** for market research.
    - *Academic Mode*: Uses **Semantic Scholar** to filter for peer-reviewed papers (impact factor > 50).
- **Analyst (Reflexion)**: Reads the data and asks: *"Is this enough?"*
    - If **No**: It loops back (`Loop Count < 3`) with new, refined queries.
    - If **Yes**: It proceeds to the Writer.

### 2. 🛡️ Enterprise Reliability
Built to prove that AI can be trusted in high-stakes environments.
- **Anti-Hallucination**: Strict prompt engineering forbids inventing citations. "No data" is a valid answer.
- **Type Safety**: Replaced dangerous `eval()` with **Pydantic** models. Outputs are guaranteed valid JSON.
- **Resilience**: Implemented **Exponential Backoff** for API rate limits (handles 429 errors gracefully).

### 3. 👁️ Transparent Cortex UI
We don't hide the AI's logic. We visualize it.
- **Neural Stream**: A real-time terminal showing the agent's internal monologue ("🤖 Planner: Analyzing...", "🌍 Network: GET 200 OK").
- **Live State Pulse**: Visual indicators show exactly which specialized agent is active.

---

## 🏗️ Architecture

```
User Query
    ↓
┌─────────────────────────────────────┐
│  🎯 PLANNER                         │
│  Breaks query into sub-questions    │
└──────────────┬──────────────────────┘
               ↓
         ┌─────────────┐
         │   Router    │
         └─────┬───┬───┘
               │   │
        Web ←──┘   └──→ Academic
         ↓              ↓
    🌍 Tavily      🎓 Scholar
         ↓              ↓
    📖 Scraper          │
         └──────┬───────┘
                ↓
    ┌───────────────────────┐
    │  🧠 ANALYST           │
    │  Extracts insights    │
    └──────────┬────────────┘
               ↓
          Enough info?
         ┌─────┴─────┐
        No           Yes
         │            │
    Loop back        ↓
         │      ✍️ WRITER
         │           ↓
         └──→   📄 Report
```

---

## 🛠️ Tech Stack

- **Orchestration**: LangGraph (Cyclic State Management)
- **Backend**: FastAPI (Python 3.11), Pydantic
- **Frontend**: Next.js 14, TailwindCSS, Glassmorphism UI
- **Search**: Tavily API (Web), Semantic Scholar API (Academic)
- **Model**: OpenRouter / Groq (Llama 3 / GPT-4)

---

## ⚡ Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- API Keys: [OpenRouter](https://openrouter.ai/) or [Groq](https://groq.com/), [Tavily](https://tavily.com/)

### Installation

```bash
# 1. Clone
git clone https://github.com/zakejabar/insightflow.git
cd insightflow

# 2. Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure API Keys
cp .env.example .env
# Edit .env and add your keys:
# OPENROUTER_API_KEY=your_key_here
# TAVILY_API_KEY=your_key_here

# 4. Frontend Setup
cd ../frontend
npm install

# 5. Run System
# Terminal A (Backend)
cd backend && source venv/bin/activate && python main.py

# Terminal B (Frontend)
cd frontend && npm run dev
```

Visit `http://localhost:3000` to start your research engine.

---

## 🐛 Troubleshooting

### **"Rate limit hit" errors**
**Cause:** Semantic Scholar API has strict rate limits.  
**Fix:** The system auto-retries with exponential backoff. If it persists, increase the delay:
```bash
# In backend/.env
RETRY_DELAY_BASE=5.0  # Default is 2.0
```

### **"Module not found" errors**
**Cause:** Virtual environment not activated.  
**Fix:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### **Frontend shows "Failed to fetch status"**
**Cause:** Backend not running or CORS issue.  
**Fix:** Ensure backend is running on `http://localhost:8000`. Check terminal for errors.

---

## 🎓 Design Decisions

### **Why LangGraph instead of LangChain?**
LangChain is linear. LangGraph supports cyclic workflows, which I needed for the Reflexion loop where the agent can loop back to gather more data.

### **Why Pydantic models instead of raw LLM output?**
LLMs are probabilistic and can output malformed JSON. Pydantic guarantees type-safe, parsable outputs, making the system integration-ready.

### **Why separate Web and Academic modes?**
Google Search is optimized for broad queries. Semantic Scholar is optimized for peer-reviewed research. Using the right tool for the job improves both speed and accuracy.

### **Why the "Transparent Cortex" UI?**
Trust comes from visibility. Showing the agent's thought process (logs, network calls, decision points) builds user confidence and aids debugging.

---

## 👨‍💻 Author

**Zahir Jabar**
- *AI Engineer specialized in Agentic Systems*
- [LinkedIn](https://www.linkedin.com/in/zahir-jabar-7b7944281/)
- [Portfolio](https://github.com/zakejabar)

> *"Reliability is not an accident. It is an architecture."*
