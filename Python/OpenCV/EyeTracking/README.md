<h1>Eye Tracking.</h1>
<h3>(work in progress)</h3>
<p>
Eye tracking program in Python, using OpenCV.
</p>
<!-- ![alt text](http://url/to/img.png)-->

## 1. Introduction to the project

The core of the project is the eye tracking program which allows extracting data from the user, the interface is the connecting part, which permits the interaction between the user and the computer, and finally the computer will be connected to a circuit using a specific microcontroller to control the environment of the patient.

## 2. Eye Tracking Algorithm

The eye tracking algorithm is the heart of the project, it processes images taken by a standard computer webcam, and extract eye ball position and blink (wink) action, to control the user interface or the mouse.  

Since we seek a project that serves any individual in need we tried to make the program intuitive, easily usable under any circumstances beside being available for free so it is written in Python 3 which is a modern programming language, popular because of its simplistic syntax, and the presence of inexpensive open source libraries, also all image acquisition and processing are based on OpenCV, an open source Computer Vision framework, written in C/C++ but has a python binding module, which we use here.  

### 2.1 Image Acquisition:

The picture is acquired from the webcam in an RGB format.  
Images are a set of pixels arranged in a 3D matrix: (n x m) x 3 color channels (Red, Green, Blue), starting from the top left corner.
For the purpose of feature detection the picture is converted into grayscale.  
Grayscale images are one channel matrices (n x m), so they are suitable for easy matrix operations, and reduce computing load.  

### 1. Detect Face:

After the image is converted to grayscale, we feed the image to the feature detection library.  
We start by the face detection, the eye detection is quite heavy on the computer, so it&#39;s better to first detect the face, then restrict the eyes detection on the area of the face, our region of interest.  

### 2. Detect Eye:

After the face have been detected, we crop the image to only have the detected face. We then proceed to the eye detection.
- We get a list of all eyes detected, their position and size.  
- We do some basic filtering, like removing false positive, like an eye detected below half the face is surely not an eye, but a glitch from the feature detection, it is not a perfect technology.  
- After the filtration we detect which eye is it, left or right, by comparing the horizontal coordinate of the eye, with the middle of the face, since the image pixels are arranged from the left to right, left \&lt; middle \&lt; right.  
- We save the detected eye information in a variable, the informations are the coordinates of the eye&#39;s center and its side (left of right).  
In this step we also detect the wink, blink action.  
- Prior to the detection, we set two variables, left\_open and right\_open, both equals to zero.  
- During the iterations of the detected eyes, if the detected eye is the left one, we set left\_open = 1, and if its the right eye, right\_open = 2.  
- After the iteration is finished, we add both values, left\_open and right\_open, and save it in a variable. Here are the 4 possibilities:  

#### a. Both eyes closed:
   left\_open = 0 and right\_open = 0  
   0 + 0 = 0

#### b. Right blink (only left eye is openned):
   left\_open = 1 and right\_open = 0  
   1 + 0 = 1

#### c. Left blink (only right eye is openned):
   left\_open = 0 and right\_open = 2  
   0 + 2 = 2

#### d. Both eyes openned:
   left\_open = 1 and right\_open = 2  
   1 + 2 = 3

  From here we can map each blink action to a number for later use to command the mouse clicking etc. In this step we gathered all information about the eye.  

### 3. Calibration: Set Bound Box around Eye.

Calibration is toggled automatically at the beginning of the program or launched by clicking on the calibrate button.  
The calibration take place at the eye detection phase, there is a variable that hold the eye coordinates as usual plus the eye&#39;s dimensions (height and width).  
That information is used to set the region of interest to detect the position of the eye&#39;s iris.  
The user has to keep the eyes centered, because the position of the eye at that stage set the coordinates origin.  
For example, if the eye was slightly in the left, the whole image will be shifted slightly right, so to keep the eye at the center of the image. And that shift will be kept throughout the detection phase, until recalibrated.  

### 4. Process image:

After the calibration process is finished, and the region of interest of the eyes is saved, we can now look for the position of the iris, but the image needs to be processed and filtered, until now the images have been in grayscale.  
First, we centralize the image by applying the shifts set in the calibration phase.  
Then crop the image to avoid eyebrows or corner of the eye which can be dark enough to interfere in our detection. We crop 20% of the image on all side, top, down, left and right. The value 20 have been set upon testing various numbers, it&#39;s the one that offer the cleanest results.  
Those are the image operation (shift and crop), now we do the image color operation.  
First, we have to remember that the image in grayscale is a set of pixels arranged in a 2D-matrix (n x m), each pixel has its brightness value, this value goes from 0 (Black) to 255 (White).  
Now we need to turn the image into a pseudo-binary image, black or white, no grays involved. To do that we need to calculate a brightness threshold. By testing we set that threshold to be the minimum value (darkest pixel) plus 10% of the average brightness of the whole image.  
This way only the darkest pixels and their neighbors are set to black, the remaining of the image is set to white.  
Since we cropped the image on all side, we are sure that only the iris will be black and nothing else.  

### 5. Resize image into 3x3 pixels image:
  Now that only the iris is black, we divide the image into a grid of size 3 by 3 cells.  
Each cell calculates the average brightness and apply it as it brightness value, meaning there would be some gray value where the iris was partially present.  
To remove the gray values, we use the same method as before but this time the threshold is the minimum value (darkest pixel).  
So now the cell containing the iris will be the only dark one, all other will be white.  
If by any chance the iris is in between two cells, the cell containing the maximum portion of the iris would be the dark one, the other will be white.  
At the end of this stage we have a 3x3 grid with only one dark cell, the one containing the iris.  

### 6. Map the pixel index to direction:
  As we said before, images are matrices, each pixel has an index and value corresponding to its brightness.  
Now that we have a nine pixels image, we can easily get the index of the dark pixel which is the minimum value in the matrix, then map the index to a direction.  
At the end of the process, we have extracted at first the blink action, and then the iris location. That information will be sent to the user interface, to control the mouse movement and click events.  

## 3. User Interface

  The interface is based on the tkinter library, it is divided in different views, that the user can switch between using the &quot;View&quot; button is the navigation bar at the top of the user interface. There is also a &quot;Help&quot; in the navigation bar that has two elements:  
Help: Shows basic explanation on how to use the program.  
About us: Show information about the persons who made the program, and their contact information.  

### 3.1. Preview View:

  Where a live display of the webcam is shown, the user can see if the program is detecting the face and eyes.  
Start/Pause/Resume Button: button to start and pause the process of detection.  
Calibrate Button: Calibration is done at the start of the program, but If the result is not satisfying, this button run a recalibration process.  
Live video feed: this window is divided in two parts:  
- The top shows the captured eyes, the eye after image processing and the direction detected.  
- The bottom shows the live stream from the webcam, and a black frame around the detected face, and a red frame delimiting the eye bounding box (set in the calibration phase), and a blue &quot;+&quot; at the center of the detected eye.  

### 3.2. Settings View:

  Major preference settings are set here:  
Move mouse: To enable the control of the mouse using our program.  
  Note: Mouse can still be controlled through normal mouse.  
Audio: To enable audio feedback of the commands.  
  example: if the user look right, the software says &quot;right&quot;, so the user knows that his input is taken.  
Horizontal division: The mouse moves by discrete distance or jumps, the horizontal division is the percentage of the screen that the mouse jumps.  
  Example: a screen of width 1280 pixels and a horizontal division of 1%, means the mouse move with a jump of 12 pixels at a time.  
Vertical division: Same as Horizontal division but with the screens height.  
FPS (Frame per second): The number of image taken per second, this affect the CPU use, and response of the software.  
Temperature Offset: This determine the threshold by which the room AC and Heater are controlled.  
  Example: With a desired Temperature of 20°C and offset 5°C means the the heater will go ON when temperature drops below 15°C and the AC at 25°C.  

### 3.3 Application View:

  This view is where the circuitry is controlled, the program take the user&#39;s input and transfer it to the microcontroller that take the desired action.  
  In this view, the eye movement doesn&#39;t control the mouse by default, instead it jumps from a button to the other, and buttons are activated when the user blinks his left or right eye.  
Mouse: to activate the control of the mouse by the eye. This is deactivated by default.  
Alarm: rings an alarm to notice the person taking care of the patient, that he request an assistance.  
Light: Controls the room&#39;s light, On/Off.  
Heater: Manual control of a heater, On/Off.  
AC: Manual control of an AC or fan, On/Off.  
Temperature: Set the desired room temperature, for an automatic control of the heater and AC, the microcontroller will turn On/Off the AC or Heater to keep this temperature constant, within the temperature offset set in the Settings View.  
Window: percentage by which the window sis to be opened.  
  Example: 0% is fully closed, 100% is fully opened, 50% is half open.

## 4. Circuit

  The Arduino program take care of all hardware manipulations, it receives the commands from the computer program, then take the proper action. The data is sent from the computer using Serial connection via an USB cable that connects the computer to the Arduino.
The microcontroller receives the data as a String in the format &quot;\&lt; indicator \&gt;\&lt; Command \&gt;#&quot;:  
- Indicator: select the application. (e.g.: &#39;a&#39; for alarm.)  
- Command: what to do.  (&#39;0&#39; for turn off.)  
- #: Serves as a delimiter for the string, this is needed for performance reasons, it speeds up the reading process and also make sure the received data is in proper format.  

## 5. How to use it:

  On the launch of the program the user is greeted on the Preview page where he need to start the image acquisition. This is done by clicking on the Start button. A live feed is then shown and the user can see the result and decide if the calibration is correct or not, if the calibration is not satisfying, it can be corrected by pressing the calibrate button.  
  The patient needs to test the setting by looking left/right up/down, left/right blink. An audio feedback is provided to confirm if the input is taken or not. If the program doesn&#39;t respond correctly, it needs another calibration, by clicking the calibrate button. 
  At this stage the mouse is still not responding to eye movement, to enable this feature, the person helping has to go to the Settings menu, by clicking on the View item on the menu bar, then click on the Settings.  
On the settings view, the mouse checkbox has to be enabled so the control of the mouse can be done via the program. Note that the mouse can still be controlled by the physical mouse.  
  The mouse moves by a fixed offset, expressed by a percentage of the screen resolution. This percentage can be set in the Horizontal/Vertical text field.  
  The patient is now free to test the mouse movements, by looking up, and the program is supposed to give an audio feedback after the mouse is moved, note that the audio feedback can be deactivated by unchecking the Audio checkbox.  
  The patient is now independent to browse the computer with the eye movements. He can come back to the preview page and keep an eye on the calibration, to see if the eyes are still inside the red box.  Or he can open the Applications page that is used to control the outside circuitry that controls the room.  
  On the applications page, the controls change automatically so that when the patient looks Left/Up the cursor goes to the previous option, if looking Right/Down, the next option is selected. Option are activated/deactivated by blinking the left or right eye.  
  If the patient wish to pause the program he can do so on the Preview page, by clicking on the pause button, note that the calibration is saved, but can be recalibrated at any time after the program is resumed.  