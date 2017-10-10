# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import drivelib as dl

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        """Initial procedures for GUI"""
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(712, 621)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.formLayout = QtWidgets.QFormLayout(self.centralwidget)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.pushButton_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeWidget.sizePolicy().hasHeightForWidth())
        self.treeWidget.setSizePolicy(sizePolicy)
        self.treeWidget.setMinimumSize(QtCore.QSize(177, 531))
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.horizontalLayout.addWidget(self.treeWidget)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.gridLayout_3.setContentsMargins(-1, -1, -1, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.horizontalLayout.addLayout(self.gridLayout_3)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.LabelRole, self.horizontalLayout)
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setObjectName("listWidget")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.listWidget)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.pushButton_3)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.pushButton)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 712, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        #Non-generated code: slots and events
        self.pushButton_3.clicked.connect(self.handleExit)
        self.listWidget.itemDoubleClicked.connect(self.handleOnDoubleClick)
        self.pushButton_2.clicked.connect(self.handleOpenFileNamesDialog)
        self.treeWidget.headerItem().setText(0, "Folders: ")
        self.treeWidget.itemClicked.connect(self.handleFolderOnClick)
        self.retranslateUi(MainWindow)
        self.pushButton.clicked.connect(self.handleUpdate)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.keyPressed = QtCore.pyqtSignal()
        self.listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.handleContextMenu)
        try:
            #Get service object, retrieve index of files
            print("Starting service...")
            self.service = dl.getService()
            self.items = dl.getAllElements(self.service)
            print('items got')
            #Build ierarchy for treeWidget
            self.tree = dl.getTreeOfFolders(self.service,self.items,'root')
            print("tree's built.")
        except Exception as ex:
            print("Error occured when service began to run")
            #self.error(ex)
            sys.exit(1)

        self.current = 'root'
        self.folders = {}  #Dictionary of folders and QTreeWidgetsItems corresponging to them
        self.folderItems = {} #Dictionary of files and QListWidgetItmes coresponding to them
        self.updateUI() #Refresh view on screen

    def restart_service(self):
        """Retreive new service object if connection broke or for new user sign-in"""
        try:
            print("Starting service...")
            self.service = dl.getService()
            self.rootId = dl.getRootId(self.service)
            self.items = dl.getAllElements(self.service) #Get index of all files at cloud which were not trashed
            print('items got')
            self.tree = dl.getTreeOfFolders(self.service,self.items,'root') #Get tree structure for treeWidget
            print("tree's built.")
        except Exception as ex:
            self.error(ex)
            sys.exit(1)
    def handleDownload(self, fileId):
        """Handling request for handleDownload"""
        try:
            if  fileId in self.folders:
                raise dl.DError("API doesn't allow to donwload folders.") #Drive API doesn't allow to download folders as regular files
            from PyQt5.QtWidgets import QFileDialog   
            options = QFileDialog.Options()
            file = str(QFileDialog.getExistingDirectory(caption="Select Directory")) #Calling standart Windows's "Select Direction" 
            if file: #If file choosen
                record = iter(filter(lambda blob: blob['id']==fileId,self.items)) #Find record of file with file Id equal to fileId
                record = next(record)
                name  = record['name'] 
                path = file+"/"+name
                dl.download(self.service,fileId,path) #Downloading
        except Exception as ex:
            self.error(ex)

    def handleExit(self):
        """Handle click on Exit button"""
        import os
        #Get path to credentials file
        path = os.path.join(dl.home_dir,dl.credentials_dir) 
        print(path)
        file = os.path.join(path,dl.client_cred)
        print(file)
        os.remove(file)
        #Remove credentials file
        print("Exists?:",os.path.exists(file)) #Check, does it exist after removal
        self.restart_service() #Restart service and get new service object. Browser window will apear with Goggle Sign IN
        self.updateUI() #Update UI with new data

    def handleUpdate(self):
        """Handle click on Update button"""
        self.restart_service()
        self.updateUI()

    def handleDelete(self, fileId):
        """Handle click on Delete action in context menu"""
        try:
            print(fileId)
            dl.remove(self.service,fileId)
            deletedFileRec = next(iter(filter(lambda x:x['id']==fileId,self.items))) #FInd reocrd about deleted file
            self.items.remove(deletedFileRec) #Remove it from index
            self.updateContents() #Update list of files
        except Exception as ex:
            self.error(ex)

    def handleContextMenu(self,event):
        """Context menu for ListWidget"""
        selected = self.listWidget.selectedItems()
        try:
            ids = map(self.getIdOfFile,selected)
            id = next(iter(ids))
        except:
            print("Warning. Ids not found")
        menu = QtWidgets.QMenu()
        mouse = QtGui.QCursor
        download_act = menu.addAction("Dowload")
        delete_act = menu.addAction("Delete")
        action = menu.exec((mouse.pos()))
        if action == download_act:
            print("Downloading")
            self.handleDownload(id)
        elif action==delete_act:
            print("Deleting")
            self.handleDelete(id)

    def error(self, err):
        """MessageBox for errors"""
        from PyQt5.QtWidgets import QMessageBox
        infoBox = QMessageBox() 
        infoBox.setIcon(QMessageBox.Information)
        infoBox.setText("Errors")
        infoBox.setInformativeText(str(err))
        infoBox.setWindowTitle("Error")
        infoBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        infoBox.setEscapeButton(QMessageBox.Close)
        infoBox.exec_()
        print("Handling errors...")
        print(err)

    def updateUI(self):
        """Update UI after changing data of app"""
        print("Updating UI")
        try:
            self.items = dl.getAllElements(self.service)
            self.tree = dl.getTreeOfFolders(self.service,self.items,'root')
            self.updateFolders()
            self.updateContents()
        except Exception as ex:
            print("Error occured while updating UI")
            self.error(ex)

    def handleOpenFileNamesDialog(self):
        """Handle opening files for uploading"""
        from PyQt5.QtWidgets import QFileDialog    
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(QtWidgets.QWidget(),"Open Files...", "","All Files (*);;Python Files (*.py)", options=options)
        try:
            if files:
                for x in files:
                    dl.upload(self.service,x,self.current)
            self.updateUI()
        except Exception as ex:
            self.error(ex)

    def handleFolderOnClick(self,item,col):
        """Handle for clicking on TreeWidget. It will cause changing current folder and updating UI for current dfolder"""
        print("Started to handle click...")
        self.current = list(filter(lambda x: x[1]==item, self.folders.items()))[0][0]
        print("Current: ", self.current)
        self.updateContents()

    def getIdOfFile(self,item):
        """Get ID of item in ListWidget."""
        id = list(filter(lambda x: x[1]==item, self.folderItems.items())) 
        #self.folderItems is a dictionary: key:value, where key is fileID, value is QListWidgetItem corresponging to that fileID
        #id = list of tuples (key,value)
        id = id[0][0] #taking key element of first item retrieved
        return id

    def handleOnDoubleClick(self,item):
        """Handling double click on ListWidget, If folder was clikced, make folder current and update ListWidget
        to show contents of that folder
        """
        try:
            id = filter(lambda x: x[1]==item, self.folderItems.items())
            id = list(id)[0][0]
            record = list(filter(lambda x: x['id']==id,self.items))[0]
            if record['mimeType']=="application/vnd.google-apps.folder":
                self.current=record['id']
                self.updateContents()
        except Exception as ex:
            self.error(ex)
    def updateContents(self):
        """Update ListWidget"""
        try:
            self.folderItems={}
            self.listWidget.clear()
            print("Updating folders...")
            items = dl.getContentsOfFolder(self.service,self.items,self.current)
            for item in items:
                if item['mimeType'] == 'application/vnd.google-apps.folder' and not item['name'].endswith('/'):
                    item['name']+="/"
                else:
                    pass
                current = QtWidgets.QListWidgetItem(self.listWidget)
                current.setText(item['name'])
                self.folderItems[item['id']]=current; #self.listWidget.addItem(item['name'])
        except Exception as er:
            self.error(er)
            sys.exit(1)
    def updateFolders(self):
        """Update TreeWidget (wrapper for updateTree which is recursive)"""
        self.treeWidget.clear()
        self.updateTree(self.treeWidget)

    def updateTree(self,parent,node=None):
        """Fill TreeWidget with folders in self.items"""
        try:
            print("Updating tree...")
            self.folder = {}
            col = 0
            if not node:
                node = dl.getTreeOfFolders(self.service,self.items,'root')
            current = QtWidgets.QTreeWidgetItem(parent)
            self.folders[node['id']] = current
            current.setText(col,node['name'])
            if node['hasDescendants']:
                for x in node['descendants']:
                    self.updateTree(current,x)
        except Exception as err:
            self.error(err)
            sys.exit(1)

    def retranslateUi(self, MainWindow):
        """Show captions"""
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Drive API App"))
        self.pushButton_2.setText(_translate("MainWindow", "Upload"))
        self.pushButton_3.setText(_translate("MainWindow", "Exit"))
        self.pushButton.setText(_translate("MainWindow", "Update"))



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
