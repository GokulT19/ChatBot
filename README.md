# Voice-Based ChatGPT Assistant

This is a voice-enabled AI assistant built with Python. It uses OpenAI's GPT model to answer your questions and responds using text-to-speech. You can speak to it, and it will reply with audio.

---

## Features

- Recognizes speech using Google Speech API
- Generates replies using OpenAI's GPT-4
- Speaks responses using Google Text-to-Speech (gTTS)
- Plays a beep sound before listening
- Detects spoken language (basic support)

---

## Requirements

Install the required Python packages:

```
pip install -r requirements.txt
```

### Dependencies:

- pygame  
- numpy  
- SpeechRecognition  
- gTTS  
- openai  
- langdetect  

---

## How to Use

1. Replace `'openai key'` in the script with your actual OpenAI API key.
2. Run the script:

```
python ChatBot.py
```

3. Wait for the beep, then ask your question.
4. Say **"exit"** or **"quit"** to stop.

---

## Notes

- You need a working microphone.
- Make sure you’re connected to the internet.
- By default, it supports English but can be extended to more languages.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Author

Developed by Gokul Thakral
