# Define function to import external files when using PyInstaller.
import os
import sys
import traceback as tb
import subprocess

from PyQt5 import QtCore, QtWidgets, uic, QtGui
from PyQt5.QtCore import pyqtSlot, QModelIndex, Qt
from PyQt5.QtWidgets import *


def resource_path(relative_path):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	try:
		### PyInstaller creates a temp folder and stores path in _MEIPASS ##
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")

	return os.path.join(base_path, relative_path)


### connect *.ui file to code ###
uiPath = resource_path('gvDataBackup_MainWindow.ui')


### the meat of the program  ###
class MainWindowUI(QtWidgets.QMainWindow):
	def __init__(self):
		super(MainWindowUI, self).__init__()

		### warning dialog ###
		self.warn = QDialog()

		### Source and Destination selection flags ###
		self.isSrcSelected = False
		self.isDstSeleceted = False

		### the Source and Destination directory-paths ###
		self.srcDirPath = ''
		self.dstDirPath = ''

		### full Source file-path(s) ###
		self.srcPaths = []

		### options for Robocopy ###
		self.opts = '/E /COPY:DT'

		### the command string for Robocopy ###
		self.cmdStr = ''

		global uiPath
		self.ui = uic.loadUi(uiPath, self)

		self.startBTN.clicked.connect(self.startBackup)
		self.sourceRefreshBTN.clicked.connect(self.sourceRefresh)
		self.destRefreshBTN.clicked.connect(self.destRefresh)
		self.actionQuit.triggered.connect(QApplication.quit)

		self.srcDirMODEL = QFileSystemModel()
		self.srcDirMODEL.setRootPath('')

		self.dstDirMODEL = QFileSystemModel()
		self.dstDirMODEL.setRootPath('')

		self.srcFlistMODEL = QFileSystemModel()
		self.srcFlistMODEL.setRootPath('')
		self.srcFlistMODEL.setReadOnly(False)

		self.dstFlistMODEL = QFileSystemModel()
		self.dstFlistMODEL.setRootPath('')

		### link QML elements to Python variables ###
		self.mainWin: QMainWindow = self.ui.findChild(QMainWindow, "MainWindow")
		self.srcDirView: QTreeView = self.ui.findChild(QTreeView, "sourceDirView")
		self.dstDirV: QTreeView = self.ui.findChild(QTreeView, "destDirView")
		self.srcFlistView: QListView = self.ui.findChild(QListView, "sourceFileListView")
		self.dstFlistView: QListView = self.ui.findChild(QListView, "destFileListView")
		self.srcPathLNE: QLineEdit = self.ui.findChild(QLineEdit, "sourcePathLNE")
		self.dstPathLNE: QLineEdit = self.ui.findChild(QLineEdit, "destPathLNE")
		self.newSrcFolderBTN: QPushButton = self.ui.findChild(QPushButton, "newSrcFolderBTN")
		self.newDestFolderBTN: QPushButton = self.ui.findChild(QPushButton, "newDstFolderBTN")

		### enable custom right-click menus ###
		self.srcFlistView.setContextMenuPolicy(Qt.CustomContextMenu)
		self.dstFlistView.setContextMenuPolicy(Qt.CustomContextMenu)

		### set up file-system models ###
		self.srcDirView.setModel(self.srcDirMODEL)
		self.srcFlistView.setModel(self.srcFlistMODEL)
		self.dstDirV.setModel(self.dstDirMODEL)
		self.dstFlistView.setModel(self.dstFlistMODEL)

		self.dstDirMODEL.setObjectName("dstDirMODEL")

		### selecting item(s) in treeview(s) return(s) pathname(s) ###
		self.srcDirView.clicked.connect(self.srcDirSelected)
		self.dstDirV.clicked.connect(self.dstDirSelected)

		### selecting item in listviews returns filename ###
		self.srcFlistView.clicked.connect(self.srcFilesSelected)
		self.dstFlistView.clicked.connect(self.dstFilesSelected)

		### connect right-click menu slots ###
		self.srcFlistView.customContextMenuRequested.connect(lambda rm: self.rightClickMenu(self.srcDirView))
		self.dstFlistView.customContextMenuRequested.connect(lambda rm: self.rightClickMenu(self.dstDirV))

	def safetyDialog(self) -> None:
		'''	Spawn a modal QDialog window with info about the source and destination locations, as well as
			the current robocopy options.'''
		### set the modal property to True ###
		self.warn.setModal(True)

		### 'glayout' is the root layout widget for this dialog window ###
		glayout = QGridLayout(self.warn)

		### 'msg' is the message string to be displayed ###
		msg = QLabel()

		if self.srcPaths != [] and self.dstDirPath != '':
			msgSrcStr = self.srcPaths[0]
			for i in range(1, self.srcPaths.__len__()):
				msgSrcStr += ' ' + self.srcPaths[i]
			msgDstStr = self.dstDirPath

			msgStr = f'robocopy {msgSrcStr} {msgDstStr} {self.opts}'
			self.cmdStr = f'robocopy {msgSrcStr} {msgDstStr} {self.opts}'
			msg.setText(msgStr)
		else:
			msg.setText('BLANK')

		glayout.addWidget(msg, 0, 0, 1, 1)

		### 'buttonbox' contains our 'OK' and 'Cancel' buttons ###
		buttonbox = QDialogButtonBox()
		buttonbox.setOrientation(QtCore.Qt.Horizontal)
		buttonbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
		glayout.addWidget(buttonbox, 1, 0, 1, 1)

		### set up actions for our 'OK' and 'Cancel' buttons ###
		buttonbox.accepted.connect(self.acceptWarn)
		buttonbox.rejected.connect(self.rejectWarn)

		### spawn the dialog box ###
		self.warn.exec()

	def rightClickMenu(self, dirView: QTreeView):
		view: QListView = self.sender()
		model: QFileSystemModel = view.model()

		print(f'right-click')
		print(f'{view.objectName()}')
		print(f'{model.objectName()}')

		menu = QMenu()
		nf = QAction('New Folder')
		menu.addAction(nf)
		nf.triggered.connect(lambda t: self.createNewFolder(view, model, dirView))
		menu.addSeparator()
		quitAction = menu.addAction("Quit")

		action = menu.exec_(QtGui.QCursor.pos())

	def createNewFolder(self, view: QListView, model: QFileSystemModel, dir: QTreeView):
		sender = self.sender()
		vm: QFileSystemModel = view.model()

		print(f'{self.sender()}')
		print(f'{view.objectName()}')
		print(f'{view.model().objectName()}')

		nfi: QModelIndex = model.mkdir(dir.currentIndex(), 'new folder')

		print(f'new folder')

	@pyqtSlot()
	def rejectWarn(self):
		'''Dialog to show if 'Cancel' is clicked'''
		print('rejectWarn')
		self.warn.reject()

	@pyqtSlot()
	def acceptWarn(self):
		'''Dialog to show if 'Accept' is clicked'''
		print('acceptWarn')
		# subprocess.call(self.cmdStr)
		print(self.cmdStr)
		self.warn.accept()

	@pyqtSlot(QModelIndex, name='index1')
	def srcDirSelected(self, index1):
		''' Get selected path from srcDirView '''

		print(f'index1 = {index1.row()}')

		### get path from srcDirView  ###
		path = self.srcDirMODEL.fileInfo(index1).absoluteFilePath().replace('/', '\\')

		self.srcDirView.expand(index1)

		print(f'path: {path}')

		### update srcFlistView ###
		self.srcFlistView.setRootIndex(self.srcFlistMODEL.setRootPath(path))

		### update self.srcPath ###
		self.srcDirPath = path

		# print(f'self.srcDirPath: {self.srcPath}')

		return path

	@pyqtSlot(QModelIndex, name='index2')
	def dstDirSelected(self, index2) -> str:
		''' Get selected path from dstDirView '''

		### get path from dstDirView ###
		path = self.dstDirMODEL.fileInfo(index2).absoluteFilePath()

		print(f'path: {path}')

		### update dstFlistView ###
		self.dstFlistView.setRootIndex(self.dstFlistMODEL.setRootPath(path))

		### update srcPath ###
		self.dstDirPath = path

		print(f'self.dstDirPath: {self.dstDirPath}')

		return path

	@pyqtSlot()
	def srcFilesSelected(self):
		try:
			stuff = []
			for i in self.srcFlistView.selectedIndexes():
				temp2 = str(f'{self.srcFlistMODEL.filePath(i)}')
				# temp2 = self.srcFlistMODEL.filePath(i)
				temp = temp2.replace("/", "\\")
				stuff.append(temp)
			# stuff.append(self.srcFlistMODEL.filePath(i))
			self.srcPaths = stuff
		except:
			print(f'{tb.print_exc()}')

		print(self.srcPaths)

		### mark Source as being selected ###
		if self.srcPaths is not []:
			self.isSrcSelected = True

		return stuff

	@pyqtSlot()
	def dstFilesSelected(self):
		dirry = str(f'\"{self.dstFlistMODEL.filePath(self.dstFlistView.selectedIndexes().pop())}\"')
		# dirry = self.dstFlistMODEL.filePath(self.dstFlistView.selectedIndexes().pop())
		dirry = dirry.replace('/', '\\')

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
		path = self.srcFlistMODEL.rootPath()
		self.srcFlistView.setRootIndex(self.srcFlistMODEL.setRootPath(path))
		print('sourceRefreshBTN clicked')

	@pyqtSlot(name='')
	def destRefresh(self):
		print('destRefreshBTN clicked')

	@pyqtSlot(name='')
	def startBackup(self):
		try:
			if self.isSrcSelected and self.isDstSeleceted:
				self.opts = '/E /MT /COPY:DT'

			if self.opts == '':
				subprocess.call(['robocopy', '/?'], shell=True)
			else:
				try:
					for i in range(self.srcPaths.__len__()):
						subprocess.call(str(f'robocopy {self.opts} {self.srcPaths[i]} {self.dstDirPath}'), shell=True)
				# print(str(f'robocopy {self.opts} {self.srcPaths[i]} {self.dstDirPath}'))
				# print(str(f'robocopy {self.opts} {str(" ").join(map(str, self.srcPaths))} {self.dstDirPath}'))
				except:
					print(f'{tb.print_exc()}')

			print(f'self.srcPath: {self.srcDirPath}')
			print(f'self.dstPath: {self.dstDirPath}')

			print(f'Source selected = {self.isSrcSelected}')
			print(f'Destination selected = {self.isDstSeleceted}')
		except:
			print(f'{tb.print_exc()}')


if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = MainWindowUI()
	window.show()
	sys.exit(app.exec_())
