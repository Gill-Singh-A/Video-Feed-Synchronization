# Video Feed Synchronization
Simple Python Programs that Synchronizes video frames of different FPS and recording time by mapping frames with respect to the time time they were captured.

## Requirements
Language Used = Python3<br />
Modules/Packages used:
* cv2
* pickle
* numpy
* pathlib
* datetime
* optparse
* colorama
* time
<!-- -->
Install the dependencies:
```bash
pip install -r requirements.txt
```

## Recorder
***record.py*** is the Recorder Program that maps recorded frames to the time they were captured.<br />
It creates a folder in the current working directory with name depending upon the command line arguments provided.<br />
In the folder there are 2 items:
* frames
* time_mapping
<!-- -->
**frames** is a folder that contains the recorded frames with their name as frame index and extension *.jpg*<br />
**time_mapping** is a pickle file that maps the time at which the frame was recorded to the frame index.
### Arguments
It takes in the following command line arguments:
* '-c', "--camera": Index of Camera Device to use
* '-s', "--show": Show the Camera Feed (True/False, Default=False)
* '-w', "--write": Folder Name to store the Frames and Time Mappings (default=current data and time)

## Synchronizer
***synchronize.py*** is the Synchronizer Program that loads the time mappings and frames to make final videos for each recording that is synchronized with each other.<br />
The Final Videos are stored in a newly folder created in the current working directory with name depending upon the command line arguments provided.<br />
It has 2 types of Synchronizing Options:
* Union
* Intersection
<!-- -->
### Union Mode
In the union mode, every frame of the video is there in the final video. If a video feed didn't capture a frame at some specific time, then a Blank Frame is added at that time.
### Intersection Mode
In the intersection mode, only the video frames that are in common in all the video files are added.
### Arguments
It takes in the following command line arguments:
* '-f', "--feed": Name of Feed Folders with time mappings (seperated by ',')
* '-w', "--write": Folder Name to store the Final Video Files (default=current data and time)
* '-t', "--type": Type of Video Set (Union/Intersection, Default=Intersection)