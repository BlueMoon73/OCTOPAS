#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#
#  Author:  Monish Saravana Kumar Divya Sundari
#
#  Initial Date:  9/10/2022
#
#  Last Updated:  10/1/2022
#
#  Description:  The main python source code, for the OCTOPAS Algorithm, as found on
#                 https://github.com/BlueMoon73/OCTOPAS. OCTOPAS stands for Oil spill Cleanup Through an Optimized
#                 Pragmatic Automated System. OCTOPAS is a novel system aimed towards automating oil spill clean-ups.
#                 This is part of a # multi-year (currently year 3) research project, towards improving oil spill
#                 clean-ups.
#
#  Version: OCTOPAS 1.0
#
#
#
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

# import OS - to be able to manipulate system paths
# import time - used for the timers, to calculate media processing time.
# import cv2 - used to import OpenCV, which is the library used to process and analyze the images.
# import kivy - used to create the GUI
# import numpy - used to perform calculations, based on the images. used for concatenating arrays, calculations of
# histograms, finding unique colors, etc. numpy simplifies and optimizes mathematical calculations.
# import datetime - used to get the current date and time, to be displayed on screen


import os
import time
import cv2 as cv
import kivy
import matplotlib
import numpy as np
import serial
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# from kivy.app import App - required import to run the application.
# from kivy.clock import Clock - required for scheduling certain tasks.
# from config import Config - used to set the configuration of the application, such as how to respond to various inputs
# from kivy.core.window import Window - used to set the window size, and the window title
# from kivy.uix.screenmanager import ScreenManager, Screen - used to create the screens, and to switch between them
# from kivy.utils import get_color_from_hex as rgba - used for converting hexadecmical colors into the rgba format
# from matplotlib import pyplot as plt - used to plot the histograms; for future enhancements
# from sklearn import cluster - used to perform the clustering of the colors

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import get_color_from_hex as rgba

from sklearn import cluster

# set minimum version of kivy to 2.0.0
kivy.require('2.0.0')

# setting  configuration of how to respond to other mouse buttons that are not left-click
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

# set the window color to white

Window.clearcolor = (1, 1, 1, 1)


