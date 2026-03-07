# Copyright Detection in Generative AI

A comprehensive deep learning system designed to detect synthetic media manipulation in both **Video** and **Audio**. The system uses a microservices architecture with a React frontend and two specialized Flask backends.

## Features

- **Video Detection:** Uses ResNet + LSTM to analyze frame sequences for visual anomalies.
- **Audio Detection:** Analyzes spectral patterns (MFCCs/Mel Spectrograms) to detect AI-generated voice.
- **Multimodal Fusion:** Intelligently combines video and audio analysis with confidence blending.
- **JWT Authentication:** Secure user registration and login with token-based session management.
- **Analysis History:** Users can view, track, and delete their past analysis results.
- **Creator Registration:** Creators can register to protect their identity against unauthorized deepfakes.
- **Copyright Detection:** Automatically detects if flagged faces match registered protected identities.
- **Identity Matching:** Uses FaceNet embeddings for high-accuracy face comparison (0.6+ threshold).
- **License Status Tracking:** Identifies unauthorized usage of protected identities.
- **Automated Model Fetching:** Automatically downloads the latest trained models from **Hugging Face** on first startup.
- **Detailed Reporting:** Generates comprehensive analysis reports with confidence scores, flagged frames, and audio segments.
- **Zero Retention Policy:** All uploaded files deleted immediately after processing for privacy compliance.
- **Service Orchestration:** Single command to launch all 4 microservices (video, audio, identity, frontend).

---

## Tech Stack

- **Frontend:** React.js / Next.js (TypeScript)
- **Video Backend:** Python, Flask, TensorFlow/Keras, OpenCV, Dlib
- **Audio Backend:** Python, Flask, PyTorch, Librosa
- **Identity Service:** Python, Flask, FaceNet, OpenCV DNN
- **Database:** SQLite3 (User accounts, analysis history, protected identities, license records)
- **Model Hosting:** Hugging Face Hub
- **Authorization:** JWT (JSON Web Tokens)
- **Orchestration:** Multi-service launcher (orchestrator.py)

---

## Prerequisites

Before running the project, ensure you have the following installed:

- [Python 3.11](https://www.python.org/downloads/)
- [Node.js & npm](https://nodejs.org/)
- [Git](https://git-scm.com/)
- **FFmpeg** (Required for audio/video processing)
  - _Windows:_ `winget install ffmpeg`
  - _Mac:_ `brew install ffmpeg`
  - _Linux:_ `sudo apt install ffmpeg`

---

## Installation & Setup

Clone the repository:
git clone [https://github.com/Codesmith-23/Deepfake-Detection-System.git](https://github.com/Codesmith-23/Deepfake-Detection-System.git)
cd Deepfake-Detection-System

# Setting up Audio detection:

### Open a new terminal

cd "Voice Deepfake"

### Create virtual environment (Optional but recommended)

python -m venv venv

#### Windows:

venv\Scripts\activate

#### Mac/Linux:

source venv/bin/activate

### Install dependencies

pip install -r requirements.txt

### Run the Audio Service

python api_audio.py

# Setting up Video Detection :

### Open a NEW terminal (keep the previous one running)

cd "DeepFake/backend"

### Create virtual environment

python -m venv venv

#### Windows:

venv\Scripts\activate

#### Mac/Linux:

source venv/bin/activate

### Install dependencies

pip install -r requirements.txt

### Run the Video Service

python app.py

### Open a NEW terminal

cd "DeepFake/frontend"

### Install Node modules

npm install

### Start the React App

npm run dev

---

## Quick Start with Orchestrator

Once you've completed the initial setup above, you can launch all services with a **single command**:

```bash
python orchestrator.py
```

This will automatically start:

- Identity Service (Port 5002)
- Audio API (Port 5001)
- Video Backend (Port 5000)
- Frontend (Port 3000)

**Note:** Configure the Python paths in `orchestrator.py` before first use.
