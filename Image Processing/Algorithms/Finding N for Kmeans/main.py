# Elbow method for finding optimal method to find K for the kmeans clustering. 

from matplotlib import pyplot as plt
from sklearn import cluster
import cv2 as cv
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from kneed import KneeLocator

path = "C:\[2] Oil Spill.jpg"


# path = "C:\Practice Pictures (SF)\OilSpill5.jpg"

# path = "C:\Practice Pictures (SF)\OilSpill5.jpg"
# path = "C:\Practice Pictures (SF)\oilspillimg175.jpg"
# path = "C:\Practice Pictures (SF)\rgb.jpg"
# path = "rgb.jpg"


# ![](../../Practice Pictures (SF)/rgb.jpg)

def reshapeImg(imgPath):
    img = cv.imread(imgPath)
    cv.cvtColor(img, cv.COLOR_BGR2HSV) / 255
    h, w, c = img.shape
    return img.reshape(h * w, c)


def simplifyData(img):
    mms = MinMaxScaler()
    mms.fit(img)
    return mms.transform(img)  # data transformed

def findElbow(x, y, direction):
    kn = KneeLocator(x, y, curve='convex', direction=direction)
    return kn.knee

def elbowGraph(data_transformed, rangeNum):
    SumOfSquaredDistances = []

    x = range(1, rangeNum)
    for i in x:
        print(i)
        km = KMeans(n_clusters=i)
        km.fit(data_transformed)
        SumOfSquaredDistances.append(km.inertia_)
    optimalNum = findElbow(x, SumOfSquaredDistances, 'decreasing')
    print("Optimal Number of Clusters is:")
    print(optimalNum)
    plt.plot(x, SumOfSquaredDistances, 'bx-')
    plt.xlabel('k')
    plt.ylabel('Sum_of_squared_distances')
    plt.title('Elbow Method For Optimal k')
    plt.vlines(optimalNum, plt.ylim()[0], plt.ylim()[1], linestyles='dashed')
    plt.savefig('Output/ElbowGraph.png')
    plt.show()





rangeNum = 7
elbowGraph(simplifyData(reshapeImg(path)), rangeNum)

# print(findElbow(rangeNum, y))
