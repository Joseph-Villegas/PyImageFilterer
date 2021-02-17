import os
import sys
from filters import *
from PIL import Image
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter, QIcon
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog, QApplication, QStyle

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

def resource_path(relative_path):
	""" Translate asset paths to useable format for PyInstaller """
	if hasattr(sys, '_MEIPASS'):
		return os.path.join(sys._MEIPASS, relative_path)
	return os.path.join(os.path.abspath('.'), relative_path)

class PyImageFilterer(QMainWindow):
	""" GUI for Image Manipulation """
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

		self.setWindowIcon(QIcon(resource_path('./assets/icon.png')))
		self.setWindowTitle("PyImage Filterer")
		self.resize(800, 600)

	def open(self):
		""" Selects and displays an image from a user's personal files """
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		self.fileName, _ = QFileDialog.getOpenFileName(self, 'Select an Image to Filter', '', 'Images (*.png *.jpeg *.jpg *.bmp *.gif)', options=options)
		if self.fileName:
			self.base_image = Image.open(self.fileName)
			self.filtered_image = self.base_image.copy()
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
			self.sepiaAct.setEnabled(True)
			self.contrastAct.setEnabled(True)
			self.flipAct.setEnabled(True)
			self.mirrorAct.setEnabled(True)

			self.updateZoomActions()

			if not self.fitToWindowAct.isChecked():
				self.imageLabel.adjustSize()

	def print_(self):
		""" Prints image as displayed """
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
		QMessageBox.about(self, "About PyImage Filterer",
								"<p>The <b>PyImage Filterer</b> GUI was developed in the Python programming language using the PyQt5 module for widget creation "
								"and PIL for image manipulation. "
								"A user may select an image from their personal files and apply any one of the available filters to their image. "
								"An image can be saved as a PNG or JPG in the user's desired directory destination or be printed. "
								"Developed by Joseph Villegas, student at CSUMB.</p>"
								"<a class='link' href='https://github.com/Joseph-Villegas/PyImageFilterer_V1'>View source code on GitHub</a>")

	def createActions(self):
		self.openAct = QAction(self.style().standardIcon(QStyle.SP_DialogOpenButton), "&Open...", self, shortcut="Ctrl+O", triggered=self.open)
		self.printAct = QAction("&Print...", self, shortcut="Ctrl+P", enabled=False, triggered=self.print_)
		self.saveAct = QAction(self.style().standardIcon(QStyle.SP_DialogSaveButton), "&Save...", self, enabled=False, triggered=self.save)
		self.exitAct = QAction(self.style().standardIcon(QStyle.SP_DialogCancelButton),"&Exit", self, shortcut="Ctrl+Q", triggered=self.close)

		self.zoomInAct = QAction("Zoom &In (25%)", self, shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)
		self.zoomOutAct = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)
		self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)
		self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False, checkable=True, shortcut="Ctrl+F", triggered=self.fitToWindow)
		self.aboutAct = QAction(self.style().standardIcon(QStyle.SP_FileDialogInfoView), "&About", self, triggered=self.about)
		self.aboutQtAct = QAction(self.style().standardIcon(QStyle.SP_FileDialogInfoView), "About &Qt", self, triggered=qApp.aboutQt)

		self.invertAct = QAction("&Invert", self, enabled=False, triggered=lambda: self.filter("invert"))
		self.maskAct = QAction("&Mask", self, enabled=False, triggered=lambda: self.filter("mask"))
		self.grayscaleAct = QAction("&Grayscale", self, enabled=False, triggered=lambda: self.filter("grayscale"))
		self.swapChannelsAct = QAction("Swap &Channels", self, enabled=False, triggered=lambda: self.filter("swap channels"))
		self.sepiaAct = QAction("&Sepia", self, enabled=False, triggered=lambda: self.filter("sepia"))
		self.contrastAct = QAction("&Contrast", self, enabled=False, triggered=lambda: self.filter("contrast"))
		self.flipAct = QAction("&Flip", self, enabled=False, triggered=lambda: self.filter("flip"))
		self.mirrorAct = QAction("&Mirror", self, enabled=False, triggered=lambda: self.filter("mirror"))

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
		self.editMenu.addAction(self.sepiaAct)
		self.editMenu.addAction(self.contrastAct)
		self.editMenu.addAction(self.flipAct)
		self.editMenu.addAction(self.mirrorAct)

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

	def filter(self, filter):
		""" Applies selected filters to an image """
		QApplication.setOverrideCursor(Qt.WaitCursor)

		if filter == "invert":
			self.filtered_image = invert(self.base_image)
		elif filter == "grayscale":
			self.filtered_image = grayscale(self.base_image)
		elif filter == "swap channels":
			self.filtered_image = swap_channels(self.base_image)
		elif filter == "mask":
			self.filtered_image = mask(self.base_image)
		elif filter == "sepia":
			self.filtered_image = sepia(self.base_image)
		elif filter == "contrast":
			self.filtered_image = contrast(self.base_image)
		elif filter == "flip":
			self.filtered_image = flip(self.base_image)
		elif filter == "mirror":
			self.filtered_image = mirror(self.base_image)

		pixmap = pil2pixmap(self.filtered_image)
		self.imageLabel.setPixmap(pixmap)
		QApplication.restoreOverrideCursor()

	def save(self):
		""" Saves PNG/JPG file at user's desired destination """
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		filename, extension = QFileDialog.getSaveFileName(self, "Save Filtered Image", '', 'JPG (*.jpg);;PNG (*.png)', options=options)
		
		if filename:
			if 'PNG' in extension:
				self.filtered_image.save(f'{filename}.png')
			elif 'JPG' in extension:
				self.filtered_image.save(f'{filename}.jpg')

def main():
	app = QApplication(sys.argv)
	imageFilterer = PyImageFilterer()
	imageFilterer.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
