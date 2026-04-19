# AI-Powered Multilingual Smart Agricultural Chatbot using Transformer Models

An AI-driven agricultural chatbot designed to assist farmers by providing intelligent, multilingual responses using advanced Transformer models. This project is split into a Python backend and a React (Vite) frontend.

## Prerequisites

Before you begin, ensure you have the following installed on your computer:
- **Python 3.8+** (for the backend)
- **Node.js** & **npm** (for the frontend)
- **Git**

---

## 🚀 Getting Started

Follow these step-by-step instructions to set up the project on your local machine. You will need to run the backend and the frontend simultaneously in two separate terminals.

### 1. Backend Setup (Python)

The backend handles the AI model and logic. You must set up a "Virtual Environment" to prevent library conflicts.

1. **Open a terminal** in the root project folder (`final year project`).
2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```
3. **Activate the virtual environment:**
   - On **Windows**:
     ```powershell
     .\.venv\Scripts\activate
     ```
   - On **Mac/Linux**:
     ```bash
     source .venv/bin/activate
     ```
   *(Note: You should now see `(.venv)` at the beginning of your terminal line, meaning it is active).*

4. **Install the required libraries:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Start the backend server:**
   Navigate into the backend folder and start the script:
   ```bash
   cd backend
   python main.py
   ```
   *Leave this terminal running!*

---

### 2. Frontend Setup (React/Vite)

The frontend is the user interface you interact with in your browser. 

1. **Open a NEW terminal window** (keep the backend terminal running).
2. **Navigate into the frontend directory:**
   ```bash
   cd frontend
   ```
3. **Install the node modules (libraries):**
   This downloads all frontend dependencies.
   ```bash
   npm install
   ```
4. **Start the development server:**
   ```bash
   npm run dev
   ```
5. **Open the web app:**
   The terminal will output a local link (usually `http://localhost:5173`). **Ctrl+Click** that link to open the chatbot in your web browser!

---

## 💡 Troubleshooting
- **"pip is not recognized"**: Make sure Python is added to your system's PATH during installation.
- **"npm is not recognized"**: Ensure you have installed Node.js correctly.
- **Packages not found**: Ensure your virtual environment `(.venv)` is activated before running `pip install` and `python main.py`.
