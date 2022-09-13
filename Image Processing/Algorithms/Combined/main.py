
import math
import sys
import cv2 as cv
import numpy
import numpy as np
from matplotlib import pyplot as plt
from sklearn import cluster


class oilSpillImage:
    def __init__(self, img):
        self.img = img

    def scale(self, img, scale=0.2):
        dim1 = int(img.shape[1] * scale)
        dim2 = int(img.shape[0] * scale)
        dims = (dim1, dim2)
        return cv.resize(img, dims, interpolation=cv.INTER_AREA)

    def findOil(self, img, number=2):
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
        print(colors)
        print("xxx")
        print(counts)
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
        plt.show()
        # fig.savefig('barn_color_historgram.png')
        plt.close(fig)
        return img3

    def process(self,img):
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        ret, threshold = cv.threshold(gray, 150, 190, cv.THRESH_BINARY)
        median = cv.medianBlur(threshold, 5)
        contours, hierarchies = cv.findContours(median, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
        output = cv.drawContours(img, contours, -1, (255, 0, 0), 2)

        return output, gray

    def makePerimeters(self,real,  reduced, areaReq=1000):
        reduced = cv.cvtColor(reduced, cv.COLOR_BGR2GRAY)
        cv.imshow('graty', reduced)
        (thresh, reduced) = cv.threshold(reduced, 90, 255, cv.THRESH_BINARY)
        contours, hierarchies = cv.findContours(reduced, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        cv.imshow('v2',reduced)


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

                hull = cv.convexHull(contours[i])
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


            else:
                continue
            if area > maxArea:
                maxArea = area
                maxContournumber = i
                maxContour = contours[i]
            else:
                continue

                kernel = np.ones((5, 5), np.uint8)
                # dilation = cv.dilate(final, kernel, iterations=1)
                kernel = np.ones((10, 10), np.uint8)
                # final = cv.morphologyEx(final, cv.MORPH_CLOSE, kernel)
                final = np.uint8(final)
                final = cv.medianBlur(final, (3, 3))
                final = cv.GaussianBlur(final, (1, 1))

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

        return final, contours
    def process2(self, img, hsvRange1, hsvRange2, areaReq):
        hsvVersion = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        wantedColor = cv.inRange(hsvVersion, hsvRange1, hsvRange2)
        # gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        # _, thresged =  cv.threshold(gray, 160, 255, cv.THRESH_BINARY)
        kernel = np.ones((7, 7), np.uint8)
        median = cv.morphologyEx(wantedColor, cv.MORPH_CLOSE, kernel)
        # median = np.uint8(median)
        median = cv.GaussianBlur(median, (3, 3), cv.BORDER_DEFAULT)
        # median = cv.medianBlur(median, 3)

        # C,H=cv.findContours(thresged, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        contours, hierarchies = cv.findContours(median, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        final = img;
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

                hull = cv.convexHull(contours[i])
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


            else:
                continue
            if area > maxArea:
                maxArea = area
                maxContournumber = i
                maxContour = contours[i]
            else:
                continue

                kernel = np.ones((5, 5), np.uint8)
                # dilation = cv.dilate(final, kernel, iterations=1)
                kernel = np.ones((10, 10), np.uint8)
                # final = cv.morphologyEx(final, cv.MORPH_CLOSE, kernel)
                final = np.uint8(final)
                final = cv.medianBlur(final, (3, 3))
                final = cv.GaussianBlur(final, (1, 1))

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

        # kernel = np.ones((7, 7), np.uint8)
        # final = cv.morphologyEx(final, cv.MORPH_CLOSE, kernel)
        # final = np.uint8(final)

        return final, median, contours, maxArea, maxContournumber, maxContour, hull, totalOilArea

    def boom(self, img, contour, scale=1):
        (x, y), radius = cv.minEnclosingCircle(contour)
        center = (int(x), int(y))
        radius = int(radius * scale)
        # cv.circle(img, center, radius, (0, 255, 255), 2)  # yellow
        return img, center, radius

    def ellipseboom(self, img, hull):
        scale = 1.1
        ellipse = cv.fitEllipse(hull)
        (x, y), (width, height), angle = ellipse
        ellipse2 = (x, y), (width * scale, height * scale), angle
        cv.ellipse(img, ellipse2, (255, 255, 128), 2)  # light blue
        return img, ellipse2

    def rectboom(self, img, hull):
        x, y, w, h = cv.boundingRect(hull)
        cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return img

    def rotrectboom(self, img, hull):
        rect = cv.minAreaRect(hull)
        box = cv.boxPoints(rect)
        box = np.int0(box)
        cv.drawContours(img, [box], 0, (0, 0, 255), -1) //red
        return img

    def blobdetection(self,image):
        params = cv.SimpleBlobDetector_Params()
        # params.minThreshold = 75
        # params.maxThreshold = 255
        # Filter by Area.
        params.filterByArea = True
        params.minArea = 100
        # Filter by Circularity
        params.filterByCircularity = False
        params.minCircularity = 0
        # Filter by Convexity
        params.filterByConvexity = True
        params.minConvexity = 0
        params.maxConvexity = 1999
        # Filter by Inertia
        params.filterByInertia = True
        params.minInertiaRatio = 0
        params.filterByColor = True
        params.blobColor = 10
        detector = cv.SimpleBlobDetector_create(params)
        keypoints = detector.detect(image)

        blank = np.zeros((1, 1))
        blobs = cv.drawKeypoints(image, keypoints, blank, (0, 0, 255), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        return blobs

    def smooth(self,finalimg):
        # Creating the kernel with numpy
        kernel2 = np.ones((5, 5), np.float32) / 25

        # Applying the filter
        finalimg = cv.filter2D(src=finalimg, ddepth=-1, kernel=kernel2)

        kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
        finalimg = cv.morphologyEx(finalimg, cv.MORPH_OPEN, kernel)

        return finalimg

    def label(self,finalimg, ellipse, totalOilArea, circlerad, largestContourArea, hull, px, cm):
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
        cv.putText(finalimg, ('Total Oil Area: ' + str((totalOilAreainCM2)) + ' cm'), (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5,
                   (255, 0, 0), 2)
        cv.putText(finalimg, ('Largest Patch Area: ' + str((largestContourAreainCM)) + ' cm'), (0, 30),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        cv.putText(finalimg, ('Length of Ellipse Boom: ' + str((perimeterOfEllipseBoominCM)) + ' cm'), (0, 45),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 128), 2)
        cv.putText(finalimg, ('Length of Circle Boom: ' + str((perimeterOfCircleBoominCM)) + ' cm'), (0, 60),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        cv.putText(finalimg, ('Length of Hull Boom: ' + str((hullLengthinCM)) + ' cm'), (0, 75), cv.FONT_HERSHEY_SIMPLEX,
                   0.5, (165, 255, 0), 2)
        cv.putText(finalimg, ('Percent of Oil in Container: ' + str((percentOfOil)) + ' %'), (0, 90),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        return finalimg

    def outerEdges(self,img):
        gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        gray_img = cv.medianBlur(gray_img, 3)
        height, width = gray_img.shape
        gray_img = 255 - gray_img
        gray_img[gray_img > 100] = 255
        gray_img[gray_img <= 100] = 0
        # cv.imshow('gray', gray_img)

        edgedimg = cv.Canny(img, 50, 200)
        # cv.imshow('edged', edgedimg)

        # ret, thresh = cv.threshold(img, 170, 255, cv.THRESH_BINARY)
        # cv.imshow("thresh", thresh)
        #
        # threshedge = cv.Canny(thresh, 20, 200)
        # cv.imshow('threshedandedged', threshedge)

        kernel = np.ones((30, 30), np.uint8)
        smoothed = cv.morphologyEx(edgedimg, cv.MORPH_CLOSE, kernel)
        final = np.uint8(smoothed)
        # cv.imshow('smoothed', smoothed)

        externalcontour, hierarchies = cv.findContours(final, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        ContainerContour = []

        for i in range(len(externalcontour)):
            area = cv.contourArea(externalcontour[i])
            if area > 2000:
                ContainerContour.append(externalcontour[i])
            else:
                continue

        uni_hull = []
        length = len(ContainerContour)
        # concatinate poits form all shapes into one array
        cont = np.vstack([ContainerContour[i] for i in range(length)])
        hull = cv.convexHull(cont)
        uni_hull.append(hull)  # <- array as first element of list

        # final =  cv.drawContours(img, uni_hull, -1, (0, 165, 255), 4); ## DRAW THE HULL WHEN YOU NEED TO SEE IT

        # APPROXIMATING THE SHAPE OF THE HULL AS A POLYGON
        # epsilon = 0.12 * cv.arcLength(hull, True)
        # poly =  cv.approxPolyDP(hull, epsilon, True);
        # final = cv.drawContours(final, [poly], -1, (210, 165, 255), 5);

        return uni_hull

    def hull(self,contours):
        hull_list = []
        for i in range(len(contours)):
            hull = cv.convexHull(contours[i])
            hull_list.append(hull)
        return hull_list

    def mergingContourPoints(self, contours):
        list_of_pts = []
        for ctr in contours:
            list_of_pts += [pt[0] for pt in ctr]
        ctr = np.array(list_of_pts).reshape((-1, 1, 1)).astype(np.int32)

        return ctr

#----------------#----------------#----------------#----------------#----------------#----------------#----------------#----------------#----------------#----------------
# final6, median6, contour6, maxContourArea6, element_6, maxContour6, hull6, totalOilArea6  = process2\
#     (scale(cv.imread('Practice Photos/OilSpill6.jpg'), scale=0.5), (17, 9, 154), (43, 27, 181))
# final6, median6, contour6, maxContourArea6, element_6, maxContour6, hull6, totalOilArea6  = process2\
#     (scale(cv.imread('Practice Photos/OilSpill10.jpg'), scale=0.25), (21, 10, 200), (179,  26, 229))

def scale(img, scale=0.2):
    dim1 = int(img.shape[1] * scale)
    dim2 = int(img.shape[0] * scale)
    dims = (dim1, dim2)
    return cv.resize(img, dims, interpolation=cv.INTER_AREA)

pic = scale(cv.imread('C:/School/Science Fair/2022-2023/Oil Spill Pictures/Practice Photos/OilSpill2.2.jpg'), scale=.75)
# pic = scale(cv.imread('C:\GitHub\OCTOPAS\Image Processing\Images\Practice Photos\OilSpill6.jpg'), scale=.75)
# picAddress  = sys.argv[1]
# pic = scale(cv.imread(picAddress), scale=0.5)

img1 = oilSpillImage(pic)
reducedColors = img1.findOil(pic)
# reducedColors = cv.cvtColor(reducedColors, cv.HSV)
final, contours = img1.makePerimeters(pic, reducedColors, areaReq=100)
cv.imshow('reduced', reducedColors)
cv.imshow('final', final)
# final6, median6, contour6, maxContourArea6, element_6, maxContour6, hull6, totalOilArea6  = img1.process2(pic, (17, 9, 154), (43, 27, 181), 1000)
# final6, median6, contour6, maxContourArea6, element_6, maxContour6, hull6, totalOilArea6,   = img1.process2(pic,(27, 54, 60), (87, 255, 255), 2000)

# cv.imshow('median', median6)
# cv.imshow('hsv', hsvversion)

# boom6, center6, radius6 = img1.boom(final6, hull6, scale=1.1)
# ellipseboom6, ellipse6 = img1.ellipseboom(final6, hull6)
# outerHullList = img1.outerEdges(final)
# outerHull = outerHullList[0]
# outerCircle, outerCenter, outerRadius = img1.boom(final6, outerHull, scale=0.9)
# cm = 3
# pixelsOnScreen = outerRadius
# scale = pixelsOnScreen/cm
# print (math.pi * ((pixelsOnScreen/scale) ** 2))
# print()
# labeled6 = img1.label(final6, ellipse6, totalOilArea6, radius6, maxContourArea6, hull6, pixelsOnScreen, cm)
# cv.imshow('final6', final6)
cv.waitKey(0)

