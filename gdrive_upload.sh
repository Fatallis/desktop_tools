#!/bin/bash
# Upload multiple files (uses gnu-parallel) and requires single_upload.sh

# Set IFS so that it won't consider spaces as entry separators.  Without this, spaces in file/folder names can make the loop go wacky.
IFS=$'\n'

# See if the Nautilus environment variable is empty
if [ -z $NAUTILUS_SCRIPT_SELECTED_FILE_PATHS ]; then
    # If it's blank, set it equal to $1
    NAUTILUS_SCRIPT_SELECTED_FILE_PATHS=$*
fi

ls $NAUTILUS_SCRIPT_SELECTED_FILE_PATHS | grep -E '\.*$' > tmp.tmp
cat tmp.tmp | parallel ~/.local/share/nemo/scripts/single_upload.sh {}

if [ $? -eq 0 ]; then
    rm tmp.tmp
else
    notify-send -t 5000 -i /usr/share/icons/gnome/32x32/status/info.png "Uploading Failed"
fi
