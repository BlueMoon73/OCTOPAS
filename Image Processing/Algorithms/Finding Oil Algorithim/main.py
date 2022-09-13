# import cv2 as cv
# import matplotlib.pyplot as plt
#
# # pic = cv.imread("C:/School/Science Fair/2022-2023/Oil Spill Pictures/Practice Photos/OilSpill3.jpg")
# pic = cv.imread("C:/School/Science Fair/2022-2023/Oil Spill Pictures/Practice Photos/OilSpill2.2.jpg")
# img = cv.cvtColor(pic, cv.COLOR_BGR2HSV)
# gray = cv.cvtColor(pic, cv.COLOR_BGR2GRAY)
# # cv.imshow('og pic', pic)
# # cv.imshow('hsv', img)
# # cv.imshow('gray', gray)
# cv.waitKey(0)
#
#
#
# #
# #
# def process(img):
#     # pic = cv.imread(path)
#     cv.imshow('og', img)
#     b, g, r = img[:, :, 0], img[:, :, 1], img[:, :, 2]
#     hist_b = cv.calcHist([b], [0], None, [256], [0, 256])
#     hist_g = cv.calcHist([g], [0], None, [256], [0, 256])
#     hist_r = cv.calcHist([r], [0], None, [256], [0, 256])
#     plt.plot(hist_r, color='r', label="r")
#     plt.plot(hist_g, color='g', label="g")
#     plt.plot(hist_b, color='b', label="b")
#     plt.legend()
#     plt.show()
#     img2 = cv.cvtColor(img, cv.COLOR_BGR2HSV)
#     cv.imshow('hsv', img2)
#     img2 = img
#     h, s, v = img2[:, :, 0], img2[:, :, 1], img2[:, :, 2]
#     hist_h = cv.calcHist([h], [0], None, [256], [0, 256])
#     hist_s = cv.calcHist([s], [0], None, [256], [0, 256])
#     hist_v = cv.calcHist([v], [0], None, [256], [0, 256])
#     plt.plot(hist_h, color='gray', label="h")
#     plt.plot(hist_s, color='g', label="s")
#     plt.plot(hist_v, color='b', label="v")
#     plt.legend()
#     plt.show()
#     # return hist_r, hist_g, hist_b, hist_h, hist_s, hist_v
#
# def histo(img):
#     gray_image = cv.cvtColor([pic], cv.COLOR_BGR2GRAY)
#     histogram = cv.calcHist([gray_image], [0], None, [256], [0, 256])
#     plt.plot(histogram, color='k')
#     plt.show()
#
# process(pic)























import cv2
import numpy as np
from matplotlib import pyplot as plt
from sklearn import cluster

# read image into range 0 to 1
img = cv2.imread('C:/School/Science Fair/2022-2023/Oil Spill Pictures/Practice Photos/OilSpill2.2.jpg')
cv2.imshow('og', img)
img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) / 255
# set number of colors
number = 4

# quantize to 16 colors using kmeans
h, w, c = img.shape
img2 = img.reshape(h*w, c)
kmeans_cluster = cluster.KMeans(n_clusters=number)
kmeans_cluster.fit(img2)
cluster_centers = kmeans_cluster.cluster_centers_
cluster_labels = kmeans_cluster.labels_

# need to scale back to range 0-255 and reshape
img3 = cluster_centers[cluster_labels].reshape(h, w, c)*255
img3 = img3.astype('uint8')

cv2.imshow('reduced colors',img3)
cv2.waitKey(0)
cv2.destroyAllWindows()

# reshape img to 1 column of 3 colors
# -1 means figure out how big it needs to be for that dimension
img4 = img3.reshape(-1,3)

# get the unique colors
colors, counts = np.unique(img4, return_counts=True, axis=0)
print(colors)
print("xxx")
print(counts)
unique = zip(colors,counts)

# function to convert from r,g,b to hex
def encode_hex(color):
    b=color[0]
    g=color[1]
    r=color[2]
    hex = '#'+str(bytearray([r,g,b]).hex())
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