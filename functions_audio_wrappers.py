import functions_tools
import configs
import re

if configs.os == "Windows":
    ffmpeg_path = '''C:\\ffmpeg\\bin\\ffmpeg.exe'''
elif configs.os == "Linux":
    ffmpeg_path = '''/usr/bin/ffmpeg'''

def convert_wav_to_mp3(wav_file, mp3_file):
    command = ffmpeg_path + ''' -y -i ''' + wav_file + \
        ''' -vn -ar 44100 -ac 2 -b:a 192k ''' + mp3_file
    functions_tools.execute_command(command)

def create_silence_file(duration_s, file_path):
    command = ffmpeg_path + ''' -y -f lavfi -i anullsrc -t ''' + str(float(duration_s/1000)) + ''' ''' + file_path
    functions_tools.execute_command(command)

def create_silence_wav_sox(duration_s, file_path):
    command = '''sox -n -r 44100 -c 2 ''' + file_path + ''' trim 0.0 ''' + str(float(duration_s / 1000))
    functions_tools.execute_command(command)

def concat_files_in_list(file_list, mp3_file):
    command = ffmpeg_path + ''' -y -f concat -i ''' + file_list + ''' -c copy ''' + mp3_file
    functions_tools.execute_command(command)

def concat_files_sox(mask, result_file):
    #sox projects/test/audio_temp/part* result.wav
    command = "sox " + mask + " " + result_file
    functions_tools.execute_command(command)

def amix_files_in_list(file1, file2 , new_file):
    command = ffmpeg_path + ''' -i ''' + file1 + ''' -i ''' + file2 + ''' -filter_complex "amix" ''' + new_file
    functions_tools.execute_command(command)


def get_file_duration_ffmpeg(mp3_file):
    command = ffmpeg_path +  ''' -i ''' + mp3_file + " 2>&1 | grep 'Duration:'"
    output = functions_tools.execute_command(command)
    time_value = output.split(" ")[3].split(",")[0]
    duration = int(time_value.split(":")[0]) * 3600
    duration += int(time_value.split(":")[1]) * 60
    duration += int(time_value.split(":")[2].split(".")[0])
    duration += float("0." + time_value.split(":")[2].split(".")[1])
    return duration * 1000

def get_file_duration_mediainfo(mp3_file):
    command = '''mediainfo ''' + mp3_file + '''  | grep "Duration" | tail -n 1 | sed 's/ //g' | sed 's/.*://' '''
    output = functions_tools.execute_command(command)
    #1s567ms
    duration = re.sub("\\\\n","",str(output))
    duration = re.sub("ms","",duration)
    duration = re.sub("s", "", duration)
    duration = duration.split("'")[1]
    return int(duration)

# sudo apt-get install sox libsox-fmt-mp3 lame
def get_file_duration_sox(file_path):
    command = '''sox ''' + file_path + ''' -n stat 2>&1 | grep "Length" '''
    output = functions_tools.execute_command(command)
    duration = str(output).split(":")[1]
    duration = re.sub("\\\\n","",duration)
    duration = re.sub("[ \t\n\']*","",str(duration))
    return int(round(float(duration),3)*1000)


### Debug
# print(get_file_duration_sox("projects/test/audio_temp/1.mp3"))

# wav_file = '''projects\\kau\\audio_temp\\1.wav'''
# mp3_file = '''projects\\kau\\audio_temp\\1.mp3'''
# convert_wav_to_mp3(wav_file, mp3_file)