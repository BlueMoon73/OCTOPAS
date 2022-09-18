import os
import kivy
from kivy import platform

kivy.require('2.0.0')
from kivy.uix.image import Image

import math
from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
import cv2 as cv
from time import process_time
import numpy as np
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from matplotlib import pyplot as plt
from sklearn import cluster
from kivy.core.text import LabelBase
from kivy.core.window import Window

Window.clearcolor = (1, 1, 1, 1)
from kivy.utils import get_color_from_hex as rgba
import kivy.core.text.markup

if platform == "android":
    from android.permissions import request_permissions, Permission

    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])


# LabelBase.register(name='Gill', fn_regular="Gill Sans MT.ttf")


class oilSpillImage:
    def __init__(self, img):
        self.scaleW = None
        self.scaleH = None
        self.combinedScale = None
        self.img = img

    def scale(self, img, scale=0.2):
        dim1 = int(img.shape[1] * scale)
        dim2 = int(img.shape[0] * scale)
        dims = (dim1, dim2)
        return cv.resize(img, dims, interpolation=cv.INTER_AREA)

    def findOil(self, img, number=2):
        startTime = process_time()
        img = cv.cvtColor(img, cv.COLOR_BGR2HSV) / 255
        # set number of colors

        # quantize to 2 colors using kmeans
        h, w, c = img.shape
        img2 = img.reshape(h * w, c)
        kmeans_cluster = cluster.KMeans(n_clusters=number)
        kmeans_cluster.fit(img2)
        cluster_centers = kmeans_cluster.cluster_centers_
        cluster_labels = kmeans_cluster.labels_

        # need to scale back to range 0-255 and reshape
        img3 = cluster_centers[cluster_labels].reshape(h, w, c) * 255
        img3 = img3.astype('uint8')

        # cv.imshow('reduced colors', img3)
        # cv.waitKey(0)
        # cv.destroyAllWindows()

        # reshape img to 1 column of 3 colors
        # -1 means figure out how big it needs to be for that dimension
        img4 = img3.reshape(-1, 3)

        # get the unique colors
        colors, counts = np.unique(img4, return_counts=True, axis=0)
        # print(colors)
        print("xxx")
        # print(counts)
        unique = zip(colors, counts)

        # function to convert from r,g,b to hex
        def encode_hex(color):
            b = color[0]
            g = color[1]
            r = color[2]
            hex = '#' + str(bytearray([r, g, b]).hex())
            print(hex)
            return hex

        # plot each color
        fig = plt.figure()
        for i, uni in enumerate(unique):
            color = uni[0]
            count = uni[1]
            plt.bar(i, count, color=encode_hex(color))

        # show and save plot
        # plt.show()
        # fig.savefig('barn_color_historgram.png')
        # plt.close(fig)

        endTime = process_time()

        processingTime = endTime - startTime

        (Hpx, Wpx) = img3.shape[:2]
        Wcm = 88
        Hcm = 45

        self.scaleH = Hpx / Hcm
        self.scaleW = Wpx / Wcm
        print(str(self.scaleH), str(self.scaleW))
        self.combinedScale = (self.scaleW + self.scaleW) / 2
        totalWaterArea = Hcm * Wcm

        return img3, processingTime, totalWaterArea, self.scaleH, self.scaleW, self.combinedScale

    def makePerimeters(self, real, reduced, areaReq=1000):
        reduced = cv.cvtColor(reduced, cv.COLOR_BGR2GRAY)
        # cv.imshow('graty', reduced)

        ###CODE  THAT WORKS###
        # (thresh, reduced) = cv.threshold(reduced, 90, 255, cv.THRESH_BINARY)
        reduced = cv.adaptiveThreshold(reduced, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 3, 0)

        contours, hierarchies = cv.findContours(reduced, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        # cv.imshow('v2',reduced)

        final = real;
        maxArea = -1
        totalOilArea = 0
        oil_contours = []
        maxContournumber = None
        maxContour = None
        hull = None
        length = len(contours)
        uni_hull = []
        for i in range(len(contours)):

            area = cv.contourArea(contours[i])
            if area > areaReq:
                # epsilon = 0.006 * cv.arcLength(contours[i], True)
                # approx = cv.approxPolyDP(contours[i], epsilon, True)
                # final = cv.drawContours(final, [approx], 0, (255, 0, 0), -1)

                # hull = cv.convexHull(contours[i])
                # hull_list.append(hull)

                oil_contours.append(contours[i])

                epsilon = 0.0008 * cv.arcLength(contours[i], True)
                poly = cv.approxPolyDP(contours[i], epsilon, True);
                final = cv.drawContours(final, [poly], -1, (255, 200, 0), -1);

                # final = cv.drawContours(final, contours, i, (255, 0, 0), -1)

                kernel = np.ones((9, 9), np.uint8)
                final = cv.morphologyEx(final, cv.MORPH_CLOSE, kernel)
                final = np.uint8(final)
                totalOilArea = totalOilArea + area

            if area > maxArea:
                maxArea = area
                maxContournumber = i
                maxContour = contours[i]

                # kernel = np.ones((5, 5), np.uint8)
                # # dilation = cv.dilate(final, kernel, iterations=1)
                # kernel = np.ones((10, 10), np.uint8)
                # # final = cv.morphologyEx(final, cv.MORPH_CLOSE, kernel)
                # final = np.uint8(final)
                # final = cv.medianBlur(final, (3, 3))
                # final = cv.GaussianBlur(final, (1, 1))

        for i in range(len(contours)):

            area = cv.contourArea(contours[i])
            if area > areaReq:
                hull = cv.convexHull(contours[i])
                cv.drawContours(final, [hull], -1, (0, 0, 255), 4)
            else:
                continue

        # size of contour points
        numOfSpills = len(oil_contours)
        # concatinate poits form all shapes into one array
        cont = np.vstack([oil_contours[i] for i in range(numOfSpills)])
        hull = cv.convexHull(cont)
        uni_hull.append(hull)  # <- array as first element of list
        cv.drawContours(final, uni_hull, -1, (165, 255, 0), 4);

        hullLengthinPX = cv.arcLength(hull, closed=True)
        hullLengthinCM = hullLengthinPX / self.combinedScale
        return final, contours, totalOilArea, hullLengthinCM

    def label(self, finalimg, ellipse, totalOilArea, circlerad, largestContourArea, hull, px, cm):
        scale = px / cm

        # ellipse perimeter
        (x, y), (width, height), angle = ellipse
        a = width / 2
        a = a / scale
        b = width / 2
        b = b / scale
        h = (a - b) ** 2 / (a + b) ** 2

        # ellipse boom
        perimeterOfEllipseBoominPX = (math.pi * (a + b) * (1 + (3 * h) / (10 + np.sqrt((4 - (3 * h))))))
        perimeterOfEllipseBoominCM = perimeterOfEllipseBoominPX

        # circle boom
        perimeterOfCircleBoominPX = (2 * math.pi * circlerad)
        perimeterOfCircleBoominCM = (perimeterOfCircleBoominPX / scale);

        # oil area
        totalOilAreainCM2 = totalOilArea / (scale * scale)
        largestContourAreainCM = largestContourArea / (scale * scale)

        # hull length
        hullLengthinPX = cv.arcLength(hull, closed=True)
        hullLengthinCM = hullLengthinPX / scale

        # percent of oil
        containerArea = cm ** 2 * math.pi
        percentOfOil = totalOilAreainCM2 * 100 / containerArea

        # labeling
        cv.putText(finalimg, ('Total Oil Area: ' + str((totalOilAreainCM2)) + ' cm'), (0, 15), cv.FONT_HERSHEY_SIMPLEX,
                   0.5,
                   (255, 0, 0), 2)
        cv.putText(finalimg, ('Largest Patch Area: ' + str((largestContourAreainCM)) + ' cm'), (0, 30),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        cv.putText(finalimg, ('Length of Ellipse Boom: ' + str((perimeterOfEllipseBoominCM)) + ' cm'), (0, 45),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 128), 2)
        cv.putText(finalimg, ('Length of Circle Boom: ' + str((perimeterOfCircleBoominCM)) + ' cm'), (0, 60),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        cv.putText(finalimg, ('Length of Hull Boom: ' + str((hullLengthinCM)) + ' cm'), (0, 75),
                   cv.FONT_HERSHEY_SIMPLEX,
                   0.5, (165, 255, 0), 2)
        cv.putText(finalimg, ('Percent of Oil in Container: ' + str((percentOfOil)) + ' %'), (0, 90),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        return finalimg

    # def analyze(self, processedIMG):


class FilePickerScreen(Screen):
    def __init__(self, **kwargs):
        self.processPic = None
        self.scaleW = None
        self.scaleH = None
        self.combinedScale = None

        super(FilePickerScreen, self).__init__(**kwargs)
        print(len(self.children))
        print(len(self.children))

    def _finish_init(self):
        self.layout = self.ids["displayOverlay"]
        self.OilImage = self.ids["OilImage"]
        self.OilImage.nocache = True
        # self.OilImage.size = self.parent.width, self.parent.width/self.image_ratio

        self.filePicker = self.ids["filechooser"]
        self.filePicker.bind(on_entry_added=self.update_file_list_entry)
        self.filePicker.bind(on_subentry_to_entry=self.update_file_list_entry)
        # self.layout.add_widget(self.OilImage)
        self.title = self.ids["title"]
        self.processTimeLabel = self.ids["processTime"]
        self.areaOfWaterLabel = self.ids["areaOfWater"]
        self.areaOfOilLabel = self.ids["areaOfOil"]
        self.percentOfOilLabel = self.ids["percentOfOil"]
        self.lengthOfBoomLabel = self.ids["lengthOfBoom"]

        # self.layout.add_widget(self.ProcessedImage)
        print("innit finished")

    def selected(self, filename):
        self.fileName = filename
        # print("selected: %s" % filename[0])

    def update_file_list_entry(self, file_chooser, file_list_entry, *args):
        file_list_entry.font_size = 30
        file_list_entry.ids['filename'].color = rgba("#005c7a")

    def open(self, path, fileName):

        try:
            file = os.path.join(path, fileName[0])
            pic = cv.imread(file)
            (h, w) = pic.shape[:2]
            if h > w:

                pic = cv.rotate(pic, cv.ROTATE_90_CLOCKWISE)
                cv.imwrite('originalImage.png', pic)
                print('rotated')
                print(h, w)

            else:
                cv.imwrite('originalImage.png', pic)

            self.OilImage.source = 'originalImage.png'

        except IndexError:
            self.title.text = "Please select an Image!"
        except:
            self.title.text = "An error occured!"

    def scale(self, img, scale=0.2):
        dim1 = int(img.shape[1] * scale)
        dim2 = int(img.shape[0] * scale)
        dims = (dim1, dim2)
        return cv.resize(img, dims, interpolation=cv.INTER_AREA)

    def process(self):

        file = self.OilImage.source
        if (file != "PleasePickAnImage.png"):
            pic = cv.imread(file)
            self.processPic = oilSpillImage(pic)
            print("file being processed" + file)

            reducedColors, processingTime, totalWaterAreainCM3, self.scaleH, self.scaleW, self.combinedScale = self.processPic.findOil(pic)

            final, contours, totalOilAreainPx, hullLengthinCM3 = self.processPic.makePerimeters(pic, reducedColors, areaReq=100)
            cv.imwrite('processed_pic.jpg', final)

            totalOilAreainCM3 = totalOilAreainPx / self.scaleH
            totalOilAreainCM3 = totalOilAreainCM3 / self.scaleW
            totalOilAreainCM3 = round(totalOilAreainCM3, 2)

            totalOilPercent = (totalOilAreainCM3 / totalWaterAreainCM3) * 100
            totalOilPercent = round(totalOilPercent, 2)

            hullLengthinCM3 = round(hullLengthinCM3, 2)
            # self.combinedScale = (self.scaleW + self.scaleH) / 2



            self.OilImage.source = 'processed_pic.jpg'
            self.OilImage.reload()

            self.title.text = "Image Analytics:  "
            self.processTimeLabel.text = "The time taken to process the image was: " + str(processingTime) + " seconds!"
            self.areaOfWaterLabel.text = "The area of water is " + str(totalWaterAreainCM3) + " cubic centimeters"
            self.areaOfOilLabel.text = "The area of oil is " + str(totalOilAreainCM3) + " cubic centimeters"
            self.percentOfOilLabel.text = "The percent of oil in the water is " + str(totalOilPercent) + "%"
            self.lengthOfBoomLabel.text = "The length of the boom is " + str(hullLengthinCM3) +  " centimeters"
        else:
            self.title.text = "Please select an Image!"

    def clear(self, path):
        print("cleared!")
        self.title.text = "Image Succesfully Cleared!"
        self.OilImage.source = 'PleasePickAnImage.png'
        self.clearText()

    def clearText(self):
        self.processTimeLabel.text = ''
        self.areaOfWaterLabel.text = ''
        self.areaOfOilLabel.text = ''
        self.percentOfOilLabel.text = ''
        self.lengthOfBoomLabel.text = ''


class ProcessedImageScreen(Screen):
    pass


class WindowManager(ScreenManager):
    pass


# kv = Builder.load_file('octopas.kv')
class OctopasAPP(App):

    def build(self):
        sm = WindowManager()
        aids = FilePickerScreen(name='first')
        aids._finish_init()
        sm.add_widget(aids)

        # sm.add_widget(FP)
        return sm


if __name__ == '__main__':
    OctopasAPP().run()
