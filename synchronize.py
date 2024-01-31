#! /usr/bin/env python3

import cv2, pickle, numpy
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

default_video_set_type = "Intersection"
fourcc = cv2.VideoWriter_fourcc(*'MJPG')

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
                              ('-w', "--write", "write", "Folder Name to store the Final Video Files (default=current data and time)"),
                              ('-t', "--type", "type", f"Type of Video Set (Union/Intersection, Default={default_video_set_type})"))
    if not arguments.feed:
        display('-', f"Please provide Name of Feed Folders with time mappings")
        exit(0)
    else:
        arguments.feed = arguments.feed.split(',')
    if not arguments.write:
        arguments.write = f"{date.today()} {strftime('%H_%M_%S', localtime())}"
    if not arguments.type:
        arguments.type = default_video_set_type
    elif arguments.type == "Union":
        arguments.type = "Union"
    makeFolder(arguments.write)
    time_mappings = {}
    display(':', f"Loading Time Mappings")
    T1 = time()
    not_found = []
    for video_feed_folder in arguments.feed:
        try:
            display('*', f"\t{video_feed_folder}", end='')
            t1 = time()
            with open(f"{video_feed_folder}/time_mapping", 'rb') as file:
                time_mappings[video_feed_folder] = pickle.load(file)
            t2 = time()
            if t2 == t1:
                print(f" => {Back.MAGENTA}{t2-t1} seconds{Back.RESET}")
            else:
                print()
        except FileNotFoundError:
            display('-', f"\t{Back.MAGENTA}{video_feed_folder}{Back.RESET} not found", start='\n')
            not_found.append(video_feed_folder)
        except:
            display('-', f"\tError while Reading File {Back.MAGENTA}{video_feed_folder}{Back.RESET}", start='\n')
            not_found.append(video_feed_folder)
    for video in not_found:
        arguments.feed.remove(video)
    T2 = time()
    display('+', f"Loaded Time Mappings")
    display(':', f"\tTime Taken     = {Back.MAGENTA}{T2-T1} seconds{Back.RESET}")
    display(':', f"\tTimings Loaded = {Back.MAGENTA}{len(arguments.feed)}{Back.RESET}")
    if T2 != T1:
        display(':', f"\tRate           = {Back.MAGENTA}{len(arguments.feed)/(T2-T1):.2f} timings/second{Back.RESET}")
    start_timings = {video_feed: list(time_map.keys())[0] for video_feed, time_map in time_mappings.items()}
    end_timings = {video_feed: list(time_map.keys())[-1] for video_feed, time_map in time_mappings.items()}
    min_start_time = min(list(start_timings.values()))
    max_start_time = max(list(start_timings.values()))
    min_end_time = min(list(end_timings.values()))
    max_end_time = max(list(end_timings.values()))
    video_wise_min_delay = {video_feed: min([list(time_map.keys())[index+1]-list(time_map.keys())[index] for index in range(0, len(time_map)-1)]) for video_feed, time_map in time_mappings.items()}
    video_wise_fps = {video_feed: 1/video_min_delay for video_feed, video_min_delay in video_wise_min_delay.items()}
    min_delay = min(list(video_wise_min_delay.values()))
    fps = 1/min_delay
    resolutions = {video_feed: list(reversed(cv2.imread(f"{video_feed}/frames/1.jpg").shape[:2])) for video_feed in time_mappings.keys()}
    gray_scale = {video_feed: False if len(cv2.imread(f"{video_feed}/frames/1.jpg").shape) == 3 else True for video_feed in time_mappings.keys()}
    blank_frames = {video_feed: numpy.zeros(cv2.imread(f"{video_feed}/frames/1.jpg").shape, dtype=numpy.uint8) for video_feed in time_mappings.keys()}
    video_writers = {video_feed: cv2.VideoWriter(f"{arguments.write}/{video_feed}.avi", fourcc, fps, resolutions[video_feed]) for video_feed in time_mappings.keys()}
    display(':', f"FPS    = {Back.MAGENTA}{fps}{Back.RESET}")
    if arguments.type == "Union":
        frames = (max_end_time - min_start_time) / min_delay
        display(':', f"Frames = {Back.MAGENTA}{frames}{Back.RESET}")
        display(':', f"Time   = {Back.MAGENTA}{max_end_time-min_start_time} seconds{Back.RESET}")
        T1 = time()
        for video_feed, time_mapping in time_mappings.items():
            t1 = time()
            print()
            display(':', f"Processing Video Feed {Back.MAGENTA}{video_feed}{Back.RESET}")
            video_timing = min_start_time
            while video_timing < max_end_time:
                if video_timing < start_timings[video_feed] or video_timing > end_timings[video_feed]:
                    frame = blank_frames[video_feed]
                else:
                    frame = cv2.imread(f"{video_feed}/frames/{time_mapping[min(list(time_mapping.keys()), key=lambda frame_time: abs(frame_time-video_timing))]}.jpg")
                video_writers[video_feed].write(frame)
                video_timing += min_delay
            video_writers[video_feed].release()
            t2 = time()
            display('+', f"Processed Video Feed {Back.MAGENTA}{video_feed}{Back.RESET}")
            if t2 != t1:
                display(':', f"\tTime Taken = {Back.MAGENTA}{t2-t1} seconds{Back.RESET}")
        T2 = time()
        print()
        display('+', f"Processed All Video Feeds")
        display(':', f"\tTime Taken  = {Back.MAGENTA}{T2-T1} seconds{Back.RESET}")
        display(':', f"\tVideo Feeds = {Back.MAGENTA}{len(time_mappings)}{Back.RESET}")
        if T2 != T1:
            display(':', f"\tRate        = {Back.MAGENTA}{len(time_mappings)/(T2-T1)} Video Feeds / second{Back.RESET}")
    else:
        frames = (min_end_time - max_start_time) / min_delay
        if frames < 0:
            display('-', f"No Frames in Common")
            exit(0)
        display(':', f"Frames = {Back.MAGENTA}{frames}{Back.RESET}")
        display(':', f"Time   = {Back.MAGENTA}{min_end_time-max_start_time} seconds{Back.RESET}")
        T1 = time()
        for video_feed, time_mapping in time_mappings.items():
            t1 = time()
            print()
            display(':', f"Processing Video Feed {Back.MAGENTA}{video_feed}{Back.RESET}")
            video_timing = max_start_time
            while video_timing < min_end_time:
                if video_timing < start_timings[video_feed] or video_timing > end_timings[video_feed]:
                    frame = blank_frames[video_feed]
                else:
                    frame = cv2.imread(f"{video_feed}/frames/{time_mapping[min(list(time_mapping.keys()), key=lambda frame_time: abs(frame_time-video_timing))]}.jpg")
                video_writers[video_feed].write(frame)
                video_timing += min_delay
            video_writers[video_feed].release()
            t2 = time()
            display('+', f"Processed Video Feed {Back.MAGENTA}{video_feed}{Back.RESET}")
            if t2 != t1:
                display(':', f"\tTime Taken = {Back.MAGENTA}{t2-t1} seconds{Back.RESET}")
        T2 = time()
        print()
        display('+', f"Processed All Video Feeds")
        display(':', f"\tTime Taken  = {Back.MAGENTA}{T2-T1} seconds{Back.RESET}")
        display(':', f"\tVideo Feeds = {Back.MAGENTA}{len(time_mappings)}{Back.RESET}")
        if T2 != T1:
            display(':', f"\tRate        = {Back.MAGENTA}{len(time_mappings)/(T2-T1)} Video Feeds / second{Back.RESET}")