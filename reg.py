"""Regex discord IDs"""
from os import system

import re
import pyperclip

if input("Enter 1 to use current clipboard;\n") == '1':
    a = pyperclip.paste()
else:
    print("Ready! Please copy the text to filter.")
    a = pyperclip.waitForNewPaste()
    l = re.findall(r'[0-9]{18}', a)
    chunks = [l[x:x+100] for x in range(0, len(l), 100)]
    if len(chunks) == 1:
        result = ' '.join([str(elem) for elem in chunks[0]])
        pyperclip.copy(result)
        print("Done! The filtered results are in your clipboard!")
        system('pause')
    else:
        for o in range(len(chunks)):
            result = ' '.join([str(elem) for elem in chunks[o]])
            pyperclip.copy(result)
            print(f"Done! The filtered result {o+1} out of {len(chunks)} is in your clipboard!")
            system('pause')
