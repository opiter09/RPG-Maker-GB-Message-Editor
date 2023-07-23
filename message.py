import os
import PySimpleGUI as psg

cont = 0
fileName = ""

def writeData(starts, originals, texts, reading, thingy):
    global fileName
    new = open(fileName, "wb")
    new.close()
    new = open(fileName, "ab")
    new.write(reading[0:starts[0]])
    shift = 0
    space = 0
    for i in range(len(starts) - 1):
        quote = texts[i].split("\n")[0:4]
        quote2 = ""
        for line in quote:
            if (len(line) >= 16):
                quote2 = quote2 + line[0:16]
            else:
                quote2 = quote2 + line + "/"
        if (quote2[-1] == "/"):
            quote2 = quote2[0:-1]
        for ch in quote2.upper():
            for k in thingy.keys():
                if (thingy[k] == ch):
                    new.write(k.to_bytes(1, "little"))
                    break
        new.write(reading[(starts[i] + len(originals[i])):starts[i + 1]])
        shift = shift + len(quote2) - len(originals[i])
        space = space + len(quote2)
    if (shift < 0):
        for i in range(abs(shift)):
            new.write((0xAF).to_bytes(1, "little"))
        new.write(reading[starts[-1]:])
    elif (shift > 0):
        new.write(reading[min(starts[-1] + shift, 0x6000):])
    else:
        new.write(reading[starts[-1]:])
    new.close()
    psg.popup("Write complete!" + "\n" + str(0x6000 - 0x2F57 - space) + " bytes remaining!", font = "-size 12")
    
