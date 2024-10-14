import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, 
                             QGraphicsPixmapItem, QMainWindow, QPushButton, 
                             QVBoxLayout, QWidget)
from PyQt5.QtGui import QPixmap, QImage, QColor
from PyQt5.QtCore import QRectF, Qt, QPointF


class ImageEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.image = cv2.imread("sample.png")  # Load image using OpenCV
        self.image_copy = self.image.copy()  # Keep a copy of the image for resetting

        # Create graphics view and scene for displaying the image
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.image_item = QGraphicsPixmapItem()
        self.scene.addItem(self.image_item)

        # Display the image
        self.update_image(self.image)

        # Layout and buttons for the main window
        self.delete_button = QPushButton("Delete Region", self)
        self.resize_button = QPushButton("Resize Region", self)
        self.reset_button = QPushButton("Reset", self)

        # Button connections
        self.delete_button.clicked.connect(self.delete_region)
        self.resize_button.clicked.connect(self.resize_region)
        self.reset_button.clicked.connect(self.reset_image)

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.resize_button)
        layout.addWidget(self.reset_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Variables for selection
        self.start_point = None
        self.end_point = None
        self.rect_item = None

        # Enable mouse tracking for the view
        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

    def update_image(self, img):
        """Update the QGraphicsPixmapItem with the current image."""
        height, width, channel = img.shape
        bytes_per_line = 3 * width
        q_img = QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        self.image_item.setPixmap(QPixmap.fromImage(q_img))
        self.view.fitInView(self.image_item, Qt.KeepAspectRatio)

    def eventFilter(self, source, event):
        """Handle mouse events for selecting regions."""
        if event.type() == event.MouseButtonPress and event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.end_point = event.pos()

            # Create or reset the rectangle item
            if self.rect_item is None:
                self.rect_item = self.scene.addRect(QRectF(self.start_point, self.start_point), 
                                                     QColor(255, 0, 0), 
                                                     QColor(255, 0, 0, 50))  # Semi-transparent red
            return True
        elif event.type() == event.MouseMove and self.start_point:
            self.end_point = event.pos()
            # Update the rectangle item
            self.rect_item.setRect(QRectF(self.start_point, self.end_point).normalized())
            return True
        elif event.type() == event.MouseButtonRelease and event.button() == Qt.LeftButton:
            self.end_point = event.pos()
            # Finalize the rectangle coordinates
            self.rect_item.setRect(QRectF(self.start_point, self.end_point).normalized())
            self.start_point = None
            return True
        return False

    def delete_region(self):
        """Delete the area outside the selected rectangle."""
        if self.rect_item:
            rect = self.rect_item.rect().toRect()
            x1, y1 = int(rect.topLeft().x()), int(rect.topLeft().y())
            x2, y2 = int(rect.bottomRight().x()), int(rect.bottomRight().y())

            # Create a mask of the same shape as the image
            mask = np.zeros(self.image.shape, dtype=np.uint8)

            # Set the region inside the rectangle to white (or any color you want)
            mask[y1:y2, x1:x2] = (255, 255, 255)

            # Combine the mask with the original image using bitwise operations
            self.image = cv2.bitwise_and(self.image, mask)

            # Save the cropped image without black bars
            self.save_cropped_image("cropped.png")

            # Update the displayed image
            self.update_image(self.image)

            # Remove the rectangle item from the scene
            self.scene.removeItem(self.rect_item)
            self.rect_item = None

    def save_cropped_image(self, filename="sample.png"):
        """Save the cropped image without black bars."""
        if self.rect_item:
            rect = self.rect_item.rect().toRect()
            x1, y1 = int(rect.topLeft().x()), int(rect.topLeft().y())
            x2, y2 = int(rect.bottomRight().x()), int(rect.bottomRight().y())

            # Ensure coordinates are within image boundaries
            x1 = max(x1, 0)
            y1 = max(y1, 0)
            x2 = min(x2, self.image.shape[1])
            y2 = min(y2, self.image.shape[0])

            # Crop the image to the selected rectangle
            cropped_image = self.image[y1:y2, x1:x2]

            # Save the cropped image
            cv2.imwrite(filename, cropped_image)
            print(f"Cropped image saved as {filename}.")


    def resize_region(self):
        """Resize the selected region."""
        if self.rect_item:
            rect = self.rect_item.rect().toRect()
            x1, y1 = int(rect.left()), int(rect.top())
            x2, y2 = int(rect.right()), int(rect.bottom())
            # Extract the region of interest (ROI)
            roi = self.image[y1:y2, x1:x2]
            # Resize the ROI
            roi_resized = cv2.resize(roi, (0, 0), fx=1.5, fy=1.5)
            # Paste the resized region back into the image
            new_height, new_width = roi_resized.shape[:2]
            self.image[y1:y1 + new_height, x1:x1 + new_width] = roi_resized
            self.update_image(self.image)
            # Remove the rectangle item from the scene
            self.scene.removeItem(self.rect_item)
            self.rect_item = None

    def reset_image(self):
        """Reset the image to its original state."""
        self.image = self.image_copy.copy()
        self.update_image(self.image)
        # Remove the rectangle item from the scene if it exists
        if self.rect_item:
            self.scene.removeItem(self.rect_item)
            self.rect_item = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageEditor()
    window.show()
    sys.exit(app.exec_())
