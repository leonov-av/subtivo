ffmpeg -i input/my_speech.mp4 -ar 22050  input/my_speech_input_track.mp3
ffmpeg -i audio_track.mp3 -i input/my_speech.mp4 -c copy final_video.mp4

Project structure:
Project
 -> audio_temp
 -> result
 -> sub
 url.txt