# 🧠 InsightFlow

**AI research agent that delivers comprehensive reports in 10 minutes instead of 6 hours.**

Built with LangGraph multi-agent system, Next.js, and real-time web search.


## 🎯 What It Does

InsightFlow automates research by:
1. **Breaking down** complex queries into searchable sub-questions
2. **Searching** the web for relevant sources
3. **Analyzing** information and extracting key insights
4. **Generating** comprehensive reports with citations

## 🚀 Live Demo

Try it: [Your deployed link or localhost instructions]

## ⚡ Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- OpenRouter API key (or Groq)
- Tavily API key

### Installation
```bash
# Clone repo
git clone https://github.com/yourusername/insightflow
cd insightflow

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env

# Frontend setup
cd ../frontend
npm install

# Run both
# Terminal 1:
cd backend && python main.py

# Terminal 2:
cd frontend && npm run dev
```

Visit http://localhost:3000

## 🏗️ Architecture
```
┌─────────────┐
│  Next.js UI │ ← User submits query
└──────┬──────┘
       │ HTTP POST
       ▼
┌─────────────┐
│  FastAPI    │ ← Returns job_id immediately
└──────┬──────┘
       │ Async
       ▼
┌─────────────────────────────────┐
│  LangGraph Multi-Agent System   │
├─────────────────────────────────┤
│ 1. Planner   → Sub-questions    │
│ 2. Gatherer  → Web search       │
│ 3. Analyzer  → Extract insights │
│ 4. Reporter  → Generate report  │
└─────────────────────────────────┘
       │
       ▼ Poll every 2s
┌─────────────┐
│  Show       │
│  Progress   │
└─────────────┘
```

## 🛠️ Tech Stack

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- React Markdown

**Backend:**
- Python 3.11
- FastAPI
- LangGraph (multi-agent orchestration)
- OpenRouter API (LLM)
- Tavily API (web search)

## 📊 Performance

- **Speed**: 10-15 seconds average
- **Cost**: ~$0.02-0.05 per research
- **Accuracy**: Cites sources for all claims

## 🎓 Why I Built This

I needed to do market research for a project and spent 6 hours manually reading articles and taking notes. I thought: "AI should do this."

So I built InsightFlow in 3 days using LangGraph to orchestrate multiple specialized agents. Each agent has one job: planning, searching, analyzing, or reporting.

## 🚧 Roadmap

- [ ] PDF upload support
- [ ] Save research history
- [ ] Custom agent workflows
- [ ] Multi-language support
- [ ] API for developers

## 📝 License

MIT

## 👤 Author

**Your Name**
- LinkedIn: https://www.linkedin.com/in/zahir-jabar-7b7944281/
- Portfolio: https://github.com/zakejabar

---

⭐ Star this repo if it helped you!
