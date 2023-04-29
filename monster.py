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
    for i in range(0x2000, 0x2990, 34):
        if ((reading[i] != 0x80) and (reading[i + 1] != 0x80)):
            starts.append(i)

    thingy = {}
    f = open("rpg.tbl", "rt")
    for line in f.read().split("\n"):
        thingy[int(line[0:2], 16)] = line[3]
    f.close()
    f2 = open("firstFont.tbl", "rt")
    for line in f2.read().split("\n"):
        thingy[int(line[0:2], 16)] = line[3]
    f2.close()    
    thingy[0] = ""

    data = []
    for num in starts:
        quote = ""
        for i in range(num, num + 6):
            try:
                quote = quote + thingy[reading[i]]
            except:
                quote = quote + " "
        binList = []
        for i in range(num + 22, num + 26):
            integer = reading[i]
            small = bin(integer - (integer % 16))[2:]
            small = small[::-1]
            small = small + ("0" * (4 - len(small)))
            small2 = bin(integer % 16)[2:]
            small2 = small2[::-1]
            small2 = small2 + ("0" * (4 - len(small2)))
            small3 = small2 + small
            binList = binList + [ int(x) for x in small3 ]
        binList = binList + ([0] * (64 - len(binList)))
        # print(binList)
        data.append([quote, int.from_bytes(reading[(num + 22):(num + 26)], "little"), reading[num + 21] // 16] + binList)
    
    names = [str(i).zfill(3) + " " + data[i][0] for i in list(range(len(data)))]
    types = ["Attack", "Defend", "Assist", "Magic"]
    pages = ["Page 1", "Page 2", "Page 3", "Page 4", "Page 5"]
    layout = [
        [ psg.DropDown(names, enable_events = True, default_value = names[0], size = (12, 1), key = "monster") ],
        [
            psg.DropDown(types, enable_events = True, default_value = types[data[0][2]], key = "type"),
            psg.DropDown(pages, enable_events = True, default_value = pages[0], key = "page")
        ],
        [ psg.Button("Write All"), psg.Button("Reload"), psg.Button("Run Game") ],
    ]

    window = psg.Window("", layout, grab_anywhere = True, font = "-size 12").Finalize()

    while True:
        event, values = window.read()
        # See if user wants to quit or window was closed
        if (event == psg.WINDOW_CLOSED) or (event == "Quit"):
            cont = 1
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
            cont = 0
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
        
    # Finish up by removing from the screen
    window.close()

def loopFunc():
    while (cont != 1):
        run()