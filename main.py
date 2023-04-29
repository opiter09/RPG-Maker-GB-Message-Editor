import os
import PySimpleGUI as psg
import message
import monster

result = 0
layout = [ [psg.Button("Messages"), psg.Button("Monsters")] ]
window = psg.Window("", layout, grab_anywhere = True, font = "-size 12").Finalize()
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if (event == psg.WINDOW_CLOSED) or (event == "Quit"):
        break
    elif (event == "Messages"):
        result = 1
        break
    elif (event == "Monsters"):
        result = 2
        break

if (result == 1):
    message.loopFunc()
elif (result == 2):
    monster.loopFunc()
    