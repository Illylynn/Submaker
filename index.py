from visual import create_visual
from audio import create_audio
from affsmaker import generate_affs

from pick import pick

import os

import win32clipboard as clip
import win32con
from io import BytesIO

topic = input("Sub topic:")

title = "Pick a sub type: "
options = ["Visual", "Audio"]
option, index = pick(options,title, indicator = "=>", default_index=0)

if index == 1:
    title2 = "Pick a background file: "
    options2 = ["Silence"] + os.listdir('Background')

    option2, index2 = pick(options2,title2, indicator = "=>", default_index=0)
    
    file_name = input("Export file name: ")

affs = generate_affs(topic)

if index == 0: 
    
    flattened_affs = []
    
    for aff in affs:
        for aff2 in aff.split("|"):
            flattened_affs.append(aff2)
    
    image = create_visual("copy", flattened_affs)
    
    # Prevent weird progress bar glitch
    print()

    image.show()

    output = BytesIO()
    image.convert('RGB').save(output, 'BMP')
    data = output.getvalue()[14:]
    output.close()
    clip.OpenClipboard()
    clip.EmptyClipboard()
    clip.SetClipboardData(win32con.CF_DIB, data)
    clip.CloseClipboard()
else:
    affs = "|".join(affs)
    
    create_audio(affs, file_name, index2, option2)