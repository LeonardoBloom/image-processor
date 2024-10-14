import cv2
import sys

def cartoonize(image):

    # get chosen image
    image = cv2.imread(image)

    # convert the RGB image into grayscale
    rgb_to_grayscale = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Reduce noise using median blur
    blurImages = cv2.medianBlur(rgb_to_grayscale, 1)

    # edge detection using adaptive threshold to overcome false prediction and illumination problems
    edges = cv2.adaptiveThreshold(rgb_to_grayscale, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

    # apply bilateral filter
    color = cv2.bilateralFilter(image, 9, 200, 200)
    # adjust color orders to prevent image from showing blue
    color = cv2.cvtColor(color, cv2.COLOR_RGB2BGR)

    # finalize application of filter via bitwise and
    cartoon = cv2.bitwise_and(color, color, mask = edges)

    return cartoon



# cartoonize = cartoon('sample3.jpg')
# cv2.imshow("Image", cartoonize)
# cv2.waitKey(0)
