The main file (widget.py) requires Python 3 or above.

To run the project, the following programs must be opened: widgets.py, openCV.py, speechRecognition.py, and webscraping.py.

The following modules were also installed either through the module_manager or pip: cv2, opencv-config, numpy, speech_recognition, google-api-python-client (requires additional setup to personal account), newspaper3k, bs4, requests, PIL, lmlx.

To register a new user within the software uncomment the last line in the __init__ of the Greeting class in the file widgets.py which runs the facial recognition trainer. This allows immediate recognition of the new user once the main file starts. If the user is not new, they should leave the line commented and proceed to run widget.py as is. The index of the camera at the top of openCV.py and of the microphone in speechRecognition.py should be checked if on a device that is not the original. 