# class for the actual image processing algorithm. this class can be called, anytime an image needs to be processed.
# this is a separate class, and not coded into the screen class because there may be multiple images that get processed
# at the same time.
class OilSpillImage:

    # initializes the class, and declares the Width Scale, Height Scale, Combined Scale, and the image variables.
    # the input for this function is just the image.
    def __init__(self, img):
        self.scaleW = None
        self.scaleH = None
        self.combinedScale = None
        self.img = img

    # function to distinguish the oil from the water. this function takes in the image, and the number of colors to
    # quantize.  the default is 2, which is water and oil, but it can be changed when the function is called.
    # it uses the kmeans algorithm from scikit learn, in order to separate the colors and group them.

    def findOil(self, img, numOfColors=2):

        # convert the image from the BGR colorspace to the HSV color space. this is done because the HSV color space is
        # easier to work with, for distinguishing between oil and water.
        img = cv.cvtColor(img, cv.COLOR_BGR2HSV) / 255

        # quantize to 2 colors using kmeans. this is the majority of the code that is used to distinguish between oil
        # and water.
        h, w, c = img.shape
        img2 = img.reshape(h * w, c)
        kmeans_cluster = cluster.KMeans(n_clusters=numOfColors)
        kmeans_cluster.fit(img2)
        cluster_centers = kmeans_cluster.cluster_centers_
        cluster_labels = kmeans_cluster.labels_

        # need to scale back to range 0-255 and reshape
        clusteredImage = cluster_centers[cluster_labels].reshape(h, w, c) * 255
        clusteredImage = clusteredImage.astype('uint8')

        # reshape img to 1 column of 3 colors
        # -1 means figure out how big it needs to be for that dimension
        img4 = clusteredImage.reshape(-1, 3)
        # shows the clustered image; used for debugging
        ## cv.imshow('img4', clusteredImage)

        # get the unique colors
        colors, counts = np.unique(img4, return_counts=True, axis=0)
        unique = zip(colors, counts)

        # function to convert from r,g,b to hex; not used yet; for future enhancements
        ## def encode_hex(BGRcolor):
        ##     b = BGRcolor[0]
        ##     g = BGRcolor[1]
        ##     r = BGRcolor[2]
        ##     hexColor = '#' + str(bytearray([r, g, b]).hex())
        ##     print(hexColor)
        ##     return hexColor

        # plot each color; for future enhancements
        ## fig = plt.figure()
        ## for i, uni in enumerate(unique):
        ##     color = uni[0]
        ##     count = uni[1]
        ##     plt.bar(i, count, color=encode_hex(color))

        # show and save plot; for future enhancements
        ## plt.show()
        ## fig.savefig('barn_color_histogram.png')
        ## plt.close(fig)

        # get the height and width of the image (in pixels)
        (Hpx, Wpx) = clusteredImage.shape[:2]

        # this is set to the dimensions [Length x Width] of the container, in which the oil spill is simulated. in a
        # real world use case, this can be set to the dimensions/area that the drone can cover with a singular image.
        # this is configurable. the container dimensions in the simulation, is 88cm x 45cm.

        Wcm = 88
        Hcm = 45

        # calculate the scale of the image, in pixels/cm
        self.scaleH = Hpx / Hcm
        self.scaleW = Wpx / Wcm

        # prints the scales of the image; for future enhancements and debugging
        ## print(str(self.scaleH), str(self.scaleW))

        # averaging the scales of the image to calculate the combined scale***
        # for revision
        self.combinedScale = (self.scaleW + self.scaleH) / 2

        # calculating the area of water in the image in cm^2
        totalWaterArea = Hcm * Wcm

        # returning the clustered image, the calculated total water area, and the scales of the image.

        return clusteredImage, totalWaterArea, self.scaleH, self.scaleW, self.combinedScale

    # function to interpret the clustered image. the function takes in the real (original image), the clustered image
    # and the area requirement for the oil contours. the default area requirement is set to 1000 pixels. an oil spill
    # pocket is considered "significant" if it's area is over 3000 pixels. Micro oil spill pockets,
    # less than 1000 pixels, are considered insignificant. *** for revision
    # this function also creates the booms and displays them on screen.

    def makePerimeters(self, real, clusteredImage, areaReq=1000):

        # the colorspace of the image is converted to grayscale
        grayscaleImage = cv.cvtColor(clusteredImage, cv.COLOR_BGR2GRAY)

        # thresholding the grayscale image; inputs are the grayscale image, the output threshold value, the type of
        # adaptive thresholding, the threshold method, the pixel neighborhood size, and the constant to be subtracted.
        # the image is now a binary image (black and white image)

        binaryImage = cv.adaptiveThreshold(grayscaleImage, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv.THRESH_BINARY, 3, 0)

        # finds the contours and the hierarchy of the binary image
        contours, hierarchies = cv.findContours(binaryImage, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        # declares variables and arrays to be used
        # final - makes a copy of the real image, the real image is never modified, only the final image is modified
        # throughout the algorithm
        # *** for revision
        final = real
        maxArea = -1
        totalOilArea = 0
        oil_contours = []
        uni_hull = []
        kernelFactor = 11
        maxContourIndex = None
        maxContour = None

        # go through the contours and find which ones meet the area requirement (OPS), and then add them to the
        # oil_contours array. draws all the contours that meet the area requirement. *** for revision
        for i in range(len(contours)):

            # assign the area variable to the area of the current contour
            area = cv.contourArea(contours[i])

            # *** for revision OPS
            if area > areaReq:
                # total oil area is increased as more contours are added
                totalOilArea = totalOilArea + area

                # since the contour area is greater than the area requirement, it is considered significant,
                # and so it is added to the oil_contours array
                oil_contours.append(contours[i])

                # approximates the contour to a polygon *** for revision
                polyArcLen = 0.0008 * cv.arcLength(contours[i], True)
                poly = cv.approxPolyDP(contours[i], polyArcLen, True)

                # draw the approximated contour on the image, in dark blue (same color as logo). the contour is also
                # filled in completely with dark blue. BGR  of dark blue is (122, 92, 0). the countours are drawn one
                # by one a new contour is added each iteration of the 'for loop'
                final = cv.drawContours(final, [poly], -1, (122, 92, 0), -1)

                # draws the image; for future enhancements and debugging
                ## final = cv.drawContours(final, poly, -1, (255, 0, 0), 8)

                # Smoothing the image, using a morphological closing operation. the kernel is a 11x11 matrix, but can
                # be changed if the kernelFactor variable is changed. *** for revision , why 11x11, move out of loop
                kernel = np.ones((kernelFactor, kernelFactor), np.uint8)
                final = cv.morphologyEx(final, cv.MORPH_CLOSE, kernel)
                final = np.uint8(final)

        # go through the oil contours array, and make a hull for each one. the hull is the smallest convex polygon that
        # can fit around all the given points in an array.
        for i in range(len(oil_contours)):
            # make a hull for each oil spill and draw it in red, with a width of 4 pixels
            hull = cv.convexHull(oil_contours[i])
            cv.drawContours(final, [hull], -1, (0, 0, 255), 4)

        # the number of oil spills is the length of the oil_contours array
        numOfSpills = len(oil_contours)

        # combine all the points of all the oil spills into oilPoints
        oilPoints = np.vstack([oil_contours[i] for i in range(numOfSpills)])

        # make a hull of all the oil spills, this will be the boom
        hull = cv.convexHull(oilPoints)
        uni_hull.append(hull)

        # draw the hull in blueish green, with a width of 4 pixels. BGR of blue-ish green is (165, 255, 0)
        cv.drawContours(final, uni_hull, -1, (165, 255, 0), 4)

        # calculate the length of the boom in pixels
        hullLengthinPX = cv.arcLength(hull, closed=True)

        # use the combined scale to calculate the length of the boom in cm *** for revision
        hullLengthinCM = hullLengthinPX / self.combinedScale

        # return the final image, the contours, the total oil area, and the hull length in cm
        return final, contours, totalOilArea, hullLengthinCM, clusteredImage, grayscaleImage, binaryImage


# function to update the file list entry, input requires the file chooser widget, and the file list entry.
def update_file_list_entry(file_chooser, file_list_entry, *args):
    # sets the color of the file list entry to dark blue
    file_list_entry.ids['filename'].color = rgba("#005c7a")


# this is the screen that allows you to pick an image, and process it. the analytics of the image, are all displayed on
# this screen. this is the class for the GUI, not the processing.
class FilePickerScreen(Screen):

    # initializes the screen, and declares the necessary variables
    def __init__(self, **kwargs):

        self.TimeLabel = None
        self.fileChooserTitle = None
        self.buttonLayout = None
        self.logo = None
        self.grayscaleImage = None
        self.binaryImage = None
        self.clusteredImage = None
        self.originalImage = None
        self.MenuBluetoothControllerButton = None
        self.MenuOilSpillButton = None
        self.MenuButton = None
        self.processingDropdown = None
        self.headerLayout = None
        self.clearButton = None
        self.processButton = None
        self.pickButton = None
        self.percentOfOilLabel = None
        self.lengthOfBoomLabel = None
        self.areaOfWaterLabel = None
        self.areaOfOilLabel = None
        self.title = None
        self.processTimeLabel = None
        self.filePicker = None
        self.processedImage = None
        self.processPic = None
        self.scaleW = None
        self.scaleH = None
        self.combinedScale = None
        self.fileName = None

        super(FilePickerScreen, self).__init__(**kwargs)

        # for debugging purposes
        ## print("----------------------")
        ## print(len(self.children))
        ## print(len(self.children))

    # setup-function, that cannot be executed in __init__ because the widgets are not created yet. this function
    # assigns the variables, with their respective widget. properties of the widgets are also set in this function.

    def setup(self):

        # sets some variables to their respective widgets
        self.fileChooserTitle = self.ids['FileChooserTitle']
        self.TimeLabel = self.ids['timeLabel']

        # updates the time every second
        Clock.schedule_interval(lambda dt: self.updateTime(), 1)

        # sets the variables to their respective widgets
        self.processingDropdown = self.ids['processingDropdown']
        self.MenuOilSpillButton = self.ids['MenuOilSpillButton']
        self.MenuBluetoothControllerButton = self.ids['MenuBluetoothControllerButton']
        self.MenuButton = self.ids['menuButton']

        # Makes the dropdown open, everytime the menu button is pressed
        self.MenuButton.bind(on_release=self.processingDropdown.open)

        # setting properties of the dropdown and the menu button
        self.processingDropdown.bind(on_select=lambda instance, x: setattr(self.MenuButton, 'text', x))
        self.processingDropdown.auto_dismiss = True

        # sets the images to the image widgets, using its ID. also sets properties of the widget
        self.processedImage = self.ids["processedImage"]
        self.processedImage.nocache = True

        self.originalImage = self.ids["originalImage"]
        self.originalImage.nocache = True

        self.clusteredImage = self.ids["clusteredImage"]
        self.clusteredImage.nocache = True

        self.binaryImage = self.ids["binaryImage"]
        self.binaryImage.nocache = True

        self.originalImage = self.ids["originalImage"]
        self.originalImage.nocache = True

        self.grayscaleImage = self.ids["grayscaleImage"]
        self.grayscaleImage.nocache = True

        #
        self.buttonLayout = self.ids["buttonLayout"]
        self.logo = self.ids["logo"]

        # sets button variable to their respective button widgets to the button widget, using its ID;
        # also sets properties of the buttons
        self.pickButton = self.ids["pickButton"]
        self.pickButton.background_color = rgba('#005c7a')
        self.processButton = self.ids["processButton"]
        self.processButton.background_color = rgba('#005c7a')
        self.clearButton = self.ids["clearButton"]
        self.clearButton.background_color = rgba('#005c7a')

        # sets the file picker widget to the file picker widget, using its ID; calls the update_file_list_entry function
        # every time an entry/subentry is added to the file picker
        self.filePicker = self.ids["filechooser"]
        self.filePicker.bind(on_entry_added=update_file_list_entry)
        self.filePicker.bind(on_subentry_to_entry=update_file_list_entry)

        # sets the labels to their respective label widgets, using their IDs; also sets properties of the labels
        self.title = self.ids["title"]
        self.processTimeLabel = self.ids["processTime"]
        self.areaOfWaterLabel = self.ids["areaOfWater"]
        self.areaOfOilLabel = self.ids["areaOfOil"]
        self.percentOfOilLabel = self.ids["percentOfOil"]
        self.lengthOfBoomLabel = self.ids["lengthOfBoom"]

        # prints "setup finished"; for debugging
        ## print("setup finished")

    def updateTime(self):
        now = datetime.datetime.now()
        currentTime = now.strftime("%I:%M:%S %p")
        self.TimeLabel.text = str(currentTime)

    # function called when a file is selected from the file picker. the name of the file is displayed on screen and is
    # set to the self.fileName variable. the input for this function is the filename.
    def selected(self, filename):
        try:
            self.fileChooserTitle.text = "Selected: " + filename[0]
            self.fileName = filename
        except IndexError:
            pass
        except:
            self.title.text = "An error occurred"

    def init_widget(self, *args):

        # sets the fc to the filechooser, using its ID
        fc = self.ids['filechooser']

        # calls the update file list entry function, every time an entry or subentry is added to the file picker
        fc.bind(on_entry_added=update_file_list_entry)
        fc.bind(on_subentry_to_entry=update_file_list_entry)

    # function to execute when the pick button is pressed. the function will try to open the selected image. this
    # if the image is not a jpg, png, or bmp, it will not open. if the image is opened, it will show the image on screen
    # this function will also rotate the image, if it is vertical.the inputs for the file are the path, and the filename
    # the inputs for this function are the path, and the filename.

    def open(self, path, fileName):

        # tries to open the image, but if an error rises, it will print the error.
        try:

            # reads the image and opens file
            file = os.path.join(path, fileName[0])
            pic = cv.imread(file)

            # finding the height and width of the image in pixels
            (h, w) = pic.shape[:2]

            # if the height is greater than the width, the image is rotated 90 degrees clockwise
            if h > w:
                pic = cv.rotate(pic, cv.ROTATE_90_CLOCKWISE)
                cv.imwrite('originalImage.png', pic)

            # writes the image to a file named originalImage.png
            # the file is saved on your computer
            cv.imwrite('originalImage.png', pic)

            # the source of the image displayed on screen is set to the originalImage.png file
            self.originalImage.source = ""
            self.originalImage.source = 'originalImage.png'
            cv.imwrite('original_image.jpg', pic)

        # if an errror rises, at it is an IndexError, it will display "Please Select an Image" on the screen.
        except IndexError:
            self.fileChooserTitle.text = "Please select an Image!"

        # if it is any other error, it will display an error message on the screen.
        except:
            self.fileChooserTitle.text = "An error has occured while selecting that image!"

    # function to execute when the process button is pressed. the function will process the given image, and display
    # the respective analytics. it will also display the time it took to process the image.
    def process(self):

        # gets the file that is displayed on the screen
        file = self.originalImage.source

        # process all images except the default image
        if file != "drone.png":

            # start the timer
            StartTime = time.perf_counter()

            # read the image
            originalImage = cv.imread(file)

            # create an instance of the OilSpillImage class
            self.processPic = OilSpillImage(originalImage)

            # finds the oil in the image
            reducedColors, totalWaterAreaInCM2, self.scaleH, self.scaleW, self.combinedScale = self.processPic.findOil(
                originalImage)

            #  makes the oil spill visible, and gets all the analytics
            processedImage, contours, totalOilAreaInPx, hullLengthinCM3, clusteredImage, grayscaleImage, binaryImage = \
                self.processPic.makePerimeters(originalImage, reducedColors, areaReq=1000)

            # save the images
            cv.imwrite('processed_pic.jpg', processedImage)
            cv.imwrite('clustered_image.jpg', clusteredImage)
            cv.imwrite('grayscale_image.jpg', grayscaleImage)
            cv.imwrite('binary_image.jpg', binaryImage)

            # finding oil area in cm^2 using the scale
            totalOilAreaInCM2 = totalOilAreaInPx / self.scaleH
            totalOilAreaInCM2 = totalOilAreaInCM2 / self.scaleW
            totalOilAreaInCM2 = round(totalOilAreaInCM2, 2)

            # finding oil percent of the entire image
            totalOilPercent = (totalOilAreaInCM2 / totalWaterAreaInCM2) * 100
            totalOilPercent = round(totalOilPercent, 2)

            # finding the length of boom needed
            hullLengthinCM3 = round(hullLengthinCM3, 2)

            self.clusteredImage.source = 'clustered_Image.jpg'

            self.grayscaleImage.source = 'grayscale_image.jpg'

            self.binaryImage.source = 'binary_image.jpg'

            self.processedImage.source = 'processed_pic.jpg'

            self.title.text = "Image Analytics:  "
            self.areaOfWaterLabel.text = "The area of water is " + str(totalWaterAreaInCM2) + " square centimeters"
            self.areaOfOilLabel.text = "The area of oil is " + str(totalOilAreaInCM2) + " square centimeters"
            self.percentOfOilLabel.text = "The percent of oil in the water is " + str(totalOilPercent) + "%"
            self.lengthOfBoomLabel.text = "The length of the boom is " + str(hullLengthinCM3) + " centimeters"

            # ending the timer
            endTime = time.perf_counter()

            # calculating the entire time taken to process the image
            processingTime = endTime - StartTime

            # rounding the time to 2 decimal places
            processingTime = round(processingTime, 2)

            # displaying the time it took to process the image
            self.processTimeLabel.text = "The time taken to process the image was: " + str(
                processingTime) + " seconds! "

        else:
            # if the same image is the same as the default image, tell the user to select an image
            self.title.text = "Please select an Image!"

    # function to clear the image and analytics from the screen. this function is called when the clear button is
    # pressed
    def clear(self):
        # print("cleared!")

        # clears the image and sets it to the default image. also displays that the process was a success
        self.originalImage.source = 'drone.png'
        self.processedImage.source = 'processed.png'
        self.clusteredImage.source = 'clustered.png'
        self.grayscaleImage.source = 'grayscale.png'
        self.binaryImage.source = 'blackandwhite.png'
        self.title.text = "Image Succesfully Cleared!"

        # clear the analytics from the screen
        self.processTimeLabel.text = 'Please pick an Image!'
        self.areaOfWaterLabel.text = ''
        self.areaOfOilLabel.text = ''
        self.percentOfOilLabel.text = ''
        self.lengthOfBoomLabel.text = ''


# class to control the sorbent deployment system (OCTOPAS ARM). analytics from the OCTOPAS arm will also be displayed
# on this screen.
class BluetoothController(Screen):

    # initializes requured variables
    def __init__(self, **kwargs):
        self.sorbentCurrentTime = None
        self.sorbentEndTime = None
        self.lastZeroTime = None
        self.lastMessageDateTimeObject = None
        plt.ion()
        super(BluetoothController, self).__init__(**kwargs)
        self.sorbentTime = None
        self.points = None
        self.ax = None
        self.fig = None
        self.timeSinceStart = None
        self.timeSorbentDeployed = None
        self.lastMessage = None
        self.lastMessageTime = None
        self.time = None
        self.TimeLabel = None
        self.bluetooth = None
        self.messageLog = None
        self.textInput = None
        self.MenuButton = None
        self.MenuBluetoothControllerButton = None
        self.MenuOilSpillButton = None
        self.processingDropdown = None
        self.messageLogTitle = None
        self.Graph = None
        self.startTime = datetime.datetime.now()

    def setup(self):
        # sets the variables involved with the dropdown to their respective widgets
        self.processingDropdown = self.ids['processingDropdown']
        self.MenuOilSpillButton = self.ids['MenuOilSpillButton']
        self.MenuBluetoothControllerButton = self.ids['MenuBluetoothControllerButton']
        self.MenuButton = self.ids['menuButton']

        # Makes the dropdown open, everytime the menu button is pressed
        self.MenuButton.bind(on_release=self.processingDropdown.open)

        # sets the texinput to the textinput widget
        self.textInput = self.ids['bluetoothInput']

        # sets the message log to the message log widget
        self.messageLog = self.ids['messageLog']

        # sets the message log title to the message log title widget
        self.messageLogTitle = self.ids['messageLogTitle']

        self.TimeLabel = self.ids['timeLabel']

        self.Graph = self.ids['Graph']

        # updates the time every second
        Clock.schedule_interval(lambda dt: self.updateTime(), 1)

        self.generateGraph()

        Clock.schedule_interval(lambda dt: self.updateGraph(), 1)

        try:
            self.pair()
        except Exception as e:
            self.messageLogTitle.text = "Please turn on bluetooth on your computer!"
            self.messageLog.text = "Error Occured " + str(e) + serial.__file__

    def updateTime(self):
        now = datetime.datetime.now()
        currentTime = now.strftime("%I:%M:%S %p")
        self.TimeLabel.text = str(currentTime)

    def sendMessage(self, message):
        # gets the current time and formats it
        now = datetime.datetime.now()
        currentTime = now.strftime("%I:%M:%S")
        self.lastMessageDateTimeObject = now

        if message.isdigit():

            # adds the message to the log
            self.messageLog.text = self.messageLog.text + " " + currentTime + ": " + message + '\n'
            self.lastMessage = message
            self.lastMessageTime = currentTime

            # sends the message to the arduino via the bluetooth module
            try:
                self.bluetooth.write(message.encode())
                self.messageLogTitle.text = "ARM Controller Log"
            except AttributeError:
                self.messageLogTitle.text = "Please turn on bluetooth on your computer!"

        else:
            self.messageLogTitle.text = "Please enter the time, in seconds!"

    def pair(self, port='COM10', baudrate=9600):
        # establishes a connection with the bluetooth module
        self.bluetooth = serial.Serial(port, baudrate)
        self.bluetooth.flushInput()
        self.messageLog.text = self.messageLog.text + "Bluetooth Connected to " + port + '\n'

    def generateGraph(self):

        # print(lol)

        # result = (self.startTime + datetime.timedelta(hours=0, minutes=2, seconds=24))

        xLabels = [self.startTime.strftime("%I:%M:%S")]
        xTicks = [self.startTime]
        print(self.startTime)
        print(type(self.startTime))
        for i in range(10 * 2):
            if i >= 1:
                seconds = self.startTime.strftime("%S")
                seconds = int(seconds)
                roundedStartTime = self.startTime + datetime.timedelta(seconds=-seconds)
                tick = roundedStartTime + datetime.timedelta(seconds=30 * i)
                # tick = label.strftime("%I:%M:%S")
                label = tick.strftime("%I:%M:%S")
                xTicks.append(tick)
                print(xTicks)
                print(tick)
                print('0---0-0-0-0')
                print(label)
                xLabels.append(label)

        xTicks = matplotlib.dates.date2num(xTicks)

        yTicks = []
        for i in range(60):
            yTicks.append(i)
        print(xTicks)

        self.fig, self.ax = plt.subplots(1, 1)

        self.points = self.ax.plot(self.startTime, 0, '-o')[0]

        self.ax.xaxis.axis_date = True
        self.ax.set_xlabel('Time Of Deployment')
        self.ax.set_title('Graph of Sorbent Deployment')

        self.ax.set_ylabel('Amount of Sorbent Deployed (seconds)')

        self.ax.set_yticks(yTicks)
        self.ax.set_xticks(xTicks)
        self.ax.set_xticklabels(xLabels)

        plt.savefig('Graph.png', bbox_inches='tight')
        self.Graph.source = 'Graph.png'

    def updateGraph(self):
        now = datetime.datetime.now()
        now = (now + datetime.timedelta(hours=0, minutes=0, seconds=-1))
        # currentTime = now.strftime("%I:%M:%S")
        xdata = self.points.get_xdata()
        # nowTime = matplotlib.dates.date2num(now)
        diff = None

        try:
            diff = now - self.lastMessageDateTimeObject
        except TypeError:
            pass

        if len(xdata) < 120:
            if diff and diff.total_seconds() < 1:
                self.sorbentTime = int(self.lastMessage)
                timeOfDeployment = [self.lastZeroTime]
                deployment = [0]

                for i in range(self.sorbentTime):
                    # print(self.lastMessageTime)
                    self.sorbentCurrentTime = (self.lastMessageDateTimeObject + datetime.timedelta(seconds=i))
                    timeOfDeployment.append(self.sorbentCurrentTime)
                    deployment.append(self.sorbentTime)

                self.sorbentEndTime = self.sorbentCurrentTime
                timeOfDeployment = matplotlib.dates.date2num(timeOfDeployment)
                # print(timeOfDeployment)
                # print(deployment)

                self.ax.plot(timeOfDeployment, deployment, '-o', c='green')
                print(now)

                print(self.lastMessageDateTimeObject)
                print("00-")

            else:
                zeroTime = []
                amtOfSorbent = []
                previousSecond = now + datetime.timedelta(hours=0, minutes=0, seconds=-1)
                # difference = now - self.sorbentEndTime


                pointIsPlotted = None
                try:
                    maxTime = self.sorbentEndTime + datetime.timedelta(hours=0, minutes=0, seconds=1)
                    if self.lastMessageDateTimeObject < now < maxTime:
                        pointIsPlotted = True
                    else:
                        pointIsPlotted = False

                except:
                    pass

                # print(previousSecond)
                # print(self.sorbentEndTime)
                # print('\n')

                # print(xdata)

                # print(nowTime)
                if self.sorbentTime and previousSecond.strftime("%I:%M:%S") == self.sorbentEndTime.strftime("%I:%M:%S"):
                    zeroTime.append(self.sorbentEndTime)  # the x value of the top
                    zeroTime.append(now)  # x value of 2nd
                    amtOfSorbent.append(self.sorbentTime)  # y value of top
                    amtOfSorbent.append(0)  # y value of 2nd
                    zeroTime = matplotlib.dates.date2num(zeroTime)

                    self.ax.plot(zeroTime, amtOfSorbent, '-o', color='green')
                    print(self.sorbentEndTime)
                    print('in if statement')
                    print(zeroTime)
                elif not pointIsPlotted:

                    # print('no sorbent deployed')
                    zeroTime.append(now)
                    amtOfSorbent.append(0)
                    zeroTime = matplotlib.dates.date2num(zeroTime)
                    self.ax.plot(zeroTime, amtOfSorbent, '-o', c='blue')
                    self.lastZeroTime = now

        else:
            pass   # do nothing

        plt.savefig('Graph.png', bbox_inches='tight')
        self.Graph.reload()
        # plt.show()


class ImageButton(ButtonBehavior, Image):
    pass


# screen manager class, to be able to swap screens. currently not necessary, but will be used in future enhancements
class WindowManager(ScreenManager):
    pass


def resizeScreen():
    # get the screen size
    screen = Window.size

    # get the screen width and height
    screenHeight = screen[1]

    aspectRatio = 4 / 3

    # print(Window.size)
    # set the size of the window to the screen size
    Window.size = (screenHeight * aspectRatio, screenHeight)


# the OCTOPAS class, this is what runs all the previous code.
class OCTOPASApp(App):

    def build(self):
        # makes a screen manager object
        sm = WindowManager()

        # creates a screen for the file picker, and names it 'FPScreen'
        FPScreen = FilePickerScreen(name="FPScreen")

        # creates a screen for the analytics, and names it 'BTController'
        BTController = BluetoothController(name="BTController")

        # sets up the file picker screen
        FPScreen.setup()

        # sets up the bluetooth controller screen
        BTController.setup()

        # adds the file picker screen to the screen manager
        sm.add_widget(FPScreen)

        # adds the bluetooth controller screen to the screen manager
        sm.add_widget(BTController)

        # sets the icon of the app
        self.icon = 'Icon.ico'

        # sets the title of the window
        self.title = 'OCTOPAS Algorithm'

        # returns the screen manager
        return sm


# runs the OCTOPAS class
if __name__ == '__main__':
    # forces the window to be 4:3 aspect ratio
    Clock.schedule_interval(lambda dt: resizeScreen(), 0)
    # runs the app
    OCTOPASApp().run()
