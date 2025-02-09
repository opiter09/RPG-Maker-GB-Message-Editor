# RPG-Maker-GB-Message-Editor
This small code allows you to edit existing messages in the fan-translation of the game RPG Tsukuru GB with an actual keyboard. Although it is a smaller ROM (and thus contains less assets) than its sequel, this game's fan translation
is far more complete, so that is why I have chosen to target it.

As far as operating the code, there are more than a few quirks:
- Instead of making you choose a save file, the program automatically selects the first .sav file in its folder of exactly 32,768 bytes. So try not to have more than
  one in the program's folder
- You can only edit messages that exist already in the save. I do not know how message space is allocated, and I could not even find the pointers to them, so just
  deal with it (and make sure to make each message's original text distinguishable from each other)
- Although messages are only shown in uppercase, you can type in any case you want; it will be converted automatically
- The quotes are "Japanese-style" with the right-angle things, so you must enter them in the editor using square brackets ("\[" and "\]")
- The other special characters are entered as follows:
  - ; = middle dot
  - \> = ellipsis
  - @ = heart
  - $ = eighth-note
  - & = sixteenth-notes
  - \# = droplet (tear?)
  - \* = open period
- Each message can only have four lines, each up to 16 characters in length. I don't know how to enforce this in the editor, so it just automatically truncates
  when saving and writing. Please note the four numbers next to the row of buttons, however--they show the lengths of each line in the current message
- The "Save" button saves the text into memory, so that if you switch to another one and come back, it will be the same. The "Write All" button, on the other hand,
  actually writes it (and the other messages) into the save file
- The "Run Game" button opens the game with the same name as the opened save file in the default app (i.e. what happens when you double-click it) using
  os.startfile(). I am given to understand that this function only works on Windows, so you may have to forgo this small convenience
- The find-and-replace does not try to word wrap or anything like that, so be careful if you try to replace a shorter phrase with a longer one. Also, it affects all
  instances in all messages, not just all instances in the current message

Finally, if you are new to downloading things off of GitHub, know that you may download these files by pressing the green "Code" button, and then selecting "Download ZIP."
  
# Note
This more applies to editing things in-game, but for all messages you should use the *third* font, the one with only uppercase letters. Otherwise, it will render
as Japanese in-game for some reason. For spell names, monster names, etc. you can use the first font just fine, especially since it matches the battle messages. Finally,
for the Title of your game you must use the third font as well.

#  Credits
- Thanks to PySimpleGUI, for making it trivial to make a GUI (and then an .exe) for this
- Thanks to MageCraft Translations, for fan-translating this game over 20 years ago (https://www.romhacking.net/translations/42/).
  However, do note that this fan-translation has been superseded by my own (https://romhackplaza.org/translations/rpg-maker-gb-english-translation-gbc/)
