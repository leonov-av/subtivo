import re
import functions_tools
import functions_audio_wrappers


def get_speech_audio_file_texttospeech_linux_coqui_ai(text,speed,file):
    voce_rate = 200 + 10 * int(speed)
    text = re.sub('"',"",text)
    functions_tools.execute_command('tts --text "' + text + '"  --out_path ' + file + ".wav")
    functions_audio_wrappers.convert_wav_to_mp3(wav_file=file + ".wav", mp3_file=file)
    print(text)