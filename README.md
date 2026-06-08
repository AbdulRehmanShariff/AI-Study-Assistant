# 🧠 AI Study Assistant

An intelligent, beautifully designed full-stack web application aimed at supercharging the modern student's workflow. Upload any document, and let the AI instantly generate detailed summaries, interactive flashcards, challenging quizzes, and answer any contextual questions you have about your study material.

**Developed By:** [Rehman Shariff](https://github.com/AbdulRehmanShariff)

---

## ✨ Features & Project Showcases

Below is a complete walkthrough of the AI Study Assistant's capabilities and user interface.

### 🔐 Authentication

Secure and seamless login and registration system.
_(Replace this text with your login/register screenshot)_
`![Authentication](C:\AI Study Assistant\Results_screenshots\Login_page.png)`

### 📊 User Dashboard

A central hub to track recent uploads, conversations, and view study statistics at a glance.
_(Replace this text with your dashboard screenshot)_
`![Dashboard Overview](C:\AI Study Assistant\Results_screenshots\Dashboard.png)`

### 📤 Document Upload

A sleek drag-and-drop interface allowing users to securely upload PDFs and text documents for AI processing.
_(Replace this text with your upload page screenshot)_
`![Document Upload](C:\AI Study Assistant\Results_screenshots\uploads_folders.png)`

### 📋 AI Summaries

Instantly transform massive files into concise bullet points, detailed overviews, or actionable takeaways using Gemini 1.5 Flash.
_(Replace this text with your summary result screenshot)_
`![AI Summaries](C:\AI Study Assistant\Results_screenshots\Generating_Summaries.png)`

### 💬 Contextual AI Chat

Ask the AI highly specific questions about your uploaded materials, powered by FAISS Vector Search for accurate context retrieval.
_(Replace this text with your chat result screenshot)_
`![AI Chat Interface](C:\AI Study Assistant\Results_screenshots\AI_chatbot_result.png)`

### 🧠 Interactive Flashcards

Automatically generate highly-detailed flip-cards designed to maximize active recall and memory retention.
_(Replace this text with your flashcard screenshot)_
`![Flashcards Overview](C:\AI Study Assistant\Results_screenshots\Flashcards_results.png)`

### 📝 Smart Quizzes

Test your knowledge with multiple-choice quizzes that generate challenging distractors and provide deep, educational explanations for the correct answers.
_(Replace this text with your quiz result screenshot)_
`![Quiz Results](C:\AI Study Assistant\Results_screenshots\Quiz_result.png)`

---

## 🛠️ Technology Stack

- **Frontend:** React.js, Custom CSS (Glassmorphism & Neumorphism Aesthetics)
- **Backend:** Python, Flask, PyJWT
- **Database:** MongoDB
- **AI Integration:** Google Gemini (1.5 Flash)
- **Vector Search / RAG:** FAISS & Sentence Transformers
- **Document Processing:** PyPDF

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js & npm
- MongoDB installed locally or MongoDB Atlas URI

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/AbdulRehmanShariff/ai-study-assistant.git
   cd ai-study-assistant
   ```

2. **Setup the Backend:**

   ```bash
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate   # On Mac/Linux: source venv/bin/activate
   pip install -r requirements.txt
   ```

   _Rename `.env.example` to `.env` and add your Google Gemini API key._

3. **Setup the Frontend:**
   ```bash
   cd ../frontend
   npm install
   ```

### Running the App Locally

1. Start the backend server: `cd backend` -> `python app.py`
2. Start the frontend website: `cd frontend` -> `npm start`
