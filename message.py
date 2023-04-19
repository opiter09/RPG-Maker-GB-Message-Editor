import os
import textwrap
import PySimpleGUI as psg

cont = 0
fileName = ""

def writeData(starts, texts, reading, thingy):
    global fileName
    new = open(fileName, "wb")
    new.close()
    new = open(fileName, "ab")
    new.write(reading[0:starts[0]])
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
        for j in range(starts[i + 1] - starts[i] - len(quote2)):
            new.write((0xAF).to_bytes(1, "little"))
    new.write(reading[starts[-1]:])
    new.close()
    
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
        if (reading[i] == 0):
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
    for num in starts[0:-1]:
        quote = ""
        for i in range(num, num + 64):
            if (reading[i] == 0xAF):
                break
            elif (reading[i] == 0xBF):
                quote = quote + "\n"
            else:
                try:
                    quote = quote + thingy[reading[i]]
                except:
                    quote = quote + " "
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

    layout = [
        [
            psg.Multiline(size = (18, 4), default_text = texts[cont], no_scrollbar = True, rstrip = False, key = "line"),
            psg.DropDown([str(texts.index(x)).zfill(3) + " " + x[0:16].replace("\n", "/") for x in texts], size = (23, 1),
                default_value = str(cont).zfill(3) + " " + texts[cont][0:16].replace("\n", "/"), enable_events = True, key = "drop")
        ],
        [ psg.Button("Save"), psg.Button("Write All"), psg.Button("Reload"), psg.Button("Run Game") ]
    ]

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
            texts[int(values["drop"][0:3])] = window["line"].get()[0:-1].upper()
            window["drop"].update(values = [str(texts.index(x)).zfill(3) + " " + x[0:16].upper().replace("\n", "/") for x in texts])
            window["drop"].update(set_to_index = int(values["drop"][0:3]))
            window["line"].update(window["line"].get().upper())
        elif (event == "Write All"):
            texts[int(values["drop"][0:3])] = window["line"].get()[0:-1].upper()
            window["drop"].update(values = [str(texts.index(x)).zfill(3) + " " + x[0:16].upper().replace("\n", "/") for x in texts])
            window["drop"].update(set_to_index = int(values["drop"][0:3]))
            window["line"].update(window["line"].get().upper())
            try:
                writeData(starts, texts, reading, thingy)
                psg.popup("Write complete!")
            except:
                psg.popup("Write failed!")
        elif (event == "Reload"):
            cont = int(values["drop"][0:3])
            break
        elif (event == "Run Game"):
            try:
                os.startfile(fileName[0:-4] + ".gbc")
            except:
                psg.popup("The game file cannot be found!")
        
    # Finish up by removing from the screen
    window.close()
    
while (cont > -1):
    run()