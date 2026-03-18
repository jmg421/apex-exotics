#!/bin/bash
# Refresh Chrome and click to activate sound
osascript -e 'tell application "System Events" to keystroke "r" using {command down, shift down}'
sleep 2
cliclick c:960,540
sleep 2
cliclick c:960,540
