#!/bin/bash
# Convert a pdf file to text and reformat the text in order to make it easer to read with gTTS.

# Set IFS so that it won't consider spaces as entry separators.  Without this, spaces in file/folder names can make the loop go wacky.
IFS=$'\n'

# See if the Nautilus environment variable is empty
if [ -z $NAUTILUS_SCRIPT_SELECTED_FILE_PATHS ]; then
    # If it's blank, set it equal to $1
    NAUTILUS_SCRIPT_SELECTED_FILE_PATHS=$1
fi

pdftotext -raw -enc UTF-8 -nopgbrk "$NAUTILUS_SCRIPT_SELECTED_FILE_PATHS"
gnome-terminal -x /home/fatallis/.local/share/nemo/scripts/format.py "${NAUTILUS_SCRIPT_SELECTED_FILE_PATHS%.*}.txt"
rm "${NAUTILUS_SCRIPT_SELECTED_FILE_PATHS%.*}.txt"

if [ $? -eq 0 ]; then
    notify-send -t 5000 -i /usr/share/icons/gnome/32x32/status/info.png "OK_${NAUTILUS_SCRIPT_SELECTED_FILE_PATHS%.*}.txt Created"
else
    notify-send -t 5000 -i /usr/share/icons/gnome/32x32/status/info.png "OK_${NAUTILUS_SCRIPT_SELECTED_FILE_PATHS%.*}.txt Failed"
fi

