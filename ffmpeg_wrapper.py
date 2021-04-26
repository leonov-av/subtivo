import subprocess

ffmpeg_path = '''C:\\ffmpeg\\bin\\ffmpeg.exe'''


def execute_command(command):
    process = subprocess.call(command,  shell=True)
    print(process)


def convert_wav_to_mp3(wav_file, mp3_file):
    command = ffmpeg_path + ''' -y -i ''' + wav_file + \
        ''' -vn -ar 44100 -ac 2 -b:a 192k ''' + mp3_file
    execute_command(command)


def create_silence_mp3(duration_s, mp3_file):
    command = ffmpeg_path + ''' -y -f lavfi -i anullsrc -t ''' + str(duration_s/1000) + ''' ''' + mp3_file
    execute_command(command)


def concat_files_in_list(file_list, mp3_file):
    command = ffmpeg_path + ''' -y -f concat -i ''' + file_list + ''' -c copy ''' + mp3_file
    execute_command(command)

# wav_file = '''projects\\kau\\audio_temp\\1.wav'''
# mp3_file = '''projects\\kau\\audio_temp\\1.mp3'''
# convert_wav_to_mp3(wav_file, mp3_file)