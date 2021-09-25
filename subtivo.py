#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functions_tts
import functions_audio_wrappers
import json
import re
import os
import shutil
import getopt, sys


def get_text_blocks_from_subtitles(file):
    f = open(file,"r")
    content = f.read()
    f.close()
    content = re.sub("\r","",content)
    blocks = list()
    for block in content.split("\n\n"):
        block = re.sub("<[^>]*>","",block)
        block = re.sub("\{[^}]*}", "", block)
        block = re.sub("^\!", "", block)
        blocks.append(block)
    return blocks


def check_blocks(blocks):
    for block in blocks:
        if len(block.split("\n")) != 3:
            print("---")
            print("Error: remove new lines:")
            print(block)
            exit()
        for line in re.sub("^[0-9]*\n", "", block).split("\n"):
            if not "-->" in line:
                if not re.findall("[\.!\?:]$", line):
                    print("---")
                    print("Error: wrong ending:")
                    print(block)
                    exit()


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
            analysed_block['text'] = re.sub("^! *", "", analysed_block['text'])
        except:
            print("--- Except in analyse_block ")
            print(block)
            print("---")
            exit()
    return(analysed_block)


def get_audio_file_duration(filepath):
    return functions_audio_wrappers.get_file_duration_sox(file_path=filepath)


def generate_audio_files_for_text_block(analysed_block, folder):
    print(json.dumps(analysed_block, indent=4))
    if 'number' in analysed_block and analysed_block['text'] != "" and len(re.sub(" ","",analysed_block['text'])) > 1:
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


def generate_audio_files_for_text_blocks(blocks, audio_temp_folder, result_audio_file):
    max_num = len(blocks)
    audio_track = ""
    previous_end = 0
    n = 1000000000000
    for block_id in range(0, max_num):
        print(str(block_id) + " from " + str(max_num))
        analysed_block = analyse_block(blocks[block_id])
        print(analysed_block)
        if 'number' in analysed_block:
            generate_audio_files_for_text_block(analysed_block, audio_temp_folder)
            print(str(block_id) + " from " + str(max_num))
            # Silence PRE
            pre_silence = audio_temp_folder + "part_" + str(n) + "_0_silence_pre_" + str(analysed_block['number']) + ".wav"
            print(analysed_block['start'])
            print(previous_end)
            pre_silence_duration = analysed_block['start'] - previous_end
            if not os.path.isfile(pre_silence):
                functions_audio_wrappers.create_silence_wav_sox(duration_s = pre_silence_duration,
                                                                file_path= pre_silence)

            pre_silence_duration_from_file = get_audio_file_duration(pre_silence)
            if pre_silence_duration_from_file != pre_silence_duration and \
                    pre_silence_duration_from_file != pre_silence_duration+1 and\
                    pre_silence_duration_from_file != pre_silence_duration-1:
                print("ERROR! pre_silence_duration_from_file != pre_silence_duration")
                print("pre_silence_duration_from_file: " + str(pre_silence_duration_from_file))
                print("pre_silence_duration: " + str(pre_silence_duration))
                exit()

            # Silence for Phrase
            phrase_silence = audio_temp_folder + "silence_for_phrase_" + str(analysed_block['number']) + ".wav"
            phrase_silence_duration = analysed_block['end'] - analysed_block['start']
            if not os.path.isfile(phrase_silence):
                functions_audio_wrappers.create_silence_wav_sox(duration_s = phrase_silence_duration,
                                                                file_path= phrase_silence)

            # Phrase with Silence
            phrase_with_silence = audio_temp_folder + "part_" + str(n) + "_1_phrase_with_silence_" + str(analysed_block['number']) + ".wav"
            phrase = audio_temp_folder + str(analysed_block['number']) + ".wav"
            if not os.path.isfile(phrase_with_silence):
                functions_audio_wrappers.amix_files_in_list(phrase_silence, phrase, phrase_with_silence)

            phrase_with_silence_duration_from_file = get_audio_file_duration(phrase_with_silence)
            phrase_silence_duration_from_file = get_audio_file_duration(phrase_silence)

            if phrase_with_silence_duration_from_file != phrase_silence_duration_from_file:
                print("ERROR! phrase_with_silence_duration_from_file != phrase_silence_duration_from_file")
                print("phrase_with_silence_duration_from_file: " + phrase_with_silence_duration_from_file)
                print("phrase_silence_duration_from_file: " + phrase_silence_duration_from_file)
                exit()

            previous_end = analysed_block['end']
            n += 1
    functions_audio_wrappers.concat_files_sox(audio_temp_folder + "part*", result_audio_file)
    return audio_track


def make_audio_track(subtitles_file, audio_temp_folder, result_audio_file):
    blocks = get_text_blocks_from_subtitles(subtitles_file)
    # check_blocks(blocks)
    generate_audio_files_for_text_blocks(blocks, audio_temp_folder, result_audio_file)


def process_project(project_name):
    subtitles_file = "projects/" + project_name + "/input/" + "en.srt"
    audio_temp_folder = "projects/" + project_name + "/audio_temp/"
    result_audio_file = "projects/" + project_name + "/result/audio.wav"
    make_audio_track(subtitles_file, audio_temp_folder, result_audio_file)


def create_project(project_name):
    os.mkdir("projects/" + project_name)
    os.mkdir("projects/" + project_name + "/input/")
    if not os.path.exists("projects/" + project_name + "/input/" + "en.srt"):
        os.mknod("projects/" + project_name + "/input/" + "en.srt")
    os.mkdir("projects/" + project_name + "/audio_temp/")
    os.mkdir("projects/" + project_name + "/result/")


mode = "default"
# Remove 1st argument from the
# list of command line arguments
argumentList = sys.argv[1:]

# Options
options = "hi:o:p:m:"

# Long options
long_options = ["help", "input", "output", "project", "mode"]

try:
    # Parsing argument
    arguments, values = getopt.getopt(argumentList, options, long_options)

    # checking each argument
    for currentArgument, currentValue in arguments:

        if currentArgument in ("-h", "--Help"):
            print("Displaying Help")

        elif currentArgument in ("-i", "--input"):
            input_file = currentValue

        elif currentArgument in ("-o", "--output"):
            output_file = currentValue

        elif currentArgument in ("-p", "--project"):
            project = currentValue

        elif currentArgument in ("-m", "--mode"):
            mode = currentValue

except getopt.error as err:
    # output error, and return with an error code
    print(str(err))


# project_name = "canada_uni"
# input_file = "en.srt"
# output_file = "audio.wav"

print("mode: " + mode)
print("project: " + project)
print("input_file: " + input_file)
print("output_file: " + output_file)

if mode == "clear_temp_data":
    if os.path.isdir("projects/" + project):
        shutil.rmtree("projects/" + project)


if not os.path.isdir("projects/" + project):
    create_project(project)
    shutil.copyfile(input_file, "projects/" + project + "/input/" + "en.srt")

process_project(project)
shutil.copyfile("projects/" + project + "/result/" + "audio.wav", output_file)

if mode == "clear_temp_data":
    shutil.rmtree("projects/" + project)

print("File " + output_file + " is ready")


