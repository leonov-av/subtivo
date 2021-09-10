import re
import os
import pyttsx3
import functions_ffmpeg_wrapper

def get_voices_report(engine):
    voices = engine.getProperty('voices')
    for voice in voices:
        print("Voice:")
        print(" - ID: %s" % voice.id)
        print(" - Name: %s" % voice.name)
        print(" - Languages: %s" % voice.languages)
        print(" - Gender: %s" % voice.gender)
        print(" - Age: %s" % voice.age)

def get_engine():
    engine = pyttsx3.init()
    return engine

def stop_engine(engine):
    engine.stop()

def save_phrase_to_file(text, engine, voice_id, voce_rate, file):
    # Use female English voice
    engine.setProperty('voice', voice_id)
    engine.setProperty('rate', voce_rate)
    wav_file = re.sub(".mp3",".wav",file)
    engine.save_to_file(text, wav_file, name = "text")
    engine.runAndWait()
    functions_ffmpeg_wrapper.convert_wav_to_mp3(wav_file=wav_file, mp3_file=file)
    os.remove(wav_file)

def get_speech_audio_file_texttospeech_microsoft(text,speed,file):
    engine = get_engine()
    voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0"
    voce_rate = 200 + 10 * int(speed)
    save_phrase_to_file(text, engine, voice_id, voce_rate, file)
    stop_engine(engine)