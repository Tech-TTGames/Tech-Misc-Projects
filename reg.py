import re
import pyperclip
from os import system

if input("Enter 1 to use current clipboard;\n") == '1':
    a = pyperclip.paste()
else:
    print("Ready! Please copy the text to filter.")
    a = pyperclip.waitForNewPaste()
if input('Enter 1 for HTML filtering:\n') != '1':
    l = re.findall(r'[0-9]{18}',a)
    chunks = [l[x:x+100] for x in range(0, len(l), 100)]
    if len(chunks) == 1:
        ls = ' '.join([str(elem) for elem in chunks[0]])
        pyperclip.copy(ls)
        print("Done! The filtered results are in your clipboard!")
        system('pause')
    else:
        for id in range(len(chunks)):
            ls = ' '.join([str(elem) for elem in chunks[id]])
            pyperclip.copy(ls)
            print(f"Done! The filtered result {id+1} out of {len(chunks)} is in your clipboard!")
            system('pause')
else:
    l = re.findall(r'(?s)(?<=<h3 class="post-title entry-title" itemprop="name">\r\n )(.*?)(?=</h3>)',a)
    ls = ' '.join([str(elem) for elem in l])
    print(ls)
    pyperclip.copy(ls)
    print("Done! The filtered results are in your clipboard!")
    system('pause')