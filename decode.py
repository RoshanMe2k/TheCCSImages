import sys
import struct
import zlib
from PIL import Image
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QPixmap, QImage

class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Decoded Image")
        self.label = QLabel(self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        self.layout.addWidget(self.close_button)

        self.select_button = QPushButton("Select .ccs File")
        self.select_button.clicked.connect(self.select_file_and_display)
        self.layout.addWidget(self.select_button)

        self.setLayout(self.layout)

    def select_file_and_display(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select .ccs File", "", "CCS Files (*.ccs)", options=options)
        if file_name:
            self.display_image(file_name)

    def display_image(self, image_path):
        decoded_image = self.decode_ccs_to_image(image_path)

        img = QImage(decoded_image.tobytes(), decoded_image.size[0], decoded_image.size[1], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        self.label.setPixmap(pixmap)

    def ccs_to_rgb(self, C, L, D):
        r = int(C * 255)
        g = int(L * 255)
        b = int(D * 255)
        return r, g, b

    def decode_ccs_to_image(self, ccs_file):
        with open(ccs_file, 'rb') as f:
            header = f.read(8)
            width, height = struct.unpack('II', header)

            image = Image.new('RGB', (width, height))
            pixels = []

            while True:
                try:
                    compressed_size = struct.unpack('I', f.read(4))[0]
                    compressed_data = f.read(compressed_size)
                    unpacked_data = struct.unpack('fff', zlib.decompress(compressed_data))
                    r, g, b = self.ccs_to_rgb(*unpacked_data)
                    pixels.append((r, g, b))
                except struct.error:
                    break

            image.putdata(pixels)

        return image


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())
