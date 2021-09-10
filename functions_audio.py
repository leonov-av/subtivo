from pydub import AudioSegment

# second_of_silence = AudioSegment.silent() # use default
# second_of_silence = AudioSegment.silent(duration=1000)
#
# second_of_silence.export("out.wav", format="wav")  # Is the same as:

def get_silence(duration):
    return AudioSegment.silent(duration)


def get_audio_from_file(file):
    return AudioSegment.from_mp3(file)


def analyse_audio_file(file):
    song = AudioSegment.from_mp3(file)
    data = dict()
    data['duration'] = int(song.duration_seconds * 1000)
    return(data)


def save_audio_to_file(audio, file):
    audio.export(file, format="mp3")

def mix_audio(audio1,audio2, position):
    return audio1.overlay(audio2, position)