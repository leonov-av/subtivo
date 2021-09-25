import re
import functions_tools

def get_speech_audio_file_texttospeech_festival(text,speed,file):
    text = re.sub('"',"",text)
    text = re.sub('’', "'", text)
    text = re.sub('\n', " ", text)
    command = 'echo "' + text + '" > ' + file + '.txt; text2wave ' + file + '.txt > ' + file + 'temp.wav;' + \
              ' ffmpeg -y -i ' + file + 'temp.wav -af "atempo=' + str(0.2*speed+1) + '" ' + file + ';' + \
              'rm ' + file + 'temp.wav; ' + 'rm ' + file + '.txt; '
    functions_tools.execute_command(command)
