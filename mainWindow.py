# Define function to import external files when using PyInstaller.
import os, sys

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QObject, pyqtSlot, QFile, QModelIndex
from PyQt5.QtWidgets import *
import traceback


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

		### link QML elements to Python variables ###
		self.mainWin: QMainWindow = self.ui.findChild(QMainWindow, "MainWindow")
		self.srcDirView: QTreeView = self.ui.findChild(QTreeView, "sourceDirView")
		self.dstDirV: QTreeView = self.ui.findChild(QTreeView, "destDirView")
		self.srcFlistView: QListView = self.ui.findChild(QListView, "sourceFileListView")
		self.dstFlistView: QListView = self.ui.findChild(QListView, "destFileListView")
		self.srcPathLNE: QLineEdit = self.ui.findChild(QLineEdit, "sourcePathLNE")
		self.dstPathLNE: QLineEdit = self.ui.findChild(QLineEdit, "destPathLNE")

		### set up file-system models ###
		self.srcDirView.setModel(self.model_1)
		self.srcFlistView.setModel(self.model_1)
		self.dstDirV.setModel(self.model_2)
		self.dstFlistView.setModel(self.model_2)

		### selecting item(s) in treeview(s) return(s) pathname(s) ###
		self.srcDirView.clicked.connect(self.srcDirSelected)
		self.dstDirV.clicked.connect(self.dstDirSelected)

	@pyqtSlot(QModelIndex)
	def srcDirSelected(self, index):
		''' Get selected path from srcDirView '''
		file_path = self.model_1.index(index.row(), 0, index.parent())

		filename = self.model_1.fileName(file_path)
		pathname = self.model_1.filePath(file_path)

		print(pathname + filename)

		return pathname

	@pyqtSlot(QModelIndex)
	def dstDirSelected(self, index):
		''' Get selected path from dstDirView '''
		currentRow = self.model_2.index(index.row(), 0, index.parent())

		pathname = self.model_2.filePath(currentRow)

		print(pathname)

		return pathname

	@pyqtSlot()
	def srcDirViewClick(self):
		print('srcDirView clickeds')

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
