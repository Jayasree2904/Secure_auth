
# Secure_Auth
SecureAuth-Your voice and gesture are your keys. It is a smart, touchless login system that blends voice commands and hand gestures using SpeechRecognition and MediaPipe, powered by Flask



## Tech Stack

**Backend:**

- Flask – Python web framework

- MySQL – Data storage

- SpeechRecognition – Voice-to-text

- pydub + FFmpeg – Audio conversion

- MediaPipe  – Real-time hand gesture detection and landmark extraction.

**Frontend:**

- HTML, CSS, JavaScript – UI & interaction




## Screenshots

![App Screenshot](https://github.com/Jayasree2904/Secure_auth/blob/master/screenshots/home.png?raw=true)

![App Screenshot](https://github.com/Jayasree2904/Secure_auth/blob/master/screenshots/register.png?raw=true)

![App Screenshot](https://github.com/Jayasree2904/Secure_auth/blob/master/screenshots/login.png?raw=true)

![App Screenshot](https://github.com/Jayasree2904/Secure_auth/blob/master/screenshots/dashboard.png?raw=true)

![App Screenshot](https://github.com/Jayasree2904/Secure_auth/blob/master/screenshots/voice_mismatch.png?raw=true)

![App Screenshot](https://github.com/Jayasree2904/Secure_auth/blob/master/screenshots/no%20hand%20detected.png?raw=true)



## Run Locally

Clone the project

```bash
  git clone https://github.com/Jayasree2904/Secure_auth.git
```

Go to the project directory

```bash
  cd Secure_auth
```

Set Up Python Environment

```bash
  python -m venv venv
  venv\Scripts\activate
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the Flask Server

```bash
  python app.py
```

