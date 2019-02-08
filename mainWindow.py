# Define function to import external files when using PyInstaller.
import os, sys, subprocess

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QObject, pyqtSlot, QFile, QModelIndex, pyqtSignal, QDir
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

		self.warn = QDialog()

		### Source and Destination selection flags ###
		self.isSrcSelected = False
		self.isDstSeleceted = False

		### the Source and Destination directory-paths ###
		self.srcDirPath = ''
		self.dstDirPath = ''

		### full Source file-path(s) ###
		self.srcPaths = []

		### options ###
		self.opts = ''
		# self.opts = '/E /MT /COPY:DT'

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

		self.model_3 = QFileSystemModel()
		self.model_3.setRootPath('')

		self.model_4 = QFileSystemModel()
		self.model_4.setRootPath('')

		### link QML elements to Python variables ###
		self.mainWin: QMainWindow = self.ui.findChild(QMainWindow, "MainWindow")
		self.srcDirView: QTreeView = self.ui.findChild(QTreeView, "sourceDirView")
		self.dstDirV: QTreeView = self.ui.findChild(QTreeView, "destDirView")
		# self.srcFlistView: QListWidget = self.ui.findChild(QListView, "sourceFileListView")
		# self.dstFlistView: QListWidget = self.ui.findChild(QListView, "destFileListView")
		self.srcFlistView: QListView = self.ui.findChild(QListView, "sourceFileListView")
		self.dstFlistView: QListView = self.ui.findChild(QListView, "destFileListView")
		self.srcPathLNE: QLineEdit = self.ui.findChild(QLineEdit, "sourcePathLNE")
		self.dstPathLNE: QLineEdit = self.ui.findChild(QLineEdit, "destPathLNE")

		### set up file-system models ###
		self.srcDirView.setModel(self.model_1)
		self.srcFlistView.setModel(self.model_3)
		self.dstDirV.setModel(self.model_2)
		self.dstFlistView.setModel(self.model_4)

		### selecting item(s) in treeview(s) return(s) pathname(s) ###
		self.srcDirView.clicked.connect(self.srcDirSelected)
		self.dstDirV.clicked.connect(self.dstDirSelected)

		### selecting item in listviews returns filename ###
		self.srcFlistView.clicked.connect(self.srcFilesSelected)
		self.dstFlistView.clicked.connect(self.dstFilesSelected)

	def safetyDialog(self):
		self.warn.setModal(True)

		okButton = QPushButton('OK')
		cancelButton = QPushButton('Cancel')

		hlayout = QHBoxLayout()
		hlayout.addWidget(okButton)
		hlayout.addWidget(cancelButton)

		self.warn.setLayout(hlayout)

		okButton.clicked.connect(self.acceptWarn)
		cancelButton.clicked.connect(self.rejectWarn)

		self.warn.exec()

	@pyqtSlot()
	def rejectWarn(self):
		self.warn.reject()

	@pyqtSlot()
	def acceptWarn(self):
		self.warn.accept()

	@pyqtSlot(QModelIndex, name='index1')
	def srcDirSelected(self, index1):
		''' Get selected path from srcDirView '''

		### get path from srcDirView  ###
		path = self.model_1.fileInfo(index1).absoluteFilePath()

		print(f'path: {path}')

		### update srcFlistView ###
		self.srcFlistView.setRootIndex(self.model_3.setRootPath(path))

		### update self.srcPath ###
		self.srcDirPath = path

		# print(f'self.srcDirPath: {self.srcPath}')

		return path

	@pyqtSlot(QModelIndex, name='index2')
	def dstDirSelected(self, index2) -> str:
		''' Get selected path from dstDirView '''

		### get path from dstDirView ###
		path = self.model_2.fileInfo(index2).absoluteFilePath()

		print(f'path: {path}')

		### update dstFlistView ###
		self.dstFlistView.setRootIndex(self.model_4.setRootPath(path))

		### update srcPath ###
		self.dstDirPath = path

		print(f'self.dstDirPath: {self.dstDirPath}')

		return path

	@pyqtSlot()
	def srcFilesSelected(self):
		stuff = []
		for i in self.srcFlistView.selectedIndexes():
			stuff.append(self.model_3.filePath(i))
		self.srcPaths = stuff

		print(self.srcPaths)

		### mark Source as being selected ###
		if self.srcPaths is not []:
			self.isSrcSelected = True

		return stuff

	@pyqtSlot()
	def dstFilesSelected(self):
		dirry = self.model_4.filePath(self.dstFlistView.selectedIndexes().pop())

		print(dirry)

		### mark destination as being selected ###
		if dirry is not '':
			self.isDstSeleceted = True
			self.dstDirPath = dirry

		return dirry

	@pyqtSlot(name='')
	def srcDirViewClick(self):
		print('srcDirView clickeds')

	@pyqtSlot(name='')
	def sourceRefresh(self):
		print('sourceRefreshBTN clicked')

	@pyqtSlot(name='')
	def destRefresh(self):
		print('destRefreshBTN clicked')

	@pyqtSlot(name='')
	def startBackup(self):
		# if self.opts == '':
		# 	subprocess.call(['robocopy', '/?'], shell=True)
		# else:
		# 	subprocess.call(['robocopy', self.opts], shell=True)

		# print(f'self.srcPath: {self.srcPath}')
		# print(f'self.dstPath: {self.dstPath}')

		# print(f'Source selected = {self.isSrcSelected}')
		# print(f'Destination selected = {self.isDstSeleceted}')

		self.safetyDialog()

		if self.isSrcSelected and self.isDstSeleceted:
			self.opts = '/E /MT /COPY:DT'

			print(f'robocopy {self.opts} {self.srcDirPath} {self.dstDirPath}')


# subprocess.call(['robocopy', self.opts, self.srcDirPath, self.dstDirPath], shell=True)


if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = MainWindowUI()
	window.show()
	sys.exit(app.exec_())
