import cv2

# Load the image
image = cv2.imread('sample.png')

# Resize the image
resized_image = cv2.resize(image, (300, 200))

cv2.imshow("image", resized_image)
cv2.waitKey(0)