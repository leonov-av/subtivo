import requests
import re
import os
import pyttsx3
import ffmpeg_wrapper


def get_speech_audio_file_fromtexttospeech(text,speed,file):
    headers = {
        'Origin': 'http://www.fromtexttospeech.com',
        'Upgrade-Insecure-Requests': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36',
        'X-DevTools-Emulate-Network-Conditions-Client-Id': '4D3512C486D82AC8B65EC149B3509560',
        'Referer': 'http://www.fromtexttospeech.com/',
    }

    data = [
      ('input_text', text),
      ('language', 'British English'),
      ('voice', 'IVONA Brian22 (UK English)'),
      ('speed', str(speed)),
      ('action', 'process_text'),
    ]

    response = requests.post('http://www.fromtexttospeech.com/', headers=headers, data=data)

    file_url = re.sub("file=", "http://www.fromtexttospeech.com", re.findall("file=/output/[0-9]*/[0-9]*.mp3", response.text)[0])
    r = requests.get(file_url)
    with open(file, 'wb') as f:
        f.write(r.content)

def get_speech_audio_file_texttospeech_responsivevoice(text,speed,file):

    headers = {
        'pragma': 'no-cache',
        'cookie': '__cfduid=d7fbc9143908ce1c95527a71c61277e581527354143; _ga=GA1.2.1586836185.1527354636; _gid=GA1.2.1926337946.1527354636',
        'accept-encoding': 'identity;q=1, *;q=0',
        'accept-language': 'en-US,en;q=0.9,ru;q=0.8',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36',
        'accept': '*/*',
        'cache-control': 'no-cache',
        'authority': 'code.responsivevoice.org',
        'referer': 'http://texttospeech.io/',
        'range': 'bytes=0-',
    }

    print(str(0.55 + 0.01*speed))
    params = (
        ('t', text),
        ('tl', 'en-GB'),
        ('sv', 'g1'),
        ('vn', 'rjs'),
        ('pitch', '0.5'),
        ('rate', str(0.55 + 0.1*speed)),
        ('vol', '1'),
        ('gender', 'male'),
    )

    r = requests.get('https://code.responsivevoice.org/getvoice.php', headers=headers, params=params)
    with open(file, 'wb') as f:
        f.write(r.content)


#     Microsoft tts
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


def save_phrase_to_file(text, engine, voice_id, voce_rate, file):
    # Use female English voice
    engine.setProperty('voice', voice_id)
    engine.setProperty('rate', voce_rate)
    wav_file = re.sub(".mp3",".wav",file)
    engine.save_to_file(text, wav_file, name = "text")
    engine.runAndWait()
    ffmpeg_wrapper.convert_wav_to_mp3(wav_file=wav_file, mp3_file=file)
    os.remove(wav_file)


def stop_engine(engine):
    engine.stop()


def get_speech_audio_file_texttospeech_microsoft(text,speed,file):
    engine = get_engine()
    voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0"
    voce_rate = 200 + 10 * int(speed)
    save_phrase_to_file(text, engine, voice_id, voce_rate, file)
    stop_engine(engine)



# text = "Hello! My name is Alexander Leonov and today I would like to talk about vulnerabilities and Vulnerability Databases."
# speed = 0
# file = "test.mp3"
# get_speech_audio_file_texttospeech_responsivevoice(text,speed,file)