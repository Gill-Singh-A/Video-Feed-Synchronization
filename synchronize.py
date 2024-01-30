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

if __name__ == "__main__":
    arguments = get_arguments(('-f', "--feed", "feed", "Name of Feed Folders with time mappings (seperated by ',')"),
                              ('-w', "--write", "write", "Folder Name to store the Final Video Files"))
    if not arguments.feed:
        display('-', f"Please provide Name of Feed Folders with time mappings")
        exit(0)
    else:
        arguments.feed = arguments.feed.split(',')
    time_mappings = {}
    display(':', f"Loading Time Mappings")
    T1 = time()
    not_found = []
    for video_feed_folder in arguments.feed:
        display('*', f"\t{video_feed_folder}", end='')
        t1 = time()
        with open(f"{video_feed_folder}/time_mapping", 'rb') as file:
            time_mappings[video_feed_folder] = pickle.load(file)
        t2 = time()
        if t2 == t1:
            print(f" => {Back.MAGENTA}{t2-t1} seconds{Back.RESET}")
        else:
            print()
    T2 = time()
    display('+', f"Loaded Time Mappings")
    display(':', f"\tTime Taken     = {Back.MAGENTA}{T2-T1} seconds{Back.RESET}")
    display(':', f"\tTimings Loaded = {Back.MAGENTA}{len(arguments.feed)}{Back.RESET}")
    if T2 != T1:
        display(':', f"\tRate           = {Back.MAGENTA}{len(arguments.feed)/(T2-T1):.2f} timings/second{Back.RESET}")
    start_timings = [list(time_map.keys())[0] for time_map in time_mappings.values()]
    end_timings = [list(time_map.keys())[-1] for time_map in time_mappings.values()]
    min_start_time = min(start_timings)
    max_start_time = max(start_timings)
    min_end_time = min(end_timings)
    max_end_time = max(end_timings)
    video_wise_min_delay = {video_feed: min([list(time_map.keys())[index+1]-list(time_map.keys())[index] for index in range(0, len(time_map)-1)]) for video_feed, time_map in time_mappings.items()}
    video_wise_fps = {video_feed: 1/video_min_delay for video_feed, video_min_delay in video_wise_min_delay.items()}
    min_delay = min(list(video_wise_min_delay.values()))
    fps = 1/min_delay