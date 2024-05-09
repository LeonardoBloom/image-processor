from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QProgressDialog, QGraphicsPixmapItem, QMessageBox, QGraphicsScene, QGraphicsPixmapItem, QFileDialog, QGraphicsView, QVBoxLayout, QApplication, QMainWindow, QWidget, QPushButton
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import numpy as np
import cv2
import sys

class ImageEditor(QMainWindow):

    # Class Constructor with variables
    def __init__(self):
        super().__init__()

        self.loaded_program = False
        self.edited = False

        self.graphics_view = QGraphicsView()
        self.scene = QGraphicsScene()

        self.file_name = ""
        self.image_item = QGraphicsPixmapItem()
        self.loaded_image = QPixmap(None)
        self.image_to_edit = None

        self.show_ui()

    # BUILDING THE UI
    def show_ui(self):
        
        central_widget = QWidget()

        win = QMainWindow()
        self.setGeometry(200, 200, 300, 300)
        self.setWindowTitle("Image Processor")

        self.label = QtWidgets.QLabel(self)
        self.label.setText("My First Label")
        self.label.move(50,50)


        # load_button = QPushButton('Load Image', central_widget)
        load_button = QPushButton('Load Image', central_widget)
        load_button.clicked.connect(self.load_image)

        grayscale_button = QPushButton('Convert to Grayscale', central_widget)
        grayscale_button.clicked.connect(self.edit_grayscale)

        warp_button = QPushButton('Content-Dependent Warping', central_widget)
        warp_button.clicked.connect(self.content_dependent_warping)

        mark_button = QPushButton('Mark for Deletion or Resizing', central_widget)
        mark_button.clicked.connect(self.mark_for_deletion_resizing)

        cartoon_button = QPushButton('Apply Cartoon Filter', central_widget)
        cartoon_button.clicked.connect(self.edit_cartoon_filter)

        save_button = QPushButton('Save Image', central_widget)
        save_button.clicked.connect(self.save_image)

        reset_button = QPushButton('Reset Image', central_widget)
        reset_button.clicked.connect(self.reset_image)

        layout = QVBoxLayout()
        layout.addWidget(self.graphics_view)
        layout.addWidget(load_button)
        layout.addWidget(grayscale_button)
        layout.addWidget(warp_button)
        layout.addWidget(mark_button)
        layout.addWidget(cartoon_button)
        layout.addWidget(save_button)
        layout.addWidget(reset_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle('Image Editor')

        self.loaded_program = True
        self.resizeEvent = self.on_resize

    def on_resize(self, event):
        if self.loaded_program != True:
            self.display_loaded_image()    
        
    # grab an image file 
    def load_image(self):
        options = QFileDialog.Options()
        self.file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.svg);;All Files (*)", options=options)
        print("loaded: ", self.file_name) # debug

        # debug
        # print("image to edit: ", self.image_to_edit) 

        if self.file_name:
            
            self.image_path = self.file_name
            # self.original_image = ""
            self.display_loaded_image()

    def reset_image(self):
        self.image_to_edit = None
        self.edited = False
        self.display_loaded_image()

    def no_loaded_image(self):
        # alert box for when no image is loaded
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Alert")
        msg_box.setText("No Image Loaded. Please Load an Image")
        msg_box.exec_()

    # show image on the screen
    def display_loaded_image(self):
        if hasattr(self, 'image_path') and self.image_path or self.edited:
            if self.edited:
                self.loaded_image = self.image_to_edit
            else:
                self.loaded_image = QPixmap(self.image_path)
                self.image_to_edit = self.loaded_image

            print("this is the edited image in def display: ", self.image_to_edit )
            self.label.setPixmap(self.loaded_image.scaled(self.label.size(), aspectRatioMode=Qt.KeepAspectRatio))
            
            # clear previous image
            self.scene.clear()

            # create a new item
            self.image_item = QGraphicsPixmapItem(self.loaded_image.scaled(self.graphics_view.size(), aspectRatioMode = Qt.KeepAspectRatio))
            
            self.scene.addItem(self.image_item)
            self.graphics_view.setScene(self.scene)
        else:
            # alert box for when no image is loaded
            self.no_loaded_image

    def save_image(self):
        if hasattr(self, 'image_path') and self.image_path:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG (*.png);;JPEG (*.jpg *.jpeg);;Bitmap (*.bmp)")

            if save_path:
                pixmap = self.image_item.pixmap()
                if pixmap.save(save_path):
                    QMessageBox.information(self, "Image Saved", "Image saved successfully")
                else:
                    QMessageBox.warning(self, "Error", "Failed to save image")
            

    # grayscale filter
    def edit_grayscale(self):
        # load image into openCV format
        load_image = cv2.imread(self.file_name)

        if self.file_name:

            #convert image into greyscale
            image = cv2.cvtColor(load_image, cv2.COLOR_BGR2GRAY)

            #debug
            # cv2.imshow("window", image)
            # cv2.waitKey(0)
            # print(image)

            # convert image into something QPixmap can read
            print("crashed before image.shape")
            height, width  = image.shape
            bytesPerLine = width
            Q_image = QImage(image.data, width, height, bytesPerLine, QImage.Format_Grayscale8)

            # save into image to edit
            # self.image_to_edit = None
            print("crashed at save to image_to_edit")
            self.image_to_edit = QPixmap.fromImage(Q_image)
            print("crashed before after edit")
            self.edited = True

            print("just before display loaded image")
            self.display_loaded_image()
            
                # img_gray = cv2.cvtColor(self.image_to_edit)
        else:
            # alert box for when no image is loaded
            msg_box = QMessageBox()
            msg_box.setWindowTitle("No Image Loaded")
            msg_box.setText("pls bro")
            msg_box.exec_()

    # cartoon filter
    def edit_cartoon_filter(self):

        if self.file_name:
            load_image = cv2.imread(self.file_name)

            # convert the RGB image into grayscale
            grey = cv2.cvtColor(load_image, cv2.COLOR_BGR2GRAY)
            # reduce noise with median blur
            grey = cv2.medianBlur(grey, 5)
            # detect edges using adaptive thresholding
            edges = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

            # cartoonizing
            color = cv2.bilateralFilter(load_image, 10, 250, 250)
            color = cv2.cvtColor(color, cv2.COLOR_RGB2BGR)

            cartoon = cv2.bitwise_and(color, color, mask = edges)
            # print(cartoon)
            # cv2.imshow("Image", cartoon)

            # cv2.waitKey(0)

            # cartoon = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
            
            height, width, channel  = cartoon.shape
            bytesPerLine = 3 * width
            Q_image = QImage(cartoon.data, width, height, bytesPerLine, QImage.Format_RGB888)

            # save into image to edit
            # debug
            print("crashed at save to image_to_edit in cartoonize") 
            self.image_to_edit = QPixmap.fromImage(Q_image)
            self.edited = True
            self.display_loaded_image()
        else:
            self.no_loaded_image()

    def content_dependent_warping(self):
        print("Content-Dependent Warping")

    def mark_for_deletion_resizing(self):
        print("Mark for deletion and resizing")


# main loop
if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = ImageEditor()
    editor.show()
    sys.exit(app.exec_())


