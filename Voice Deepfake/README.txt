DEEPFAKE AUDIO DETECTOR - SETUP GUIDE

1. Create a Virtual Environment (to keep things clean):
   python -m venv .venv

2. Activate the Environment:
   .venv\Scripts\activate
   
3. Install Required Libraries:
   pip install -r requirements.txt

--- 3. HOW TO TEST AN AUDIO FILE ---
1. Copy the audio/video file you want to test into this folder.
2. Open 'universal.py' in a text editor 
3. Find the line: TEST_FILE_PATH = r"..."
4. Change it to your file's name (e.g., r"my_recording.wav").
5. Save the file.

4. Run the Detector:
   Make sure your terminal still shows '(.venv)'. Then type:
   python test_universal.py
