# Define function to import external files when using PyInstaller.
import os, sys

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QObject, pyqtSlot, QFile
from PyQt5.QtWidgets import *


def resource_path(relative_path):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")

	return os.path.join(base_path, relative_path)


uiPath = resource_path('gvDataBackup_MainWindow.ui')


class MainWindowUI(QtWidgets.QMainWindow):
	def __init__(self):
		super(MainWindowUI, self).__init__()
		global uiPath

		self.ui = uic.loadUi(uiPath, self)

		self.startBTN.clicked.connect(self.startBackup)
		self.sourceRefreshBTN.clicked.connect(self.sourceRefresh)
		self.destRefreshBTN.clicked.connect(self.destRefresh)
		self.actionQuit.triggered.connect(QApplication.quit)

		self.model_1 = QFileSystemModel()
		self.model_1.setRootPath('')

		self.model_2 = QFileSystemModel()
		self.model_2.setRootPath('')

		self.srcDirView: QTreeView = self.ui.findChild(QTreeView, "sourceDirView")
		self.dstDirV: QTreeView = self.ui.findChild(QTreeView, "destDirView")

		self.srcDirView.setModel(self.model_1)

		self.dstDirV.setModel(self.model_2)

		# self.sourceFileListView

	@pyqtSlot()
	def sourceRefresh(self):
		print('sourceRefreshBTN clicked')

	@pyqtSlot()
	def destRefresh(self):
		print('destRefreshBTN clicked')

	@pyqtSlot()
	def startBackup(self):
		pass


if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = MainWindowUI()
	window.show()
	sys.exit(app.exec_())
