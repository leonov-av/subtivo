import requests
from googletrans import Translator

def print_translated_blocks(blocks):
    for block in blocks:
        text = block.split("\r\n")[2]
        #responce = requests.get("https://translate.google.com/#ru/en/" + text)
        #print(responce.text)
        translator = Translator()
        translation = translator.translate(text)
        print(block.split("\r\n")[0])
        print(block.split("\r\n")[1])
        print(translation.text)
        print("")