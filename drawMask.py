import cv2
import numpy as np

# Global variables for mouse drawing on image
drawing = False 
last_point = None  

def Masker(imageFile):

        #debug
        print("Image file is: ", imageFile)


        # mouse drawing callback function
        def draw_on_image(event, x, y, flags, param):
            global drawing, last_point

            if event == cv2.EVENT_LBUTTONDOWN:  # Mouse click starts drawing
                drawing = True
                last_point = (x, y)

            elif event == cv2.EVENT_MOUSEMOVE:  # Mouse movement
                if drawing:
                    cv2.line(image, last_point, (x, y), (255, 255, 255), thickness=6)
                    last_point = (x, y)

            elif event == cv2.EVENT_LBUTTONUP:  # Mouse release stops drawing
                drawing = False
                last_point = None


        # Load the image
        image = cv2.imread(imageFile)
        image_copy = image.copy()  # copy of the original

        cv2.namedWindow("Image")
        cv2.setMouseCallback("Image", draw_on_image)

        def developMask(imagefile):
            image = imagefile
            
            # setting bounds for RGB as WHITE
            bound = np.array([255, 255, 255])
            

            # Create a mask for the target color
            mask = cv2.inRange(image, bound, bound)

            # Apply the mask to the image
            result = cv2.bitwise_and(image, image, mask=mask)

            # Convert non-white areas to black
            black_background = np.zeros_like(image)
            result = cv2.add(black_background, result)
            
            return result


        while True:
            cv2.imshow("Image", image)
            key = cv2.waitKey(1)

            if key == ord('t'):  # Press 't' when done
                cv2.imwrite("mask/mask.jpg", developMask(image))
                break
            elif key == ord('r'):  # Press 'r' to reset the image
                image = image_copy.copy()
            elif key == ord('q'): # Press 'q' to cancel marking image
                break

        cv2.destroyAllWindows()

        return True
