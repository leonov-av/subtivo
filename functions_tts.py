import functions_tts_ms
import functions_tts_festival
import configs

def get_speech_audio_file_texttospeech(text,speed,file):
    if configs.os == "Windows":
        return functions_tts_ms.get_speech_audio_file_texttospeech_microsoft(text, speed, file)
    elif configs.os == "Linux":
        return functions_tts_festival.get_speech_audio_file_texttospeech_festival(text, speed, file)


# Debug
text = "Hello! My name is Alexander Leonov and today I would like to talk about vulnerabilities and Vulnerability Databases."
speed = 3
file = "test.mp3"
get_speech_audio_file_texttospeech(text,speed,file)