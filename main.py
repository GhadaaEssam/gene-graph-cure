import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QFileDialog, QTableWidgetItem, QProgressBar
from PyQt6.QtCore import pyqtSignal, QObject, QAbstractTableModel, Qt,QThread
from PyQt6 import QtGui as qg
from gui.form_ui import Ui_MainWindow
from model.train import train_model
from model.predict import predict_model
from PyQt6.QtCore import QSettings
import pandas as pd
from PyQt6.QtGui import QTextCursor

import ctypes
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

from warnings import simplefilter
simplefilter(action="ignore",category=FutureWarning)


class Stream(QObject):
    """[Output redirection] Redirect console output to text box control"""
    newText = pyqtSignal(str)
    
    def write(self, text):
        self.newText.emit(str(text))
        QApplication.processEvents()


class TrainThread(QThread):
    def __init__(self,uiObj):
        super().__init__()
        self.uiObj = uiObj

    # Custom signal
    finished = pyqtSignal()
    
    progress = pyqtSignal(int)  # Progress signal
 
    # Thread task
    def run(self):
        # Read input files
        data_geo = pd.read_csv(self.uiObj.lineEdit_7.text(), header= 0).iloc[:,1:]
        label_geo = pd.read_csv(self.uiObj.lineEdit_8.text(),header=0).iloc[:,1]
        anchor_list = pd.read_csv(self.uiObj.lineEdit_9.text(), header= 0)
        data_x = pd.read_csv(self.uiObj.lineEdit_10.text(),header=0).iloc[:,1:]
        data_ppi_link_index = pd.read_csv(self.uiObj.lineEdit_11.text(),header=0)
        data_homolog_index = pd.read_csv(self.uiObj.lineEdit_12.text(),header=0)
        # Call model training method and pass progress signal
        train_model(data_geo,label_geo,anchor_list,data_x,data_ppi_link_index,data_homolog_index,self.progress)

class predictThread(QThread):
    def __init__(self,uiObj):
        super().__init__()
        self.uiObj = uiObj

    # Custom signal
    finished = pyqtSignal()
    
    progress = pyqtSignal(int)  # Progress signal
    tableWidget = pyqtSignal(dict)
    item_v = pyqtSignal(dict)
 
    # Thread run method
    def run(self):
        # model
        model_path = self.uiObj.lineEdit.text()

        # sample expression matrix
        data_sample = pd.read_csv(self.uiObj.lineEdit_2.text(), header= 0)
        sample_name = data_sample.iloc[:,0]
        data_geo = data_sample.iloc[:,1:]

        pw_id = pd.read_csv(r"gui/pw_id.csv", header= 0).iloc[:,1]

        # characteristic genes
        anchor_list = pd.read_csv(self.uiObj.lineEdit_3.text(), header= 0)

        # signal path network
        data_x = pd.read_csv(self.uiObj.lineEdit_4.text(),header=0).iloc[:,1:]

        # ppi network
        data_ppi_link_index = pd.read_csv(self.uiObj.lineEdit_5.text(),header=0)

        # same origin network
        data_homolog_index = pd.read_csv(self.uiObj.lineEdit_6.text(),header=0)
        
        result = predict_model(model_path,data_geo,anchor_list,data_x,data_ppi_link_index,data_homolog_index,self.progress)
        
        df = pd.concat([pd.DataFrame({"sample_name":sample_name.values}),pd.DataFrame({"predict":result["out"]})],axis=1)
        data = df.values.tolist()
        headers = list(df.columns)
        
        
        self.tableWidget.emit({"id":0,"ColumnCount":len(headers),"HorizontalHeaderLabels":headers,"RowCount":len(data)})
        for i,row in enumerate(data):
            for j,val in enumerate(row):
                self.item_v.emit({"id":0,"i":i,"j":j,"val":val})

        df_pw = pd.concat([pw_id,pd.DataFrame({"pw_w":result["pw_w"]})],axis=1)
        data_pw = df_pw.values.tolist()
        headers_pw = list(df_pw.columns)

        self.tableWidget.emit({"id":1,"ColumnCount":len(headers_pw),"HorizontalHeaderLabels":headers_pw,"RowCount":len(data_pw)})
        for i,row in enumerate(data_pw):
            for j,val in enumerate(row):
                self.item_v.emit({"id":1,"i":i,"j":j,"val":val})


