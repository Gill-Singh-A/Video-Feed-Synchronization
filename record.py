#! /usr/bin/env python3

import cv2, pickle
from pathlib import Path
from datetime import date
from optparse import OptionParser
from colorama import Fore, Back, Style
from time import strftime, localtime, time

status_color = {
    '+': Fore.GREEN,
    '-': Fore.RED,
    '*': Fore.YELLOW,
    ':': Fore.CYAN,
    ' ': Fore.WHITE
}

default_camera = 0
show_camera_feed = False

def display(status, data, start='', end='\n'):
    print(f"{start}{status_color[status]}[{status}] {Fore.BLUE}[{date.today()} {strftime('%H:%M:%S', localtime())}] {status_color[status]}{Style.BRIGHT}{data}{Fore.RESET}{Style.RESET_ALL}", end=end)

def get_arguments(*args):
    parser = OptionParser()
    for arg in args:
        parser.add_option(arg[0], arg[1], dest=arg[2], help=arg[3])
    return parser.parse_args()[0]

def makeFolder(folder_name):
    cwd = Path.cwd()
    folder = cwd / folder_name
    folder.mkdir(exist_ok=True)
    frame_folder = folder / "frames"
    frame_folder.mkdir(exist_ok=True, parents=True)

if __name__ == "__main__":
    arguments = get_arguments(('-c', "--camera", "camera", f"Index of Camera Device to use (Default Index={default_camera})"),
                              ('-s', "--show", "show", f"Show the Camera Feed (True/False, Default={show_camera_feed})"),
                              ('-w', "--write", "write", "Folder Name to store the Frames and Time Mappings (default=current data and time)"))
    if not arguments.camera:
        arguments.camera = default_camera
    else:
        arguments.camera = int(arguments.camera)
    if not arguments.write:
        arguments.write = f"{date.today()} {strftime('%H_%M_%S', localtime())}"
    if not arguments.show:
        arguments.show = show_camera_feed
    elif arguments.show == "True":
        arguments.show = True
    display(':', f"Making {Back.MAGENTA}{arguments.write}{Back.RESET} Folder")
    makeFolder(arguments.write)
    display('+', f"Made {Back.MAGENTA}{arguments.write}{Back.RESET} Folder")
    display(':', f"Starting Camera Index {Back.MAGENTA}{arguments.camera}{Back.RESET}")
    video_capture = cv2.VideoCapture(arguments.camera)
    time_mapping = {}
    frame_index = 0
    try:
        while True:
            t1 = time()
            ret, frame = video_capture.read()
            t2 = time()
            if ret:
                cv2.imwrite(f"{arguments.write}/frames/{frame_index}.jpg", frame)
                time_mapping[(t1+t2)/2] = frame_index
                frame_index += 1
                display('+', f"Frames Recorded = {Back.MAGENTA}{frame_index}{Back.RESET}", start='\r', end='')
                if arguments.show:
                    cv2.imshow("Camera Feed", frame)
                    cv2.waitKey(1)
            else:
                display('-', f"Error Reading Frame from Camera Index {Back.MAGENTA}{arguments.camera}{Back.RESET}", start='\r')
    except KeyboardInterrupt:
        display('*', f"Detected Keyboard Interrupt...", start='\n')
        display(':', "Exiting")
    cv2.destroyAllWindows()
    display(':', f"Dumping Time Mappings to {Back.MAGENTA}{arguments.write}/time_mapping{Back.RESET}")
    with open(f"{arguments.write}/time_mapping", 'wb') as file:
        pickle.dump(time_mapping, file)
    display('+', f"Dumped Time Mappings to {Back.MAGENTA}{arguments.write}/time_mapping{Back.RESET}")