# How to Run the Project Locally

This guide provides step-by-step instructions to run the Backend (FastAPI), Frontend (React/Vite), and Streamlit Dashboard concurrently. You will need to open three separate terminal windows.

## Prerequisites
- Make sure you have Node.js and Python installed.
- Your Python virtual environment (`venv`) should be created.

---

### 1. Run the Backend (FastAPI)

1. Open your first terminal.
2. Navigate to the backend directory:
   ```bash
   cd carepoint-clinic/backend
   ```
3. Activate the virtual environment (located in the root folder):
   - **Windows:**
     ```cmd
     ..\..\venv\Scripts\activate
     ```
   - **Mac/Linux:**
     ```bash
     source ../../venv/bin/activate
     ```
4. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
   *The backend will now be running at http://localhost:8000*

---

### 2. Run the Frontend (React + Vite)

1. Open a **second** terminal window.
2. Navigate to the frontend directory:
   ```bash
   cd carepoint-clinic/frontend
   ```
3. Install the dependencies (if you haven't already):
   ```bash
   npm install
   ```
4. Start the development server:
   ```bash
   npm run dev
   ```
   *The frontend will typically run at http://localhost:5173*

---

### 3. Run the Streamlit Dashboard

1. Open a **third** terminal window.
2. Ensure you are in the root directory (`aihackathon`).
3. Activate the virtual environment:
   - **Windows:**
     ```cmd
     venv\Scripts\activate
     ```
   - **Mac/Linux:**
     ```bash
     source venv/bin/activate
     ```
4. Start the Streamlit application:
   ```bash
   streamlit run dashboard.py
   ```
   *The Streamlit dashboard will open in your browser, usually at http://localhost:8501*
