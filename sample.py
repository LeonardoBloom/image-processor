import cv2
import numpy as np
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QWidget, QFileDialog
from PyQt5.QtGui import QPixmap, QImage

class ImageProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.image_label = QLabel()
        self.original_image = None

        self.initUI()

    def initUI(self):
        # Set up main window
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Image Processor')

        # Create widgets
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 300)

        open_button = QPushButton('Open Image', self)
        open_button.clicked.connect(self.openImage)

        distort_button = QPushButton('Content Distortion', self)
        distort_button.clicked.connect(self.content_dependent_distortion)

        cartoon_button = QPushButton('Cartoon Filter', self)
        cartoon_button.clicked.connect(self.cartoon_filter)

        swap_button = QPushButton('Patch Swapping', self)
        swap_button.clicked.connect(self.patch_swapping)

        save_button = QPushButton('Save Image', self)
        save_button.clicked.connect(self.saveImage)

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(open_button)
        layout.addWidget(distort_button)
        layout.addWidget(cartoon_button)
        layout.addWidget(swap_button)
        layout.addWidget(save_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def openImage(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp *.jpeg);;All Files (*)", options=options)
        
        if file_name:
            self.original_image = cv2.imread(file_name)
            self.displayImage(self.original_image)

    def displayImage(self, image):
        if image is not None:
            # Ensure the image is in the correct format (BGR)
            if image.dtype == np.uint8 and image.ndim == 3:
                height, width, channel = image.shape
                bytes_per_line = 3 * width
                q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_BGR888)  # BGR format for OpenCV
                pixmap = QPixmap.fromImage(q_image.rgbSwapped())  # Swapping channels to RGB
                self.image_label.setPixmap(pixmap)
                self.image_label.show()

    def content_dependent_distortion(self):
        if self.original_image is not None:
            # Create a distortion map with random displacements
            distortion_map = np.random.uniform(-10, 10, self.original_image.shape[:2])

            h, w, _ = self.original_image.shape
            x, y = np.meshgrid(range(w), range(h))
            x_distorted = x + distortion_map
            y_distorted = y + distortion_map

            # Use remap to apply the distortion
            distorted_image = cv2.remap(self.original_image, x_distorted.astype(np.float32), y_distorted.astype(np.float32), interpolation=cv2.INTER_LINEAR)

            self.displayImage(distorted_image)

    def cartoon_filter(self):
        if self.original_image is not None:
            gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
            edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

            color = cv2.bilateralFilter(self.original_image, 9, 300, 300)
            cartoon = cv2.bitwise_and(color, color, mask=edges)

            self.displayImage(cartoon)

    def patch_swapping(self):
        if self.original_image is not None:
            # Load a second image for patch swapping (you can modify this to fit your needs)
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_name, _ = QFileDialog.getOpenFileName(self, "Open Image for Patch Swapping", "", "Image Files (*.png *.jpg *.bmp *.jpeg);;All Files (*)", options=options)

            if file_name:
                swap_image = cv2.imread(file_name)

                if swap_image is not None and swap_image.shape == self.original_image.shape:
                    # Define the region for swapping (you can modify this to fit your needs)
                    y1, y2, x1, x2 = 100, 300, 200, 400

                    # Extract patches from the original image and the swap image
                    patch_original = self.original_image[y1:y2, x1:x2].copy()
                    patch_swap = swap_image[y1:y2, x1:x2].copy()

                    # Swap the patches
                    self.original_image[y1:y2, x1:x2] = patch_swap
                    swap_image[y1:y2, x1:x2] = patch_original

                    # Display the images after patch swapping
                    self.displayImage(self.original_image)
                else:
                    print("Error: The swap image has a different size than the original image.")
            else:
                print("Error: Could not load the swap image.")

    def saveImage(self):
        if self.original_image is not None:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)", options=options)

            if file_name:
                # Ensure the image is in the correct format (BGR)
                if self.original_image.dtype == np.uint8 and self.original_image.ndim == 3:
                    # Get the currently displayed image
                    displayed_image = self.image_label.pixmap().toImage()
                    # Convert the QImage to a NumPy array
                    displayed_np = np.array(displayed_image)
                    # Convert BGR to RGB before saving
                    rgb_image = cv2.cvtColor(displayed_np, cv2.COLOR_BGR2RGB)

                    # Ensure the file extension is valid
                    valid_extensions = ['.png', '.jpg', '.jpeg']
                    if not any(file_name.lower().endswith(ext) for ext in valid_extensions):
                        file_name += '.png'  # Default to PNG if no valid extension is found

                    # Save the image
                    cv2.imwrite(file_name, rgb_image)
                    print("Image saved successfully.")
                else:
                    print("Error: Image has an unsupported format.")
            else:
                print("Error: Could not save the image.")
        else:
            print("Error: No image to save.")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageProcessorApp()
    ex.show()
    sys.exit(app.exec_())
