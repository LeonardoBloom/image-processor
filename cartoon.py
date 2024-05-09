import cv2
import sys

load_image = cv2.imread('sample.png')
print(load_image)

# convert the RGB image into grayscale
grey = cv2.cvtColor(load_image, cv2.COLOR_RGB2GRAY)
# reduce noise with median blur
grey = cv2.medianBlur(grey, 5)
# detect edges using adaptive thresholding
edges = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

# cartoonizing
color = cv2.bilateralFilter(load_image, 10, 250, 250)
# color = cv2.cvtColor(color, cv2.COLOR_RGB2RGB)

cartoon = cv2.bitwise_and(color, color, mask = edges)


print(cartoon)
cv2.imshow("Image", cartoon)

cv2.waitKey(0)
