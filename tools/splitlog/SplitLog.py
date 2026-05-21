import os
import re
import shutil
import sys

if len(sys.argv) < 2:
    print("Usage: python3 SplitLog.py <game_root>")
    sys.exit(1)

game_root = sys.argv[1]
log_path = os.path.join(game_root, "starsector.log")
folder_path = "public/data"
os.makedirs(folder_path, exist_ok=True)
pattern = re.compile(r"export_(\S+)_export_(.+)$")
with open(log_path, "r") as file:
    for line in file:
        match = pattern.search(line)
        if match:
            filename = os.path.join(folder_path, match.group(1) + ".json")
            content = match.group(2)
            try:
                with open(filename, "w") as outfile:
                    outfile.write(content)
                print(f'File "{filename}" saved successfully.')
            except IOError as e:
                print(f'Error saving file "{filename}": {e}')