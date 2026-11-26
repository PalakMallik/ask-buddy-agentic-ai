# 🤖 Ask Buddy — Agentic AI Chatbot

**Ask Buddy** is an Agentic AI-powered chatbot that combines Google's Gemini AI, LangGraph, and web search capabilities to deliver intelligent and context-aware conversations.

Unlike a basic chatbot, Ask Buddy can use an AI agent workflow to determine when external tools are needed, retrieve relevant information through web search, and generate responses based on the available context.

The application features a modern web interface, conversational memory, streaming responses, and a FastAPI backend.

---

## ✨ Features

- **Agentic AI Workflow:** Uses LangGraph to coordinate AI reasoning and tool execution.
- **Google Gemini Integration:** Generates intelligent and context-aware responses.
- **Web Search:** Integrates Google Serper to retrieve relevant information from the web.
- **Conversational Memory:** Maintains conversation context and stores chat history.
- **Streaming Responses:** Displays AI-generated responses progressively.
- **Chat History Management:** Create and revisit previous conversations.
- **Interactive Web Interface:** Modern frontend built with HTML, CSS, and JavaScript.
- **REST API:** FastAPI handles communication between the frontend and backend.
- **Database Integration:** SQLite and SQLAlchemy manage conversations and messages.

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| Programming Language | Python, JavaScript |
| Frontend | HTML5, CSS3, JavaScript |
| Backend | FastAPI |
| Large Language Model | Google Gemini |
| AI Framework | LangChain, LangGraph |
| Search Tool | Google Serper API |
| Database | SQLite |
| ORM | SQLAlchemy |
| API Documentation | Swagger UI |
| Version Control | Git, GitHub |

## 🏗️ Project Architecture

Ask Buddy follows a frontend-backend architecture:

1. **Frontend:** Accepts user queries and displays conversations.
2. **FastAPI Backend:** Handles API requests and coordinates application logic.
3. **AI Agent:** Uses Gemini and LangGraph to process queries and coordinate tool usage.
4. **Web Search Tool:** Retrieves external information through Google Serper when needed.
5. **Database:** Stores conversations and messages using SQLite.

## 📁 Project Structure

```text
Ask-Buddy/
│
├── README.md
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   └── services/
│       └── gemini.py
│
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── assets/
│       └── logo.svg
│
├── data/
│   └── askbuddy.db
│
├── .env
├── .gitignore
└── requirements.txt
```

## ⚙️ Getting Started

Follow these steps to run Ask Buddy locally.

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/Ask-Buddy.git
```

```bash
cd Ask-Buddy
```

### 2. Create a Virtual Environment

```bash
python -m venv env
```

Activate the environment on Windows:

```bash
env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory.

Add your API credentials:

```env
GOOGLE_API_KEY=your_google_api_key
SERPER_API_KEY=your_serper_api_key
```

Replace the placeholder values with your actual API keys.

**Important:** Never commit your `.env` file or expose your API credentials publicly.

### 5. Run the Application

From the project root directory, execute:

```bash
uvicorn backend.main:app --reload
```

Open your browser and visit:

```text
http://127.0.0.1:8000
```

### 6. API Documentation

Explore the interactive FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

## 🔑 API Configuration

Ask Buddy requires the following API credentials:

| Environment Variable | Purpose |
|---|---|
| `GOOGLE_API_KEY` | Connects to Google Gemini |
| `SERPER_API_KEY` | Enables web search functionality |

Keep all API credentials secure using environment variables.

## 🚀 Future Enhancements

- Deploy Ask Buddy for public access.
- Introduce user authentication.
- Improve agent reasoning and tool selection.
- Add more external tools and integrations.
- Enhance conversation management and personalization.

## 👩‍💻 Author

**Palak Mallik**

- GitHub: [PalakMallik](https://github.com/PalakMallik)
- LinkedIn: [LinkedIn Profile](https://www.linkedin.com/in/palak-mallik/)

---

⭐ If you find this project interesting, consider giving it a star! ⭐