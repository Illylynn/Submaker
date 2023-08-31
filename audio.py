#!/usr/bin/env python

from gtts import gTTS

import pydub
import os

def create_audio(text, file_name, index, option):
    
    language = "en"

    text = " ".join(text.split("|"))

    obj = gTTS(text=text, lang=language, slow=False)

    obj.save(file_name + ".mp3")

    audio = pydub.AudioSegment.from_file(file_name + ".mp3", format="mp3")

    audio = audio - 50

    if index > 0:
        sound = pydub.AudioSegment.from_file("Background/" + option) * 100
        audio = audio.overlay(sound[:(len(audio) / audio.frame_rate * sound.frame_rate)] - 20)

    audio.export("Subs/" + file_name + ".wav", format="wav")
    os.remove(file_name + ".mp3")
    
