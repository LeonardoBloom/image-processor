import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QFileDialog, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QWidget, QProgressDialog
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRectF
import cv2
import numpy as np
from PIL import Image, ImageQt

class ImageEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.image_path = None
        self.original_image = None
        self.modified_image = None

        self.image_label = QLabel()
        self.graphics_view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.image_item = QGraphicsPixmapItem()

        self.marking_start = None

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()

        load_button = QPushButton('Load Image', central_widget)
        load_button.clicked.connect(self.load_image)

        grayscale_button = QPushButton('Convert to Grayscale', central_widget)
        grayscale_button.clicked.connect(self.convert_to_grayscale)

        warp_button = QPushButton('Content-Dependent Warping', central_widget)
        warp_button.clicked.connect(self.content_dependent_warping)

        mark_button = QPushButton('Mark for Deletion or Resizing', central_widget)
        mark_button.clicked.connect(self.mark_for_deletion_resizing)

        cartoon_button = QPushButton('Apply Cartoon Filter', central_widget)
        cartoon_button.clicked.connect(self.apply_cartoon_filter)

        save_button = QPushButton('Save Image', central_widget)
        save_button.clicked.connect(self.save_image)

        layout = QVBoxLayout()
        layout.addWidget(load_button)
        layout.addWidget(grayscale_button)
        layout.addWidget(warp_button)
        layout.addWidget(mark_button)
        layout.addWidget(cartoon_button)
        layout.addWidget(save_button)
        layout.addWidget(self.graphics_view)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Image Editor')
        self.show()

    def load_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.svg);;All Files (*)", options=options)

        if file_name:
            self.image_path = file_name
            self.original_image = cv2.imread(self.image_path)
            self.display_image()

    def display_image(self):
        q_image = self.convert_cv_to_qimage(self.original_image)
        pixmap = QPixmap.fromImage(q_image)
        self.image_item.setPixmap(pixmap)
        self.scene.clear()
        self.scene.addItem(self.image_item)
        self.graphics_view.setScene(self.scene)

    def convert_cv_to_qimage(self, cv_image):
        height, width, channel = cv_image.shape
        bytes_per_line = 3 * width
        q_image = QImage(cv_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return q_image.rgbSwapped()

    def convert_to_grayscale(self):
        if self.original_image is not None:
            progressDialog = QProgressDialog("Converting to Grayscale...", None, 0, 0, self)
            progressDialog.setWindowModality(Qt.WindowModal)
            progressDialog.show()

            grayscale_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
            h, w = grayscale_image.shape
            q_image = QImage(grayscale_image.data, w, h, w, QImage.Format_Grayscale8)

            self.image_item = QGraphicsPixmapItem(QPixmap.fromImage(q_image))

            progressDialog.close()
            self.scene.clear()
            self.scene.addItem(self.image_item)
            self.graphics_view.setScene(self.scene)

    def content_dependent_warping(self):
        if self.original_image is not None:
            progressDialog = QProgressDialog("Performing Content-Dependent Warping...", None, 0, 0, self)
            progressDialog.setWindowModality(Qt.WindowModal)
            progressDialog.show()

            # Example: Seam Carving algorithm for content-aware image resizing
            energy_map = self.calculate_energy_map()

            for _ in range(100):  # Arbitrary number of iterations
                seam = self.find_vertical_seam(energy_map)
                self.remove_vertical_seam(seam)

            progressDialog.close()
            self.display_image()

    def calculate_energy_map(self):
        gray_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        sobel_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
        energy_map = np.abs(sobel_x) + np.abs(sobel_y)
        return energy_map

    def find_vertical_seam(self, energy_map):
        rows, cols = energy_map.shape
        dp = energy_map.copy()

        for i in range(1, rows):
            for j in range(cols):
                if j == 0:
                    dp[i, j] += min(dp[i - 1, j], dp[i - 1, j + 1])
                elif j == cols - 1:
                    dp[i, j] += min(dp[i - 1, j - 1], dp[i - 1, j])
                else:
                    dp[i, j] += min(dp[i - 1, j - 1], dp[i - 1, j], dp[i - 1, j + 1])

        seam = np.zeros(rows, dtype=int)
        seam[-1] = np.argmin(dp[-1, :])

        for i in range(rows - 2, -1, -1):
            j = seam[i + 1]
            if j == 0:
                seam[i] = np.argmin(dp[i, :2])
            elif j == cols - 1:
                seam[i] = np.argmin(dp[i, -2:]) + cols - 2
            else:
                seam[i] = np.argmin(dp[i, j - 1:j + 2]) + j - 1

        return seam

    def remove_vertical_seam(self, seam):
        rows, cols, _ = self.original_image.shape
        result_image = np.zeros((rows, cols - 1, 3), dtype=np.uint8)

        for i in range(rows):
            result_image[i, :, :] = np.delete(self.original_image[i, :, :], seam[i], axis=0)

        self.original_image = result_image

    def mark_for_deletion_resizing(self):
        if self.original_image is not None:
            pen = QPen(QColor(255, 0, 0))  # Red pen for marking
            pen.setWidth(2)
            self.scene.setSceneRect(0, 0, self.image_item.pixmap().width(), self.image_item.pixmap().height())
            self.graphics_view.setScene(self.scene)
            self.graphics_view.setSceneRect(0, 0, self.image_item.pixmap().width(), self.image_item.pixmap().height())
            self.graphics_view.setRenderHint(QPainter.Antialiasing, True)
            self.graphics_view.setRenderHint(QPainter.SmoothPixmapTransform, True)
            self.graphics_view.setRenderHint(QPainter.HighQualityAntialiasing, True)
            self.graphics_view.setRenderHint(QPainter.TextAntialiasing, True)
            self.graphics_view.setRenderHint(QPainter.NonCosmeticDefaultPen, True)
            self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            self.graphics_view.viewport().update()
            self.graphics_view.viewport().setCursor(Qt.CrossCursor)
            self.graphics_view.setScene(self.scene)

            self.scene.mousePressEvent = self.mouse_press_event
            self.scene.mouseMoveEvent = self.mouse_move_event

    def mouse_press_event(self, event):
        if self.original_image is not None:
            self.marking_start = event.scenePos()

    def mouse_move_event(self, event):
        if self.marking_start is not None:
            pen = QPen(QColor(255, 0, 0))  # Red pen for marking
            pen.setWidth(2)
            rect = QRectF(self.marking_start, event.scenePos())
            self.scene.clear()
            self.scene.addItem(self.image_item)
            self.scene.addRect(rect, pen)
            self.graphics_view.setScene(self.scene)

    def apply_cartoon_filter(self):
        if self.original_image is not None:
            # Implement cartoon filter using bilateral filter and edge detection
            gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
            gray = cv2.medianBlur(gray, 5)
            edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
            color = cv2.bilateralFilter(self.original_image, 9, 300, 300)
            self.modified_image = cv2.bitwise_and(color, color, mask=edges)
            self.display_image()

    def save_image(self):
        if self.modified_image is not None:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff);;All Files (*)", options=options)
            if file_name:
                progressDialog = QProgressDialog("Saving Image...", None, 0, 0, self)
                progressDialog.setWindowModality(Qt.WindowModal)
                progressDialog.show()

                # Save the modified image
                cv2.imwrite(file_name, self.modified_image)

                progressDialog.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = ImageEditor()
    sys.exit(app.exec_())

