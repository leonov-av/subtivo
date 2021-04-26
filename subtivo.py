#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import tts
from mutagen.mp3 import MP3
import os
import json
import ffmpeg_wrapper


def get_text_blocks_from_subtitles(file):
    f = open(file,"r")
    content = f.read()
    f.close()
    content = re.sub("\r","",content)
    blocks = list()
    for block in content.split("\n\n"):
        blocks.append(block)
    return blocks


def check_blocks(blocks):
    for block in blocks:
        if len(block.split("\n")) != 3:
            print("---")
            print("Error: remove new lines:")
            print(block)
        for line in re.sub("^[0-9]*\n", "", block).split("\n"):
            if not "-->" in line:
                if not re.findall("[\.!\?:]$", line):
                    print("---")
                    print("Error: wrong ending:")
                    print(block)


def get_mil_seconds(line):
    ms = int(line.split(",")[1])
    hour = int(line.split(",")[0].split(":")[0])
    min = int(line.split(",")[0].split(":")[1])
    sec = int(line.split(",")[0].split(":")[2])
    return ms + sec * 1000 + min * 60 * 1000 + hour * 24 * 60 * 1000


def analyse_block(block):
    analysed_block = dict()
    if len(block.split("\n")) > 2:
        try:
            analysed_block['number'] = block.split("\n")[0]
            analysed_block['time_line'] = block.split("\n")[1]
            analysed_block['text'] = block.split("\n")[0]
            analysed_block['start'] = get_mil_seconds(analysed_block['time_line'].split(" --> ")[0])
            analysed_block['end'] = get_mil_seconds(analysed_block['time_line'].split(" --> ")[1])
            analysed_block['duration'] = analysed_block['end'] - analysed_block['start']
            analysed_block['text'] = block.split("\n")[2]
        except:
            print("--- Except in analyse_block ")
            print(block)
            print("---")
            exit()
    return(analysed_block)


# def get_audio_file_duration(filepath):
#     return audio.analyse_audio_file(filepath)['duration']


def get_audio_file_duration(filepath):
    return int(MP3(filepath).info.length)


def generate_audio_files_for_text_block(block, folder):
    analysed_block = analyse_block(block)
    print(json.dumps(analysed_block, indent=4))
    if 'number' in analysed_block:
        filepath = folder + str(analysed_block['number']) + ".mp3"
        print(filepath)
        speed = 0
        status = "Unchecked file"
        while status != "OK":
            if not os.path.isfile(filepath):
                print("Generating \"" + analysed_block['text'] + "\"")
                print("Speed: " + str(speed))
                tts.get_speech_audio_file_texttospeech_microsoft(text=analysed_block['text'], speed=speed,
                                          file=folder + str(analysed_block['number']) + ".mp3")
            if get_audio_file_duration(filepath) <= analysed_block['duration']:
                status = "OK"
            else:
                status = "Bad File - " + str(get_audio_file_duration(filepath)) + "<="  + str(analysed_block['duration'])
                os.remove(filepath)
                speed += 1
            print("Status: " + status)


def generate_audio_files_for_all_text_blocks(blocks, audio_temp_folder):
    max_num = len(blocks)
    print("Generating audio files for text blocks")
    for block_id in range(0, max_num):
        print(str(block_id) + " from " + str(max_num))
        generate_audio_files_for_text_block(blocks[block_id], audio_temp_folder)


def generate_silence_files(blocks):
    max_num = len(blocks)
    print("Making silence files")
    audio_track = ""
    previous_block_end = 0
    for block_id in range(0, max_num):
        print(block_id)
        analysed_block = analyse_block(blocks[block_id])
        if 'number' in analysed_block:
            print(analysed_block)
            print(str(block_id) + " from " + str(max_num))
            if not os.path.isfile(audio_temp_folder + "silence_pre_" + str(analysed_block['number']) + ".mp3"):
                silence_filepath = audio_temp_folder + "silence_pre_" + str(analysed_block['number']) + ".mp3"
                ffmpeg_wrapper.create_silence_mp3(duration_s = analysed_block['start'] - previous_block_end,
                                                  mp3_file = silence_filepath)
            if not os.path.isfile(audio_temp_folder + "silence_post_" + str(analysed_block['number']) + ".mp3"):
                silence_filepath = audio_temp_folder + "silence_post_" + str(analysed_block['number']) + ".mp3"
                post_silence_duration = analysed_block['end'] - analysed_block['start'] - \
                                        get_audio_file_duration(audio_temp_folder + str(analysed_block['number']) + ".mp3")
                ffmpeg_wrapper.create_silence_mp3(duration_s = post_silence_duration,
                                                  mp3_file = silence_filepath)
            previous_block_end = analysed_block['end']
    return audio_track


def generate_file_list(blocks):
    max_num = len(blocks)
    print("Making file list")
    file_list = list()
    for block_id in range(0, max_num):
        analysed_block = analyse_block(blocks[block_id])
        if 'number' in analysed_block:
            if os.path.isfile(audio_temp_folder + "silence_pre_" + str(analysed_block['number']) + ".mp3"):
                silence_filepath = "silence_pre_" + str(analysed_block['number']) + ".mp3"
                file_list.append("file " + silence_filepath)
            if os.path.isfile(audio_temp_folder + str(analysed_block['number']) + ".mp3"):
                filepath = str(analysed_block['number']) + ".mp3"
                file_list.append("file " + filepath)
            if os.path.isfile(audio_temp_folder + "silence_post_" + str(analysed_block['number']) + ".mp3"):
                silence_filepath = "silence_post_" + str(analysed_block['number']) + ".mp3"
                file_list.append("file " + silence_filepath)
    f = open(audio_temp_folder + "file_list.txt","w")
    f.write("\n".join(file_list))
    f.close()



def make_audio_track(subtitles_file, audio_temp_folder, result_audio_file):
    blocks = get_text_blocks_from_subtitles(subtitles_file)
    check_blocks(blocks)
    generate_audio_files_for_all_text_blocks(blocks, audio_temp_folder)
    generate_silence_files(blocks)
    generate_file_list(blocks)
    ffmpeg_wrapper.concat_files_in_list(audio_temp_folder + "file_list.txt", result_audio_file)


project_name = "kau"
subtitles_file = "projects/" + project_name + "/sub/" + "en.srt"
audio_temp_folder = "projects/" +  project_name + "/audio_temp/"
result_audio_file =  "projects/" + project_name + "/result/audio.mp3"
make_audio_track(subtitles_file, audio_temp_folder, result_audio_file)



# subtitles_file = "subtitles_eng.srt"
# audio_temp_folder = "audio/phdays/"
# audio_track = get_audio_track(subtitles_file, audio_temp_folder)
# audio.save_audio_to_file(audio_track,"generated_audio_track.mp3")

# Combine with existing audio
# audio_track = audio.mix_audio(audio.get_audio_from_file("input/my_speech_input_track.mp3"), audio_track, 2000)
# audio.save_audio_to_file(audio_track,"audio_track.mp3")

# Making result video
# os.remove("final_video.mp4")
# os.system("ffmpeg -i audio_track.mp3 -i input/my_speech.mp4 -c copy final_video.mp4")
