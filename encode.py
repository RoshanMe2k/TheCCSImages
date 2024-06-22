import sys
import struct
import zlib
from PIL import Image, ImageEnhance
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox, QFileDialog

def rgb_to_ccs(r, g, b):
    C = r / 255.0
    L = g / 255.0
    D = b / 255.0
    return C, L, D

def encode_image_to_ccs(input_image, output_file):
    img = Image.open(input_image).convert('RGB')
    width, height = img.size

    with open(output_file, 'wb') as f:
        f.write(struct.pack('II', width, height))

        for y in range(height):
            for x in range(width):
                r, g, b = img.getpixel((x, y))
                C, L, D = rgb_to_ccs(r, g, b)
                compressed_data = zlib.compress(struct.pack('fff', C, L, D), level=9)
                f.write(struct.pack('I', len(compressed_data)))
                f.write(compressed_data)


def enhance_image(decoded_image):
    enhanced_image = decoded_image
    
    enhanced_image = ImageEnhance.Sharpness(enhanced_image).enhance(2.0)
    
    enhanced_image = ImageEnhance.Color(enhanced_image).enhance(1.2)
    
    enhanced_image = ImageEnhance.Contrast(enhanced_image).enhance(1.2)
    
    return enhanced_image


class ImageEncoderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Image to CCS Encoder')
        self.setGeometry(100, 100, 400, 150)
        
        self.file_label = QLabel('Select an image to encode:')
        self.file_button = QPushButton('Select File', self)
        self.file_button.clicked.connect(self.openFileNameDialog)
        
        self.save_label = QLabel('Save as:')
        self.save_edit = QLineEdit(self)
        
        self.encode_button = QPushButton('Encode Image to CCS', self)
        self.encode_button.clicked.connect(self.encodeImage)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.file_label)
        vbox.addWidget(self.file_button)
        vbox.addWidget(self.save_label)
        vbox.addWidget(self.save_edit)
        vbox.addWidget(self.encode_button)
        
        self.setLayout(vbox)
    
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, 'Select Image', '', 'Image files (*.jpg *.png *.bmp)', options=options)
        if fileName:
            self.input_image = fileName
    
    def encodeImage(self):
        try:
            output_file = self.save_edit.text().strip()
            if not output_file.endswith('.ccs'):
                output_file += '.ccs'
            
            if not self.input_image:
                QMessageBox.warning(self, 'Warning', 'Please select an input image.')
                return
            
            encode_image_to_ccs(self.input_image, output_file)
            encoded_image = Image.open(output_file)
            enhanced_image = enhance_image(encoded_image)
            enhanced_image.save(output_file) 
            print(f'Image encoded and saved as {output_file}')
        except Exception as e:
            print(f'Error: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ImageEncoderGUI()
    gui.show()
    sys.exit(app.exec_())
