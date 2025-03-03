from django.test import TestCase

# Create your tests here.
from django.shortcuts import render
import os
# Create your views here.
import playsound
import webbrowser
from gtts import gTTS
import speech_recognition as sr
import datetime
import pyautogui
from time import sleep


def tell_time():
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")  # 24-hour format

    # Time message
    time_message = f"The current time is {current_time}"
    alexia.speak(time_message)


def close_vs_code():
    pyautogui.click(1455, 132)


def exit_vs_code():
    location = None

    # Locate the image and click it
    while location is None:
        location = pyautogui.locateOnScreen('Exit.png', confidence=0.9)
        sleep(2)  # Sleep to avoid excessive CPU usage

    pyautogui.click(location)  # Click on the located image


class VoiceAssistant:
    def __init__(self):
        # Use self.recognizer to make it accessible in all methods
        self.recognizer = sr.Recognizer()

    def record_audio(self):
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(
                source)  # Dynamically adjust for noise
            try:
                # Set a timeout for listening and a phrase limit for processing
                audio = self.recognizer.listen(
                    source, timeout=3, phrase_time_limit=8)
            except sr.WaitTimeoutError:
                print("Listening timed out while waiting for speech.")
                return None
        return audio

    def recognize_speech(self, audio):
        if audio is None:
            return ""
        try:
            text = self.recognizer.recognize_google(audio, language="en-US")
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that!")
        except sr.RequestError:
            print("Sorry, there was an error processing your request")
        return ""

    def speak(self, audio):
        tts = gTTS(text=audio, lang="en", slow=False)
        audio_file = "audio.mp3"
        tts.save(audio_file)
        playsound.playsound(audio_file)
        print(audio)
        sleep(5)
        os.remove(audio_file)


def search_words_in_string(word_list, text):
    # Find words from word_list in the string
    found_words = [word for word in word_list if word in text]
    return len(found_words) != 0


def respond(voice_data, alexia):
    if search_words_in_string(["what's your name", "my name"], voice_data):
        alexia.speak("Hello, my name is Alexa")

    if search_words_in_string(["who's invented you", "invented"], voice_data):
        alexia.speak("Hello, its Albert who created me")

    if search_words_in_string(["why did albert create you", "create you"], voice_data):
        alexia.speak("I,m his personal assistant, thank you for asking")

    if search_words_in_string(["open google", "google"], voice_data):
        webbrowser.open("https://www.google.com")

    if search_words_in_string(["open visual studio", "visual studio code"], voice_data):
        os.system("code")

    if search_words_in_string(["open wikipedia", "wikipedia"], voice_data):
        webbrowser.open("https://en.wikipedia.org/wiki/Main_Page")

    if search_words_in_string(["what's the time", "time"], voice_data):
        tell_time()

    if search_words_in_string(["thank you", "thanks"], voice_data):
        alexia.speak("You're welcome")

    if search_words_in_string(["close visual studio", "close visual studio code"], voice_data):
        alexia.speak("Okay")
        close_vs_code()

    elif search_words_in_string(["close google", "close google chrome"], voice_data):
        alexia.speak("Okay")
        exit_vs_code()

    elif search_words_in_string(["close", "exit"], voice_data):
        alexia.speak("Goodbye")
        exit_vs_code()


if __name__ == "__main__":
    alexia = VoiceAssistant()
    while True:
        voice_note = alexia.record_audio()
        recognized_text = alexia.recognize_speech(voice_note)
        if recognized_text:
            respond(recognized_text, alexia)
