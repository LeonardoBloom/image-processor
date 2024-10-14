from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QProgressDialog, QGraphicsPixmapItem, QMessageBox, QGraphicsScene, QGraphicsPixmapItem, QFileDialog, QGraphicsView, QVBoxLayout, QApplication, QMainWindow, QWidget, QPushButton
from PyQt5.QtGui import QPixmap, QImage, QPen, QPainter, QColor
from PyQt5.QtCore import Qt, QRect, QRectF, QPointF
import numpy as np
import cv2
import sys
import Cartoon

class ImageEditor(QMainWindow):

    # Class Constructor with variables
    def __init__(self):
        super().__init__()

        self.loaded_program = False
        self.edited = False

        self.scene = QGraphicsScene()
        self.graphics_view = QGraphicsView()

        self.file_name = ""
        self.image_item = QGraphicsPixmapItem()
        self.theImage = None
        self.loaded_image = QPixmap(None)
        self.image_to_edit = None

        # Additional state for marking areas
        self.marked_regions = []  # Stores marked regions (rectangles)
        self.marking_mode = False


        # Variables for selection
        self.start_point = None
        self.end_point = None
        self.rect_item = None


        self.show_ui()

    # BUILDING THE UI
    def show_ui(self):
        
        central_widget = QWidget()

        win = QMainWindow()
        self.setGeometry(200, 200, 300, 300)
        self.setWindowTitle("Image Processor")

        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)

        self.label.setText("My First Label")
        self.label.move(50,50)


        # load_button = QPushButton('Load Image', central_widget)
        load_button = QPushButton('Load Image', central_widget)
        load_button.clicked.connect(self.load_image)

        grayscale_button = QPushButton('Convert to Grayscale', central_widget)
        grayscale_button.clicked.connect(self.edit_grayscale)

        warp_button = QPushButton('Content-Dependent Warping', central_widget)
        # warp_button.clicked.connect(self.content_dependent_warping)

        self.mark_button = QPushButton('Mark for Deletion/Resizing OFF', central_widget)
        self.mark_button.clicked.connect(self.toggle_marking_mode)

        delete_button = QPushButton('Crop Region of Marked Areas', central_widget)
        delete_button.clicked.connect(self.delete_area)

        resize_button = QPushButton('Resize Marked Areas', central_widget)
        resize_button.clicked.connect(self.resize_marked_areas)

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
        layout.addWidget(self.mark_button)
        layout.addWidget(delete_button)
        layout.addWidget(resize_button)
        layout.addWidget(cartoon_button)
        layout.addWidget(save_button)
        layout.addWidget(reset_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle('Image Editor')

        self.loaded_program = True
        self.resizeEvent = self.on_resize

    

    def mouseHandler(self, source, event):
        # handle mouse events for cropping
        if event.type() == event.MouseButtonPress and event.button() == Qt.LeftButton:
            self.startPoint = event.pos()
            return True
        
        if event.type() == event.MouseMove and self.startPoint:
            self.endPoint = event.pos()
            self.rect = QRectF(QPointF(self.startPoint), QPointF(self.endPoint))
            self.display_loaded_image()
            return True
        
        if event.type() == event.MouseButtonRelease and event.button() == Qt.LeftButton:
            self.endPoint = event.pos()
            self.rect = QRectF(QPointF(self.startPoint), QPointF(self.endPoint))
            self.startPoint = None

            return True
        
        return False
    
    def drawRectangle(self, event):
        # draw rectangle
        if self.rectangle:
            painter = QPainter(self.graphics_view.viewport())
            painter.setPen(Qt.red)
            painter.drawRect(self.rectangle)


    

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
            self.theImage = self.file_name
            
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
        # display original image or edited image
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
            self.no_loaded_image()





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
            self.no_loaded_image()


    # cartoon filter
    def edit_cartoon_filter(self):

        if self.theImage:
            # calls module to cartoon filter
            cartoon = Cartoon.cartoonize(self.theImage)
        
            # Print or display the cartoon image
            height, width, channel = cartoon.shape
            bytesPerLine = 3 * width
            Q_image = QImage(cartoon.data, width, height, bytesPerLine, QImage.Format_RGB888)

            # Save into image to edit
            print("crashed at save to image_to_edit in cartoonize")
            self.image_to_edit = QPixmap.fromImage(Q_image)
            self.edited = True
            self.display_loaded_image()

        else:
            # alert box for when no image is loaded
            self.no_loaded_image()


    def toggle_marking_mode(self):
        if self.theImage:
            # Toggles the marking mode to allow selecting regions
            self.marking_mode = not self.marking_mode
            if self.marking_mode:
                print("Marking mode ON")
                self.mark_button.setText("Mark for Deletion/Resizing ON")
                self.graphics_view.setMouseTracking(True)
                self.graphics_view.viewport().installEventFilter(self)
                self.rect_item = None
            else:
                print("Marking mode OFF")
                self.mark_button.setText("Mark for Deletion/Resizing: OFF")
                self.graphics_view.setMouseTracking(False)
                self.graphics_view.viewport().installEventFilter(self)
                if self.rect_item:
                    self.scene.removeItem(self.rect_item)
                    self.rect_item = None
        else:
            self.no_loaded_image()




    def mouseEventHandler(self, source, event):
        """Handle mouse events for selecting regions."""
        if self.marking_mode:
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





    def delete_area(self):

        if self.file_name:
            load_image = cv2.imread(self.file_name)
            """Delete the area outside the selected rectangle."""
            if self.rect_item:
                rect = self.rect_item.rect().toRect()
                x1, y1 = int(rect.topLeft().x()), int(rect.topLeft().y())
                x2, y2 = int(rect.bottomRight().x()), int(rect.bottomRight().y())

                # Create a mask of the same shape as the image
                mask = np.zeros(load_image.shape, dtype=np.uint8)

                # Set the region inside the rectangle to white (or any color you want)
                mask[y1:y2, x1:x2] = (255, 255, 255)

                # Combine the mask with the original image using bitwise operations
                load_image = cv2.bitwise_and(load_image, mask)
                print("load image: ", load_image)
                # Update the displayed image

                """Save the cropped image without black bars."""
                rect = self.rect_item.rect().toRect()
                x1, y1 = int(rect.topLeft().x()), int(rect.topLeft().y())
                x2, y2 = int(rect.bottomRight().x()), int(rect.bottomRight().y())

                # Ensure coordinates are within image boundaries
                x1 = max(x1, 0)
                y1 = max(y1, 0)
                x2 = min(x2, load_image.shape[1])
                y2 = min(y2, load_image.shape[0])

                # Crop the image to the selected rectangle
                cropped_image = load_image[y1:y2, x1:x2]
                
                cv2.imwrite("croppedImg.png", cropped_image)
                
                cropped = QPixmap("croppedImg.png")
                self.image_to_edit = cropped
                self.edited = True

                self.marking_mode = False

                self.display_loaded_image() 

                # self.display_loaded_image(cropped_image)

                # # Remove the rectangle item from the scene
                # self.scene.removeItem(self.rect_item)
                # self.rect_item = None
        else:
            self.no_loaded_image()


# main loop
if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = ImageEditor()
    editor.show()
    sys.exit(app.exec_())