class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        
        
        
        self.setupUi(self)
        self.retranslateUi(self)

        self.setWindowTitle("GC-PGE")
        self.setWindowIcon(qg.QIcon("./gui/icon.ico"))
        
        ##################

        self.console_obj = self.textEdit
       
        ##################
        # Define button messages here
        """ 1. Define select file message """
        self.toolButton.clicked.connect(lambda: self.select_file(self.lineEdit))
        self.toolButton_2.clicked.connect(lambda: self.select_file(self.lineEdit_2))
        self.toolButton_3.clicked.connect(lambda: self.select_file(self.lineEdit_3))
        self.toolButton_4.clicked.connect(lambda: self.select_file(self.lineEdit_4))
        self.toolButton_5.clicked.connect(lambda: self.select_file(self.lineEdit_5))
        self.toolButton_6.clicked.connect(lambda: self.select_file(self.lineEdit_6))
        self.toolButton_7.clicked.connect(lambda: self.select_file(self.lineEdit_7))
        self.toolButton_8.clicked.connect(lambda: self.select_file(self.lineEdit_8))
        self.toolButton_9.clicked.connect(lambda: self.select_file(self.lineEdit_9))
        self.toolButton_10.clicked.connect(lambda: self.select_file(self.lineEdit_10))
        self.toolButton_11.clicked.connect(lambda: self.select_file(self.lineEdit_11))
        self.toolButton_12.clicked.connect(lambda: self.select_file(self.lineEdit_12))

        ##################

        # Define model training-computation (button)
        self.pushButton_6.clicked.connect(self.train)
        self.pushButton.clicked.connect(self.predict)

        sys.stdout = Stream()
        sys.stdout.newText.connect(self.onUpdateText)


    ####################
    # Below define related methods, corresponding to the button messages above
    
    """ 1. Define select file method """
    def select_file(self,obj):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open file', '/path/to/initial/directory')
        if filename:
            obj.setText(filename)

    """ 2. Define log output """
    def closeEvent(self, event):
        """[Output redirection] Override closeEvent, restore stdout to default when program ends"""
        sys.stdout = sys.__stdout__
        super().closeEvent(event)
 
    def onUpdateText(self, text):
        """[Output redirection] Redirect console output to text box control"""
        cursor = self.console_obj.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self.console_obj.setTextCursor(cursor)
        self.console_obj.ensureCursorVisible()


    """ 3. Define model training """
    def train(self):
        # Disable button to prevent multiple thread starts
        self.pushButton_6.setEnabled(False)

        self.console_obj = self.textEdit
 
        # Create and start worker thread
        self.trainThread = TrainThread(self)
        self.trainThread.finished.connect(self.trainFinished)  # Connect task completion signal
        self.trainThread.progress.connect(self.updateProgress)    # Connect progress signal
 
        self.trainThread.start()  # Start thread
    def trainFinished(self):
        self.pushButton_6.setEnabled(True)
    def updateProgress(self, value):
        self.progressBar_3.setValue(value)

    """ 4. Define model prediction """
    def predict(self):
        self.pushButton.setEnabled(False)
        self.console_obj = self.textEdit_2

        # Create and start worker thread
        self.predictThread = predictThread(self)
        self.predictThread.finished.connect(self.predictFinished)  # Connect task completion signal
        self.predictThread.progress.connect(self.updateProgress2)    # Connect progress signal
        self.predictThread.tableWidget.connect(self.setTable)    # Connect table signal
        self.predictThread.item_v.connect(self.updateItem)    # Connect table signal
        self.predictThread.start()  # Start thread
        
    def predictFinished(self):
        self.pushButton.setEnabled(True)
    def updateProgress2(self, value):
        self.progressBar.setValue(value)
        
    def setTable(self, tableData):
        
        if tableData["id"] == 0:
            tableObj = self.tableWidget
        elif tableData["id"] == 1:
            tableObj = self.tableWidget_2
        tableObj.setColumnCount(tableData["ColumnCount"])
        tableObj.setHorizontalHeaderLabels(tableData["HorizontalHeaderLabels"])

        tableObj.setRowCount(tableData["RowCount"])
        


    def updateItem(self, itemData):
        if itemData["id"] == 0:
            tableObj = self.tableWidget
        elif itemData["id"] == 1:
            tableObj = self.tableWidget_2
        tableObj.setItem(itemData["i"],itemData["j"],QTableWidgetItem(str(itemData["val"])))


        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    mainWin = MyApp()
    mainWin.show()
    sys.exit(app.exec())