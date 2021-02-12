import sys
from filters import *
from PIL import Image
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter, QIcon
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog, QApplication

def pil2pixmap(image):
	""" Converts pillow image object to pixmap for use in PyQt5 GUI """
	if image.mode == "RGB":
		r, g, b = image.split()
		image = Image.merge("RGB", (b, g, r))
	elif image.mode == "RGBA":
		r, g, b, a = image.split()
		image = Image.merge("RGBA", (b, g, r, a))
	elif image.mode == "L":
		image = image.convert("RGBA")

	# Convert image to RGBA if not already done
	image2 = image.convert("RGBA")
	data = image2.tobytes("raw", "RGBA")
	qim = QImage(data, image.size[0], image.size[1], QImage.Format_ARGB32)
	pixmap = QPixmap.fromImage(qim)
	return pixmap


class PyImageFilterer(QMainWindow):
	def __init__(self):
		super().__init__()

		self.printer = QPrinter()
		self.scaleFactor = 0.0

		self.imageLabel = QLabel()
		self.imageLabel.setBackgroundRole(QPalette.Base)
		self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
		self.imageLabel.setScaledContents(True)

		self.scrollArea = QScrollArea()
		self.scrollArea.setBackgroundRole(QPalette.Dark)
		self.scrollArea.setWidget(self.imageLabel)
		self.scrollArea.setVisible(False)

		self.setCentralWidget(self.scrollArea)

		self.createActions()
		self.createMenus()

		self.setWindowIcon(QIcon("icon.jpg"))
		self.setWindowTitle("PyImage Filterer")
		self.resize(800, 600)

	def open(self):
		options = QFileDialog.Options()

		self.fileName, _ = QFileDialog.getOpenFileName(self, 'Select an Image to Filter', '', 'Images (*.png *.jpeg *.jpg *.bmp *.gif)', options=options)
		if self.fileName:
			image = QImage(self.fileName)
			if image.isNull():
				QMessageBox.information(self, "Image Viewer", "Cannot load %s." % self.fileName)
				return

			self.imageLabel.setPixmap(QPixmap.fromImage(image))
			self.scaleFactor = 1.0

			self.scrollArea.setVisible(True)
			self.printAct.setEnabled(True)
			self.saveAct.setEnabled(True)
			self.fitToWindowAct.setEnabled(True)

			self.invertAct.setEnabled(True)
			self.maskAct.setEnabled(True)
			self.grayscaleAct.setEnabled(True)
			self.swapChannelsAct.setEnabled(True)

			self.updateZoomActions()

			if not self.fitToWindowAct.isChecked():
				self.imageLabel.adjustSize()

	def print_(self):
		dialog = QPrintDialog(self.printer, self)
		if dialog.exec_():
			painter = QPainter(self.printer)
			rect = painter.viewport()
			size = self.imageLabel.pixmap().size()
			size.scale(rect.size(), Qt.KeepAspectRatio)
			painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
			painter.setWindow(self.imageLabel.pixmap().rect())
			painter.drawPixmap(0, 0, self.imageLabel.pixmap())

	def zoomIn(self):
		self.scaleImage(1.25)

	def zoomOut(self):
		self.scaleImage(0.8)

	def normalSize(self):
		self.imageLabel.adjustSize()
		self.scaleFactor = 1.0

	def fitToWindow(self):
		fitToWindow = self.fitToWindowAct.isChecked()
		self.scrollArea.setWidgetResizable(fitToWindow)
		if not fitToWindow:
			self.normalSize()

		self.updateZoomActions()

	def about(self):
		QMessageBox.about(self, "About PyImage Filter",
								"<p>The <b>PyImage Filter</b> shows how to combine "
								"QLabel and QScrollArea to display an image. QLabel is "
								"typically used for displaying text, but it can also display "
								"an image. QScrollArea provides a scrolling view around "
								"another widget. If the child widget exceeds the size of the "
								"frame, QScrollArea automatically provides scroll bars.</p>"
								"<p>The example demonstrates how QLabel's ability to scale "
								"its contents (QLabel.scaledContents), and QScrollArea's "
								"ability to automatically resize its contents "
								"(QScrollArea.widgetResizable), can be used to implement "
								"zooming and scaling features.</p>"
								"<p>In addition the example shows how to use QPainter to "
								"print an image and Pillow to filter an image .</p>"
								"<a class='link' href='https://github.com/WilliamSampson44444/cst205_weather_project'>View source on GitHub</a>")

	def createActions(self):
		self.openAct = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
		self.printAct = QAction("&Print...", self, shortcut="Ctrl+P", enabled=False, triggered=self.print_)
		self.saveAct = QAction("&Save...", self, enabled=False, triggered=self.save)
		self.exitAct = QAction("&Exit", self, shortcut="Ctrl+Q", triggered=self.close)

		self.zoomInAct = QAction("Zoom &In (25%)", self, shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)
		self.zoomOutAct = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)
		self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)
		self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False, checkable=True, shortcut="Ctrl+F", triggered=self.fitToWindow)
		self.aboutAct = QAction("&About", self, triggered=self.about)
		self.aboutQtAct = QAction("About &Qt", self, triggered=qApp.aboutQt)

		self.invertAct = QAction("&Invert", self, enabled=False, triggered=lambda: self.filterHandler("invert"))
		self.maskAct = QAction("&Mask", self, enabled=False, triggered=lambda: self.filterHandler("mask"))
		self.grayscaleAct = QAction("&Grayscale", self, enabled=False, triggered=lambda: self.filterHandler("grayscale"))
		self.swapChannelsAct = QAction("Swap &Channels", self, enabled=False, triggered=lambda: self.filterHandler("swap channels"))

	def createMenus(self):
		self.fileMenu = QMenu("&File", self)
		self.fileMenu.addAction(self.openAct)
		self.fileMenu.addAction(self.printAct)
		self.fileMenu.addAction(self.saveAct)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.exitAct)

		self.viewMenu = QMenu("&View", self)
		self.viewMenu.addAction(self.zoomInAct)
		self.viewMenu.addAction(self.zoomOutAct)
		self.viewMenu.addAction(self.normalSizeAct)
		self.viewMenu.addSeparator()
		self.viewMenu.addAction(self.fitToWindowAct)

		self.helpMenu = QMenu("&Help", self)
		self.helpMenu.addAction(self.aboutAct)
		self.helpMenu.addAction(self.aboutQtAct)

		self.editMenu = QMenu("&Edit", self)
		self.editMenu.addAction(self.invertAct)
		self.editMenu.addAction(self.maskAct)
		self.editMenu.addAction(self.grayscaleAct)
		self.editMenu.addAction(self.swapChannelsAct)

		self.menuBar().addMenu(self.fileMenu)
		self.menuBar().addMenu(self.editMenu)
		self.menuBar().addMenu(self.viewMenu)
		self.menuBar().addMenu(self.helpMenu)

	def updateZoomActions(self):
		self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
		self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
		self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

	def scaleImage(self, factor):
		self.scaleFactor *= factor
		self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

		self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
		self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

		self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
		self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

	def adjustScrollBar(self, scrollBar, factor):
		scrollBar.setValue(int(factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep() / 2)))

	def filterHandler(self, filter):
		print(f"Filter Selected: {filter}")
		QApplication.setOverrideCursor(Qt.WaitCursor)
		image = Image.open(self.fileName)
		self.filter = filter
		if filter == "invert":
			self.filtered_image = invert(image)
		elif filter == "grayscale":
			self.filtered_image = grayscale(image)
		elif filter == "swap channels":
			self.filtered_image = swap_channels(image)
		elif filter == "mask":
			self.filtered_image = mask(image)

		pixmap = pil2pixmap(self.filtered_image)
		self.imageLabel.setPixmap(pixmap)
		QApplication.restoreOverrideCursor()
		print("DONE")

	def save(self):
		image_path = self.fileName

		image_type = image_path.split('/')[-1].split('.')[-1]
		image_title = image_path.split('/')[-1].split('.')[-2]

		self.filtered_image.save(f"{image_title}-{self.filter}_filter.{image_type}")


def main():
	app = QApplication(sys.argv)
	imageFilterer = PyImageFilterer()
	imageFilterer.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
