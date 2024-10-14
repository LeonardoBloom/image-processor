import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QProgressBar, QLabel, QWidget

class Cartoonizer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the GUI components
        self.setWindowTitle("Cartoonizer with Progress Bar")
        self.setGeometry(100, 100, 600, 150)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(30, 40, 540, 25)

        self.label = QLabel("Cartoonizing...", self)
        self.label.setGeometry(30, 10, 540, 25)

        self.button = QPushButton("Start Cartoonization", self)
        self.button.setGeometry(230, 80, 140, 30)
        self.button.clicked.connect(self.cartoonize_image)

    def apply_bilateral_filter(self, image, iterations=4, sigma_s=3, sigma_r=4.25):
        """ Apply bilateral filtering with progress updates. """
        for i in range(iterations):
            image = cv2.bilateralFilter(image, d=-1, sigmaColor=sigma_r * 255, sigmaSpace=sigma_s)
            self.update_progress_bar(i + 1, iterations, "Bilateral Filtering")
        return image

    def apply_dog_filter(self, image, k=1.6, sigma=1.0):
        """ Apply Difference of Gaussians (DoG) filter for edge detection. """
        blur1 = cv2.GaussianBlur(image, (0, 0), sigma)
        blur2 = cv2.GaussianBlur(image, (0, 0), sigma * k)
        dog = blur1 - blur2
        dog = cv2.normalize(dog, None, 0, 255, cv2.NORM_MINMAX)
        return dog

    def compute_structure_tensor(self, image, sigma=1.0):
        """ Compute the structure tensor to estimate local orientations. """
        Ix = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=5)
        Iy = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=5)
        Ixx = cv2.GaussianBlur(Ix ** 2, (0, 0), sigma)
        Ixy = cv2.GaussianBlur(Ix * Iy, (0, 0), sigma)
        Iyy = cv2.GaussianBlur(Iy ** 2, (0, 0), sigma)

        eigenvalues = np.zeros((image.shape[0], image.shape[1], 2))
        eigenvectors = np.zeros((image.shape[0], image.shape[1], 2, 2))

        for y in range(image.shape[0]):
            for x in range(image.shape[1]):
                J = np.array([[Ixx[y, x], Ixy[y, x]], [Ixy[y, x], Iyy[y, x]]])
                e_vals, e_vecs = np.linalg.eig(J)
                eigenvalues[y, x] = e_vals
                eigenvectors[y, x] = e_vecs

        return eigenvalues, eigenvectors

    def flow_based_smoothing(self, image, eigenvectors, iterations=1, sigma=3.0):
        """ Apply flow-based smoothing with progress updates. """
        flow_smoothed = image.copy().astype(np.float32)
        for iteration in range(iterations):
            for y in range(1, image.shape[0] - 1):
                for x in range(1, image.shape[1] - 1):
                    v = eigenvectors[y, x]
                    dx = int(v[0, 0])
                    dy = int(v[1, 0])
                    new_x = np.clip(x + dx, 0, image.shape[1] - 1)
                    new_y = np.clip(y + dy, 0, image.shape[0] - 1)
                    flow_smoothed[y, x] = (flow_smoothed[new_y, new_x] + flow_smoothed[y, x]) * 0.5

            self.update_progress_bar(iteration + 1, iterations, "Flow-Based Smoothing")
        flow_smoothed = cv2.normalize(flow_smoothed, None, 0, 255, cv2.NORM_MINMAX)
        return flow_smoothed.astype(np.uint8)

    def cartoonize(self, image):
        """ Main cartoonization function. """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        eigenvalues, eigenvectors = self.compute_structure_tensor(gray)

        # Apply bilateral filtering with progress updates
        filtered_image = self.apply_bilateral_filter(image)

        # Apply DoG (Difference of Gaussians) for edge detection
        edges = self.apply_dog_filter(gray)

        # Apply flow-based smoothing along the structure tensor
        smoothed_edges = self.flow_based_smoothing(edges, eigenvectors)

        # Combine edges and smoothed image
        edges = cv2.adaptiveThreshold(smoothed_edges.astype(np.uint8), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        cartoon = cv2.bitwise_and(filtered_image, filtered_image, mask=edges)

        return cartoon

    def cartoonize_image(self):
        """ Load image, apply cartoonization, and show progress. """
        self.progress_bar.setValue(0)
        image = cv2.imread("sample.png")  # Replace with your image path

        if image is None:
            self.label.setText("Failed to load image.")
            return

        cartoon_image = self.cartoonize(image)

        # Show the cartoonized image in a window
        cv2.imshow("Cartoonized Image", cartoon_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def update_progress_bar(self, current_step, total_steps, process_name):
        """ Update the progress bar. """
        progress = int((current_step / total_steps) * 100)
        self.progress_bar.setValue(progress)
        self.label.setText(f"{process_name}... {progress}% Complete")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Cartoonizer()
    window.show()
    sys.exit(app.exec_())