def run():
    global cont
    global fileName

    for root, dirs, files in os.walk("./"):
        for file in files:
            if (file.lower().endswith(".sav") == True) and (os.stat(os.path.join(root, file)).st_size == 0x8000):
                fileName = file
                opening = open(file, "rb")
                reading = opening.read()
                opening.close()
                break

    starts = []
    for i in range(0x2F57, 0x8000):
        if ((reading[i] == 0) and (reading[i + 1] == 0)):
            starts.append(i)
            break
        elif ((reading[i] == 0xAF) and (reading[i + 1] != 0xAF) and (reading[i + 1] != 0)):
            starts.append(i + 1)

    thingy = {}
    f = open("rpg.tbl", "rt")
    for line in f.read().split("\n"):
        thingy[int(line[0:2], 16)] = line[3]
    f.close()

    texts = []
    originals = []
    temp = starts[0:-1].copy()
    for num in temp:
        forward = 0
        quote = ""
        for i in range(num, num + 64):
            if (reading[i] == 0xAF):
                break
            elif (reading[i] < 0x80):
                starts.remove(num)
                forward = 1
                break
            elif (reading[i] == 0xBF):
                quote = quote + "\n"
            else:
                try:
                    quote = quote + thingy[reading[i]]
                except:
                    quote = quote + " "
        if (forward == 0):
            originals.append(quote)
            quote = quote.split("\n")
            quote2 = ""
            for line in quote:
                if (len(line) > 16):
                    for i in range(0, len(line), 16):
                        quote2 = quote2 + line[i:(i + 16)] + "\n"
                else:
                    quote2 = quote2 + line + "\n"
            if (quote2[-1] == "\n"):
                quote2 = quote2[0:-1]
            texts.append(quote2)
    
    if (len(texts) == 0):
        psg.popup("No suitable strings were found!", font = "-size 12")
        cont = -1
        return

    lengths = [0, 0, 0, 0]
    for i in range(4):
        try:
            lengths[i] = len(texts[cont].upper().split("\n")[i])
        except:
            pass
    lString = str(lengths[0])[0:2].zfill(2) + " / " + str(lengths[1])[0:2].zfill(2) + " / " + str(lengths[2])[0:2].zfill(2) + " / " + str(lengths[3])[0:2].zfill(2)

    subLayout = [
        [
            psg.Multiline(size = (20, 4), default_text = texts[cont], no_scrollbar = True, rstrip = False, enable_events = True, key = "line"),
            psg.DropDown([str(texts.index(x)).zfill(3) + " " + x[0:16].replace("\n", "/") for x in texts], size = (23, 1),
                default_value = str(cont).zfill(3) + " " + texts[cont][0:16].replace("\n", "/"), enable_events = True, key = "drop")
        ],
        [ psg.Button("Save"), psg.Button("Write All"), psg.Button("Reload"), psg.Button("Run Game"), psg.Text(lString, key = "show") ],
        [ psg.Text("Replace"), psg.Input(size = 10, key = "one"), psg.Text("with"), psg.Input(size = 10, key = "two"), psg.Button("Replace All") ]
    ]
    charMap = "[ = open quotes\n\
] = close quotes\n\
; = middle dot\n\
> = ellipsis\n\
@ = heart\n\
$ = eighth-note\n\
& = sixteenth-notes\n\
# = droplet/tear\n\
* = open period\n\
` = comma-thing"
    layout = [ [psg.Column(subLayout), psg.Column([[psg.Text(charMap)]])] ]

    window = psg.Window("", layout, grab_anywhere = True, font = "-size 12").Finalize()
    window["line"].Widget.configure(wrap = "none")

    while True:
        event, values = window.read()
        # See if user wants to quit or window was closed
        if (event == psg.WINDOW_CLOSED) or (event == "Quit"):
            cont = -1
            break
        elif (event == "drop"):
            window["line"].update(texts[int(values["drop"][0:3])])
        elif (event == "Save"):
            temp = window["line"].get().upper()
            for ch in window["line"].get().upper():
                if ((ch not in thingy.values()) and (ch != "\n")):
                    temp = temp.replace(ch, "")
            quote = ""
            for line in temp[0:-1].upper().split("\n")[0:4]:
                if (len(line) >= 16):
                    quote = quote + line[0:16] + "\n"
                else:
                    quote = quote + line + "\n"
            if (quote[-1] == "\n"):
                quote = quote[0:-1]
            texts[int(values["drop"][0:3])] = quote
            window["drop"].update(values = [str(texts.index(x)).zfill(3) + " " + x[0:16].upper().replace("\n", "/") for x in texts])
            window["drop"].update(set_to_index = int(values["drop"][0:3]))
            window["line"].update(quote)
        elif (event == "Write All"):
            temp = window["line"].get().upper()
            for ch in window["line"].get().upper():
                if ((ch not in thingy.values()) and (ch != "\n")):
                    temp = temp.replace(ch, "")
            quote = ""
            for line in temp[0:-1].upper().split("\n")[0:4]:
                if (len(line) >= 16):
                    quote = quote + line[0:16] + "\n"
                else:
                    quote = quote + line + "\n"
            if (quote[-1] == "\n"):
                quote = quote[0:-1]
            texts[int(values["drop"][0:3])] = quote
            window["drop"].update(values = [str(texts.index(x)).zfill(3) + " " + x[0:16].upper().replace("\n", "/") for x in texts])
            window["drop"].update(set_to_index = int(values["drop"][0:3]))
            window["line"].update(quote)
            try:
                writeData(starts, originals, texts, reading, thingy)
            except:
                psg.popup("Write failed!", font = "-size 12")
        elif (event == "Reload"):
            cont = int(values["drop"][0:3])
            break
        elif (event == "Run Game"):
            try:
                os.startfile(fileName[0:-4] + ".gbc")
            except:
                psg.popup("The game file cannot be found!", font = "-size 12")
        elif (event == "Replace All"):
            bad = 0
            for ch in values["two"].upper():
                if (ch not in thingy.values()):
                    psg.popup("Invalid character detected!", font = "-size 12")
                    bad = 1
                    break
            if (bad == 1):
                continue
            total = 0
            for i in range(len(texts)):
                if (values["one"].upper() in texts[i]):
                    total = total + 1
                    texts[i] = texts[i].replace(values["one"].upper(), values["two"].upper())
                    quote = ""
                    for line in texts[i].upper().split("\n")[0:4]:
                        if (len(line) >= 16):
                            quote = quote + line[0:16] + "\n"
                        else:
                            quote = quote + line + "\n"
                    if (quote[-1] == "\n"):
                        quote = quote[0:-1]
                    texts[i] = quote
            window["line"].update(texts[int(values["drop"][0:3])])
            window["drop"].update(values = [str(texts.index(x)).zfill(3) + " " + x[0:16].upper().replace("\n", "/") for x in texts])
            window["drop"].update(set_to_index = int(values["drop"][0:3]))
            psg.popup("Text in " + str(total) + " message(s) has been replaced!", font = "-size 12") 

        lengths = [0, 0, 0, 0]
        for i in range(4):
            try:
                lengths[i] = len(window["line"].get()[0:-1].upper().split("\n")[i])
            except:
                pass
        window["show"].update(str(lengths[0])[0:2].zfill(2) + " / " + str(lengths[1])[0:2].zfill(2) + " / " + str(lengths[2])[0:2].zfill(2) + " / " + str(lengths[3])[0:2].zfill(2))
        
    # Finish up by removing from the screen
    window.close()
    
while (cont > -1):
    run()