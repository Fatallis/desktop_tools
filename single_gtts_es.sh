#!/bin/bash
# Convert a spanish text file (txt) to an mp3 file with gTTs (https://github.com/pndurette/gTTS)

# Set IFS so that it won't consider spaces as entry separators.  Without this, spaces in file/folder names can make the loop go wacky.
IFS=$'\n'

# See if the Nautilus environment variable is empty
if [ -z $NAUTILUS_SCRIPT_SELECTED_FILE_PATHS ]; then
    # If it's blank, set it equal to $1
    NAUTILUS_SCRIPT_SELECTED_FILE_PATHS=$1
fi

gtts-cli -f "$NAUTILUS_SCRIPT_SELECTED_FILE_PATHS" -o "${NAUTILUS_SCRIPT_SELECTED_FILE_PATHS%.*}.mp3" -l 'es-us'


if [ $? -eq 0 ]; then
    notify-send -t 5000 -i /usr/share/icons/gnome/32x32/status/info.png "${NAUTILUS_SCRIPT_SELECTED_FILE_PATHS%.*}.mp3 Created"
else
    notify-send -t 5000 -i /usr/share/icons/gnome/32x32/status/info.png "${NAUTILUS_SCRIPT_SELECTED_FILE_PATHS%.*}.mp3 Failed"
fi

