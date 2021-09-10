#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functions_tts
import functions_ffmpeg_wrapper
import json
import re
import os


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
    return ms + sec * 1000 + min * 60 * 1000 + hour * 60 * 60 * 1000


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
            n = 0
            text = ""
            for line in block.split("\n"):
                if n>=2:
                    text += line + " "
                n+=1
            analysed_block['text'] = text
        except:
            print("--- Except in analyse_block ")
            print(block)
            print("---")
            exit()
    return(analysed_block)


# def get_audio_file_duration(filepath):
#     return audio.analyse_audio_file(filepath)['duration']


def get_audio_file_duration(filepath):
    return functions_ffmpeg_wrapper.get_file_duration_sox(file_path=filepath)


def generate_audio_files_for_text_block(block, folder):
    analysed_block = analyse_block(block)
    print(json.dumps(analysed_block, indent=4))
    if 'number' in analysed_block:
        filepath = folder + str(analysed_block['number']) + ".wav"
        print(filepath)
        speed = 0
        status = "Unchecked file"
        while status != "OK":
            if not os.path.isfile(filepath):
                print("Generating \"" + analysed_block['text'] + "\"")
                print("Speed: " + str(speed))
                functions_tts.get_speech_audio_file_texttospeech(text=analysed_block['text'], speed=speed,
                                                                           file=filepath)
            if get_audio_file_duration(filepath) <= analysed_block['duration']:
                print("OK - " + str(get_audio_file_duration(filepath)) + "<="  + str(analysed_block['duration']))
                status = "OK"
            else:
                print("Bad File - " + str(get_audio_file_duration(filepath)) + "<="  + str(analysed_block['duration']))
                status = "Bad File"
                os.remove(filepath)
                speed += 1
            print("Status: " + status)


def generate_audio_files_for_all_text_blocks(blocks, audio_temp_folder):
    max_num = len(blocks)
    print("Generating audio files for text blocks")
    for block_id in range(0, max_num):
        print(str(block_id) + " from " + str(max_num))
        generate_audio_files_for_text_block(blocks[block_id], audio_temp_folder)


def generate_result_file(blocks, audio_temp_folder, result_audio_file):
    max_num = len(blocks)
    print("Making silence files")
    audio_track = ""
    previous_end = 0
    n = 1000000000000
    for block_id in range(0, max_num):
        print(block_id)
        analysed_block = analyse_block(blocks[block_id])
        if 'number' in analysed_block:
            print(analysed_block)
            print(str(block_id) + " from " + str(max_num))

            # Silence PRE
            silence = audio_temp_folder + "part_" + str(n) + "_0_silence_pre_" + str(analysed_block['number']) + ".wav"
            print(analysed_block['start'])
            print(previous_end)
            pre_silence_duration = analysed_block['start'] - previous_end
            if not os.path.isfile(silence):
                functions_ffmpeg_wrapper.create_silence_wav_sox(duration_s = pre_silence_duration,
                                                                file_path= silence)

            dur_file = get_audio_file_duration(silence)
            if dur_file != pre_silence_duration and dur_file != pre_silence_duration+1 and dur_file != pre_silence_duration-1:
                print("Silence file: " + str(dur_file))
                print("Silence file should be: " + str(pre_silence_duration))
                exit()

            # Silence for Phrase
            silence = audio_temp_folder + "silence_for_phrase_" + str(analysed_block['number']) + ".wav"
            phrase_silence_duration = analysed_block['end'] - analysed_block['start']
            if not os.path.isfile(silence):
                functions_ffmpeg_wrapper.create_silence_wav_sox(duration_s = phrase_silence_duration,
                                                                file_path= silence)

            # Phrase with Silence
            phrase_with_silence = audio_temp_folder + "part_" + str(n) + "_1_phrase_with_silence_" + str(analysed_block['number']) + ".wav"
            phrase = audio_temp_folder + str(analysed_block['number']) + ".wav"
            if not os.path.isfile(phrase_with_silence):
                functions_ffmpeg_wrapper.amix_files_in_list(silence,phrase,phrase_with_silence)

            dur1 = get_audio_file_duration(phrase_with_silence)
            dur2 = get_audio_file_duration(silence)

            if dur1 != dur2:
                print("ERROR! phrase_with_silence != silence")
                print(dur1)
                print(dur2)
                exit()

            previous_end = analysed_block['end']
            n += 1
    functions_ffmpeg_wrapper.concat_files_sox("projects/test/audio_temp/part*", result_audio_file)
    return audio_track


def make_audio_track(subtitles_file, audio_temp_folder, result_audio_file):
    blocks = get_text_blocks_from_subtitles(subtitles_file)
    check_blocks(blocks)
    generate_audio_files_for_all_text_blocks(blocks, audio_temp_folder)
    generate_result_file(blocks, audio_temp_folder, result_audio_file)


def process_project(project_name):
    subtitles_file = "projects/" + project_name + "/sub/" + "en.srt"
    audio_temp_folder = "projects/" + project_name + "/audio_temp/"
    result_audio_file = "projects/" + project_name + "/result/audio.wav"
    make_audio_track(subtitles_file, audio_temp_folder, result_audio_file)


def create_project(project_name):
    os.mkdir("projects/" + project_name)
    os.mkdir("projects/" + project_name + "/sub/")
    if not os.path.exists("projects/" + project_name + "/sub/" + "en.srt"):
        os.mknod("projects/" + project_name + "/sub/" + "en.srt")
    os.mkdir("projects/" + project_name + "/audio_temp/")
    os.mkdir("projects/" + project_name + "/result/")


project_name = "test"
if not os.path.isdir("projects/" + project_name):
    create_project(project_name)
    print("Edit " + "projects/" + project_name + "/sub/" + "en.srt")
    exit()

process_project(project_name)


