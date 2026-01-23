#  Multimodal Deepfake Detection System

A comprehensive deep learning system designed to detect synthetic media manipulation in both **Video** and **Audio**. The system uses a microservices architecture with a React frontend and two specialized Flask backends.

##  Features
* **Video Detection:** Uses ResNet + LSTM to analyze frame sequences for visual anomalies.
* **Audio Detection:** Analyzes spectral patterns (MFCCs/Mel Spectrograms) to detect AI-generated voice.
* **Automated Model Fetching:** Automatically downloads the latest trained models from **Hugging Face** on first startup.
* **Reporting:** Generates detailed analysis reports with confidence scores and flagged frames.

---

##  Tech Stack
* **Frontend:** React.js / Next.js (TypeScript)
* **Video Backend:** Python, Flask, TensorFlow/Keras, OpenCV, Dlib
* **Audio Backend:** Python, Flask, PyTorch, Librosa
* **Model Hosting:** Hugging Face Hub

---

##  Prerequisites
Before running the project, ensure you have the following installed:
* [Python 3.11](https://www.python.org/downloads/)
* [Node.js & npm](https://nodejs.org/)
* [Git](https://git-scm.com/)
* **FFmpeg** (Required for audio/video processing)
    * *Windows:* `winget install ffmpeg`
    * *Mac:* `brew install ffmpeg`
    * *Linux:* `sudo apt install ffmpeg`

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
### OR
npm start

##### If all three files launched successfully , then stop their execution , add venv python .exe paths for DeepFake and Voice Deepfake folders respective in "orchestrator.py". After this , we can launch the application by only running "python orchestrator.py" instead of three individual services.
