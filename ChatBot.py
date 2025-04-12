import time
import threading
import queue
import pygame
import tempfile
import os
import numpy as np
import speech_recognition as sr
from gtts import gTTS
from openai import OpenAI
from langdetect import detect


# Initialize OpenAI client with API key
client = OpenAI(api_key='openai key')
supported_languages ={
    'en':'en',
}
def get_chatgpt_response(prompt, context=[]):
   try:
       messages = [{"role": "system", "content": "You are a helpful assistant."}] + context + [
           {"role": "user", "content": prompt}]
       response = client.chat.completions.create(
           model="gpt-4o-mini",
           temperature=0.5,
           top_p=1,
           max_tokens=130,
           messages=messages
       )
       answer = response.choices[0].message.content.strip()
       return answer
   except Exception as e:
       print(f"Error getting response from ChatGPT: {e}")
       return "I'm sorry, I couldn't process that."


def get_temp_file_path():
   temp_dir = tempfile.gettempdir()
   return os.path.join(temp_dir, "temp_audio.mp3")


def speak(text, lang='en'):
   tmp_file_path = get_temp_file_path()
   try:
       # Generate and save speech to a temporary file
       tts = gTTS(text=text, lang=lang, slow=False)
       tts.save(tmp_file_path)
       print(f"Temporary file saved at: {tmp_file_path}")

       # Initialize pygame mixer
       pygame.mixer.init(frequency=22050)
       pygame.mixer.music.load(tmp_file_path)
       pygame.mixer.music.play()

       # Wait for the audio to finish playing
       while pygame.mixer.music.get_busy():
           pygame.time.Clock().tick(10)
   except Exception as e:
       print(f"Error in text-to-speech: {e}")
   finally:
       time.sleep(1)  # Optional: Small delay to ensure file removal
       pygame.mixer.quit()
       try:
           os.remove(tmp_file_path)
       except Exception as e:
           print(f"Error deleting temporary file: {e}")


def play_startup_beep():
   try:
       pygame.mixer.init(frequency=21070)
       # Generate a 1-second beep sound
       sample_rate = 22050
       frequency = 700  # Frequency of the beep
       duration = 0.7  # Duration in seconds
       t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
       sound = 0.5 * np.sin(2 * np.pi * frequency * t)
       sound = (sound * 32767).astype(np.int16)  # Convert to 16-bit PCM
       # Convert to 2D array (stereo) by duplicating the mono data
       sound_stereo = np.stack((sound, sound), axis=-1)
       beep_sound = pygame.sndarray.make_sound(sound_stereo)
       beep_sound.play()
       time.sleep(duration)  # Wait for the beep to finish
   except Exception as e:
       print(f"Error playing startup beep: {e}")
   finally:
       pygame.mixer.quit()


def recognize_speech(result_queue, timeout=None):
   recognizer = sr.Recognizer()
   with (sr.Microphone() as source):
       print("Adjusting for ambient noise, please wait...")
       recognizer.adjust_for_ambient_noise(source, duration=1)
       print("Listening...")

       # Play the beep to signal readiness for listening
       play_startup_beep()

       try:
           audio = recognizer.listen(source, timeout=timeout)
           print("Processing...")
           text = recognizer.recognize_google(audio, show_all=False)
           print(f"You said: {text}")

           # Detect language of the spoken text
           detected_lang = detect(text)
           lang_code = supported_languages.get(detected_lang, 'en')  # Default to English if detection fails

           result_queue.put((text, lang_code))
       except sr.UnknownValueError:
           print("Sorry, I did not understand that.")
           speak("Sorry,I didn't catch that. Please wait for the beep and try again.", lang_code)
           result_queue.put((None, 'en'))
       except sr.RequestError as e:
           print(f"Could not request results; {e}")
           result_queue.put((None, 'en'))
       except sr.WaitTimeoutError:
           print("Listening timeout. No input detected.")
           result_queue.put((None, 'en'))
       except speech_recognition.UnknownValueError:
           speak("Sorry, I didn't catch that. Please wait for the beep and try again.", lang_code)
       except Exception as e:
           print(f"An error occurred: {e}")


def chat_loop():
   context = []
   while True:
       print("Say 'exit' or 'quit' to stop.")

       # Prompt for the next question
       speak("Please wait for the beep and then ask your  question.")

       # Wait for user input
       result_queue = queue.Queue()
       listen_thread = threading.Thread(target=recognize_speech, args=(result_queue, 60))  # Timeout set to 60 seconds
       listen_thread.start()
       listen_thread.join()

       user_input, lang_code = result_queue.get()
       if user_input and user_input.lower() in ['exit', 'quit']:
           speak("Thank you for connecting with us. Have a great day!", lang_code)
           break

       if user_input:
           # Process the response
           speak("Processing your request, please wait.", lang_code)
           response = get_chatgpt_response(user_input, context)
           context.append({"role": "user", "content": user_input})
           context.append({"role": "assistant", "content": response})

           # Speak the question and the response
           speak(f"You asked: {user_input}. Here is the answer: {response}. If you wish to exit, you can say 'exit' or 'quit'after beep.", lang_code)

def main():
   play_startup_beep()
   speak(
       "Hello Gokul Thakral, I'm your AI Assistant. I support a wide range of national and international languages. Feel free to ask your questions in any language.")

   chat_loop()


if __name__ == "__main__":
   main()
