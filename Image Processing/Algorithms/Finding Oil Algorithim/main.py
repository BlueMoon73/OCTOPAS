# Finding the colors using kmeans clustering

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
