# Fair Frame - AI Bias Detection Platform

Fair Frame is a production-ready AI web application that analyzes bias in text, images, audio, and video using Gemini 2.5 Flash and Sarvam AI.

## Features
- **Multi-modal Analysis**: Support for Text, Image, Audio, and Video.
- **Bias Scoring**: 0-100 scale with intensity labels.
- **Detailed Insights**: Type of bias, root cause, and explanation.
- **Neutral Suggestions**: AI-generated rewrites to remove bias.
- **History Tracking**: Securely store and review past analyses.
- **Premium UI**: ChatGPT-style interface with modern dark mode aesthetics.

## Tech Stack
- **Frontend**: React (Vite), TailwindCSS, Framer Motion, Firebase Auth.
- **Backend**: FastAPI (Python), FFmpeg, Gemini 2.5 Flash.
- **Database**: Firebase Firestore.
- **Speech-to-Text**: Sarvam AI.

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- Node.js 18+
- FFmpeg installed on your system.
- Supabase Project setup with Google Auth.

### 2. Backend Setup
1. Navigate to the `backend` folder.
2. Create environment:
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```
3. Update `.env` with your API keys:
   - `GEMINI_API_KEY`: Get from [Google AI Studio](https://aistudio.google.com/).
   - `SARVAM_API_KEY`: Get from [Sarvam AI](https://www.sarvam.ai/).
   - `SUPABASE_URL` & `SUPABASE_SERVICE_ROLE_KEY`: From Supabase Project Settings > API.
4. Run the backend:
```bash
python main.py
```

### 3. Frontend Setup
1. Navigate to the `frontend` folder.
2. Install dependencies:
```bash
npm install
```
3. Update `.env` with your `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`.
4. Run the frontend:
```bash
npm run dev
```

## Database Schema (Supabase)
Create an `analysis` table in Supabase with the following SQL:
```sql
create table analysis (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id),
  input_type text,
  input_content text,
  bias_score int,
  bias_detected boolean,
  bias_type text,
  cause_of_bias text,
  suggestion_to_fix text,
  explanation text,
  created_at timestamp with time zone default now()
);
```

## Security
- Image uploads limited to 5MB.
- Audio uploads limited to 10MB.
- Video uploads limited to 25MB (Max 30 seconds processed).

## License
MIT
