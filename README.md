# 🚀 Job Application Automator (Job-Copilot)

An end-to-end intelligent system designed to streamline the job search and application process. Job-Copilot discovers companies, scrapes relevant job postings, filters them based on your preferences, and automatically fills out complex job application forms using an AI-powered browser extension.

![Autofill Success Demonstration](<img width="1920" height="945" alt="image" src="https://github.com/user-attachments/assets/89f39769-cccc-48e7-9958-f554af122da5" />)

## 🌟 Key Features

- **🏢 Company Discovery & Management**: Automatically discover tech companies hiring in your field, categorized by their ATS (Greenhouse, Lever, Ashby, Workday).
- **🕵️‍♂️ Intelligent Job Scraping**: Automated workflows to scrape job postings from approved companies.
- **🎯 Smart Filtering**: Set preferences for location (e.g., Canada only), remote work, keywords, and seniority to filter out noise.
- **✨ Smart Job Auto-Filler**: A dedicated Chrome extension that learns your application inputs and uses semantic AI matching to automatically populate complex application forms (supporting Greenhouse, Lever, Ashby, Workday).
- **🎨 Premium UI/UX**: A modern, glassmorphic React dashboard with dark mode support for managing your job hunt.
- **🔒 Secure Architecture**: Multi-user support with JWT authentication.

## 🏗️ System Architecture

The project is divided into three main components:

1. **`job-copilot` (Backend)**
   - Built with **Python** & **FastAPI**.
   - Handles data storage (SQLite), AI provider integration (Gemini/OpenAI), job scraping workflows, and authentication.
   - Responsible for semantic matching logic used by the extension.

2. **`job-copilot-frontend` (Dashboard)**
   - Built with **React** & **Vite**.
   - Provides the visual interface to manage discovered companies, view job matches, update your profile, and tweak system preferences.

3. **`autofill-extension` (Browser Extension)**
   - Built with **Manifest V3**.
   - Interacts with job application pages. It learns your inputs as you type and can automatically fill forms based on your saved profile and semantic matching from the backend.

---

## 📸 Screenshots

### Preferences & Dynamic Filtering
Customize your job search to your exact needs, including geographical filtering.

![Preferences Drawer](<img width="1920" height="945" alt="image" src="https://github.com/user-attachments/assets/baca49d4-86d7-44a1-afcb-3275f7c8d7ba" />)

### Job Dashboard Alignment
View matched jobs in a clean, responsive grid layout.

![Job Dashboard](<img width="1920" height="997" alt="image" src="https://github.com/user-attachments/assets/19d93062-8456-4b98-b2fa-8e6aadafb35a" />)

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+** (for the backend)
- **Node.js 18+** (for the frontend)
- **Google Chrome** (for the extension)
- An AI Provider API Key (e.g., Gemini API Key)

### 1. Backend Setup (`job-copilot`)
1. Navigate to the backend directory:
   ```bash
   cd job-copilot
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows: .\venv\Scripts\activate
   # Mac/Linux: source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   - Create a `.env` file from the supplied `.env.example` (if any), or ensure your `GEMINI_API_KEY` and `SECRET_KEY` are set.
5. Start the server:
   ```bash
   uvicorn api.main:app --reload
   ```
   *The backend will run on `http://127.0.0.1:8000`.*

### 2. Frontend Setup (`job-copilot-frontend`)
1. Navigate to the frontend directory:
   ```bash
   cd job-copilot-frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   *The dashboard will run on `http://localhost:5173`. Open this in your browser to sign up / log in.*

### 3. Extension Setup (`autofill-extension`)
1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Enable **Developer mode** (toggle in the top right).
3. Click **Load unpacked** and select the `/autofill-extension` folder.
4. Click the extension icon in your browser toolbar to log in using the same credentials you created on the frontend dashboard.
5. Navigate to a supported job application page (e.g., Ashby, Greenhouse). The extension will automatically kick in!

## 📖 Usage Guide

1. **Upload Resume**: Start by setting up your profile on the frontend dashboard (`/profile`). Upload your resume to automatically extract key information.
2. **Set Preferences**: Go to the settings drawer and define your desired keywords, locations, and Work Authorization country.
3. **Discover Companies**: From the main dashboard, hit **Run Company Discovery** to find target companies. Approve the ones you like.
4. **Scan Jobs**: Hit **Scan for New Jobs**. The backend will scrape the approved companies' boards and filter the jobs against your preferences.
5. **Auto-Apply**: Click "Apply" on a job card. When the ATS page opens, the Chrome extension will semantically match your profile data to the form fields and autofill them for you. If it misses a field, simply fill it manually—the extension "learns" from your inputs for next time!

---

*Built with ❤️ to kill the repetitive pain of job hunting.*
