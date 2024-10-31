from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QStyle, QLabel, QRadioButton, QDialog, QDialogButtonBox, QLineEdit, QGraphicsPixmapItem, QMessageBox, QGraphicsScene, QGraphicsPixmapItem, QFileDialog, QGraphicsView, QVBoxLayout, QApplication, QMainWindow, QWidget, QPushButton
from PyQt5.QtGui import QPixmap, QImage, QPen, QPainter, QColor, QIcon
from PyQt5.QtCore import Qt, QRect, QRectF, QPointF
import numpy as np
import cv2
import sys
import Cartoon
from seam_carving import SeamCarver
import time


class WarpingInputBox(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Warping")

        icon = QApplication.style().standardIcon(QStyle.SP_MessageBoxInformation)
        self.setWindowIcon(icon)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Layout and Widgets
        layout = QVBoxLayout()
        

        # First Input
        self.input1 = QLineEdit(self)
        self.input1.setPlaceholderText("Enter Width")
        layout.addWidget(self.input1)

        # Second Input
        self.input2 = QLineEdit(self)
        self.input2.setPlaceholderText("Enter Height")
        layout.addWidget(self.input2)

        self.label = QLabel(self)
        self.label.setText("Remove or Protect Object:")
        layout.addWidget(self.label)

        self.mask_button = QPushButton(self)
        self.mask_button.setText("Mark Object")
        layout.addWidget(self.mask_button)


        self.no_mask = QRadioButton("None", self)
        layout.addWidget(self.no_mask)
        self.no_mask.toggle()

        self.protect = QRadioButton("Protect Object", self)
        layout.addWidget(self.protect)
        self.protect.toggled.connect(self.checkToggle)
        

        print("Protect Toggled: ", self.protect.toggled)
        self.remove = QRadioButton("Remove Object", self)
        layout.addWidget(self.remove)

        
        self.confirmed = False
        self.objectMarked = False

        # OK and Cancel Buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.validateAndConfirm)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def checkNumber(self, number):
        if isinstance(number, str) and number.isdigit():
            return True
        else:
            return False
                
    
    def validateAndConfirm(self):
        width = self.input1.text()
        height = self.input2.text()

        if width == "" or height == "":
            QMessageBox.warning(self, "Empty Values!",
                                                "Please do enter all values",
                                                QMessageBox.Ok)
            
        if (self.protect.isChecked() or self.remove.isChecked()) and not self.objectMarked:
            QMessageBox.warning(self, "No Marked Object in Image",
                                                "Please make sure to Mark the object if protect or remove is selected",
                                                QMessageBox.Ok)
        else:
            if self.checkNumber(width) and self.checkNumber(height):
                
                if int(width) > 2000 or int(height) > 2000:
                    QMessageBox.warning(self, "Values out of range !",
                                                    "Please do not enter values > 2000",
                                                    QMessageBox.Ok)
                        
                else:
                    confirmBox = QMessageBox.question(self,
                            "Confirm Parameters",
                            f"Are you sure you want to proceed?\nNew dimensions:\nW: {width} H: {height}\n{self.checkToggle()}",
                            QMessageBox.Yes | QMessageBox.No
                            )
                    
                    if confirmBox == QMessageBox.Yes:
                        self.accept()
                        self.confirmed = True
                        print(f"Confirmed {width}x{height}  ")

            

    def getInputs(self):
        if self.confirmed: 
            return int(self.input1.text()), int(self.input2.text()), self.protect.isChecked(), self.remove.isChecked(), self.no_mask.isChecked()
    
    def checkToggle(self):
        if self.protect.isChecked():
            return "Protect Object"
        elif self.remove.isChecked():
            return "Remove Object"
        else:
            return "No Option Set"

class ImageProcessor(QMainWindow):

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

        # win = QMainWindow()
        # self.setGeometry(200, 200, 300, 300)
        # self.setWindowTitle("Image Processor")

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
        warp_button.clicked.connect(self.content_dependent_warping)


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
        layout.addWidget(cartoon_button)
        layout.addWidget(save_button)
        layout.addWidget(reset_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setGeometry(500, 150, 800, 800)
        self.setWindowTitle('Image Processor')
        self.setWindowIcon(QIcon("files/imgprocicon.png"))

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
    
    def load_warped(self, file_name):
            print("load warped: ", file_name)
            self.image_path = file_name
            self.file_name = file_name
            self.theImage = file_name
            
            # self.original_image = ""
            self.display_loaded_image()

    # def load_image(self, warped):
    #     self.image_path = warped
    #     self.theImage = warped
        
    #     # self.original_image = ""
    #     self.display_loaded_image()

    def reset_image(self):
        self.image_to_edit = None
        self.edited = False
        self.marking_mode = False
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




    def eventFilter(self, source, event):
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




    # handle content dependent warping
    def content_dependent_warping(self):
        dialog = WarpingInputBox()
        if dialog.exec_() == QDialog.Accepted:
            # import parameters set from dialog boc
            new_width, new_height, protect, remove, no_mask = dialog.getInputs()

            # debug: display the chosen parameters
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"New Width: {new_width}, Height: {new_height}\n{dialog.checkToggle()}\n{protect}\n{remove}\n{no_mask}")
            msg.setWindowTitle("Chosen Parameters:")
            # time.sleep(2)
            msg.exec_()

            # start seam carving based on options set
            if no_mask:
                # obj = SeamCarver(self.image_path, new_height, new_width)
                # obj.save_result("output/output.png")
                output = cv2.imread("output/output.png")
                cv2.imshow("Output", output)

                cv2.waitKey(0)
                # whether or not to use the warped image to see on screen
                use_image = QMessageBox.information(self, "Information",
                                                    "Use warped image?",
                                                    QMessageBox.Yes | QMessageBox.No
                                                    )
                if use_image == QMessageBox.Yes:
                    self.load_warped("output/output.png")

            elif protect:
                obj = SeamCarver(self.image_path, new_height, new_width, protect_mask="mask/mask.jpg")
                obj.save_result("output/output.png")
                output = cv2.imread("output/output.png")
                cv2.imshow("Output", output)
                
                cv2.waitKey(0)

            elif remove:
                obj = SeamCarver(self.image_path, 0, 0, object_mask="mask/mask.jpg")
                obj.save_result("output/output.png")
                output = cv2.imread("output/output.png")
                cv2.imshow("Output", output)
                cv2.waitKey(0)

            

            

        


# main loop
if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = ImageProcessor()
    editor.show()
    sys.exit(app.exec_())


