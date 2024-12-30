import cv2
import sys
import numpy as np

def cartoonize(image):
    """
    Perform color quantization on an image using OpenCV's k-means clustering.

    Args:
        image: Input image (numpy array).

    Returns:
        Quantized image.
    """
    print("fff0")
    k=8
    # Convert image to a two-dimensional array (pixels x RGB)
    image = cv2.imread(image)
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    data = image.reshape((-1, 3))  # Reshape to 2D array
    print("fff-1")
    data = np.float32(data)       # Convert to float32 for k-means
    print("fff")

    # Define criteria for the k-means algorithm
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)

    # Apply k-means
    _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    print("fff2")

    # Convert the cluster centers to uint8 (integer values)
    centers = np.uint8(centers)
    print("fff3")

    # Map each pixel to the nearest cluster center
    quantized_data = centers[labels.flatten()]
    quantized_image = quantized_data.reshape(image.shape)  # Reshape back to original image shape
    image= quantized_image
    # convert the RGB image into grayscale
    rgb_to_grayscale = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Reduce noise using median blur
    rgb_to_grayscale = cv2.medianBlur(rgb_to_grayscale, 1)

    # edge detection using adaptive threshold to overcome false prediction and illumination problems
    edges = cv2.adaptiveThreshold(rgb_to_grayscale, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

    # apply bilateral filter
    color = cv2.bilateralFilter(image, 9, 250, 250)

    
    # adjust color orders to prevent image from showing blue
    # color = cv2.cvtColor(color, cv2.COLOR_RGB2BGR)

    # finalize application of filter via bitwise and
    cartoon = cv2.bitwise_and(color, color, mask = edges)
    cartoon = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB

    return cartoon

# def cartoonize(image):

#     # get chosen image
#     image = cv2.imread(image)

#     # convert the RGB image into grayscale
#     rgb_to_grayscale = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

#     # Reduce noise using median blur
#     blurImages = cv2.medianBlur(rgb_to_grayscale, 1)

#     # edge detection using adaptive threshold to overcome false prediction and illumination problems
#     edges = cv2.adaptiveThreshold(rgb_to_grayscale, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

#     # apply bilateral filter
#     color = cv2.bilateralFilter(image, 9, 200, 200)
#     # adjust color orders to prevent image from showing blue
#     color = cv2.cvtColor(color, cv2.COLOR_RGB2BGR)

#     # finalize application of filter via bitwise and
#     cartoon = cv2.bitwise_and(color, color, mask = edges)

#     return cartoon



# # cartoonize = cartoon('sample3.jpg')
# # cv2.imshow("Image", cartoonize)
# # cv2.waitKey(0)
