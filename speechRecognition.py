# Listen to the microphone and tries to recognize any words the user says

import speech_recognition as sr

"""Followed this documentation to record and recognize audio
   https://pypi.org/project/SpeechRecognition/2.1.3/"""

def recognizeSpeech():
    print("hit")
    r = sr.Recognizer()
    mic = sr.Microphone(device_index=0)

    # Adjusts the recognizer sensitivity for ambient noise and records audio
    with mic as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    response = ""

    # Try recognizing the speech in the recording
    try:
        response = r.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response = None
        print("API unavailable")
    except sr.UnknownValueError:
        # speech was unintelligible
        response = None
        print("Unable to recognize speech")

    return response
