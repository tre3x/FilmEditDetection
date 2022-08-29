import os, sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from functools import partial
from main import run_tool


os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('NPN Tape Analyzer')
        self.setGeometry(100, 100, 600, 550)
        self.here = os.path.dirname(os.path.abspath(__file__))
        DEFAULT_OUTDIR = os.path.join(self.here, "json_mep")
        DEFAULT_CONFIG_PATH = os.path.join(self.here, "configs", "vgg16.json")
        DEFAULT_MODEL_PATH = os.path.join(self.here, "trained-models", "cutdetection-model")
        self.datadict = {'filmpath':"<No File>", 'modelpath':"<No File>", 'outputformat':2, 'cinemetrics-server-upload':False, "outdir":DEFAULT_OUTDIR,
                        "config":DEFAULT_CONFIG_PATH, "submitter-name":"", "movie-title":"", "movie-year":"", "submitter-email":""}
        if os.path.exists(DEFAULT_MODEL_PATH):
            self.datadict['modelpath'] = DEFAULT_MODEL_PATH
        self.initUI()

    def initUI(self):
        self.lbl = QLabel('Cut Detector Tool', self)
        self.lbl.setGeometry(20, 10, 231, 31)
        self.lbl.setFont(QFont("MS Shell Dlg 2", 16, QFont.Bold))

        self.lbl2 = QLabel('Film Path :',self)
        self.lbl2.setGeometry(20, 60, 100, 20)
        self.lbl2.setFont(QFont("MS Shell Dlg 2", 9, QFont.Bold))
        
        self.filmpath = QLineEdit(self)
        self.filmpath.setGeometry(130, 60, 400, 20)
        self.filmpath.setText(self.datadict['filmpath'])
        self.filmpath.setStyleSheet("color: rgb(128, 128, 128);")
        self.filmpath.setReadOnly(True)

        self.filmpathbtn = QPushButton('', self)
        self.filmpathbtn.clicked.connect(partial(self.getfilepath, self.filmpath))
        self.filmpathbtn.setIcon(QIcon('img/index.jpg'))
        self.filmpathbtn.setIconSize(QSize(24,24))
        self.filmpathbtn.setGeometry(550, 60, 24, 20)

        self.lbl11 = QLabel('Config File Path :',self)
        self.lbl11.setGeometry(20, 100, 100, 20)
        self.lbl11.setFont(QFont("MS Shell Dlg 2", 9, QFont.Bold))
        
        self.configpath = QLineEdit(self)
        self.configpath.setGeometry(130, 100, 400, 20)
        self.configpath.setText(self.datadict["config"])
        self.configpath.setStyleSheet("color: rgb(128, 128, 128);")
        self.configpath.setReadOnly(True)

        self.configpathbtn = QPushButton('', self)
        self.configpathbtn.clicked.connect(partial(self.getfolderpath, self.configpath))
        self.configpathbtn.setIcon(QIcon('img/index.jpg'))
        self.configpathbtn.setIconSize(QSize(24,24))
        self.configpathbtn.setGeometry(550, 100, 24, 20)

        self.lbl3 = QLabel('Model Path :',self)
        self.lbl3.setGeometry(20, 140, 100, 20)
        self.lbl3.setFont(QFont("MS Shell Dlg 2", 9, QFont.Bold))
        
        self.modelpath = QLineEdit(self)
        self.modelpath.setGeometry(130, 140, 400, 20)
        self.modelpath.setText(self.datadict["modelpath"])
        self.modelpath.setStyleSheet("color: rgb(128, 128, 128);")
        self.modelpath.setReadOnly(True)

        self.modelpathbtn = QPushButton('', self)
        self.modelpathbtn.clicked.connect(partial(self.getfolderpath, self.modelpath))
        self.modelpathbtn.setIcon(QIcon('img/index.jpg'))
        self.modelpathbtn.setIconSize(QSize(24,24))
        self.modelpathbtn.setGeometry(550, 140, 24, 20)

        self.lbl10 = QLabel('Output File Path :',self)
        self.lbl10.setGeometry(20, 180, 100, 20)
        self.lbl10.setFont(QFont("MS Shell Dlg 2", 9, QFont.Bold))
        
        self.outdir = QLineEdit(self)
        self.outdir.setGeometry(130, 180, 400, 20)
        self.outdir.setText(self.datadict["outdir"])
        self.outdir.setStyleSheet("color: rgb(128, 128, 128);")
        self.outdir.setReadOnly(True)

        self.outdirbtn = QPushButton('', self)
        self.outdirbtn.clicked.connect(partial(self.getfolderpath, self.outdir))
        self.outdirbtn.setIcon(QIcon('img/index.jpg'))
        self.outdirbtn.setIconSize(QSize(24,24))
        self.outdirbtn.setGeometry(550, 180, 24, 20)

        self.lbl4 = QLabel('Output Format :',self)
        self.lbl4.setGeometry(20, 220, 100, 20)
        self.lbl4.setFont(QFont("MS Shell Dlg 2", 9, QFont.Bold))
        
        self.cinemetricscombobox = QComboBox(self)
        self.cinemetricscombobox.addItems(['CUTS : CSV file containing frame index of cuts', 'SHOTS: CSV file containing timestamps of shots',
                                'MEPFORMAT: JSON format containing timestamps of shots in Media Ecology Project annotation format', 
                                'CINEMETRICS: CNS formatted file which is supported for uploading to cinemetrics'])
        self.cinemetricscombobox.setCurrentIndex(self.datadict["outputformat"])
        self.cinemetricscombobox.setGeometry(130, 220, 450, 20)

        self.cinemetricscombobox.currentTextChanged.connect(self.upload_cinemetrics)

        self.submit_btn = QPushButton('SUBMIT', self)
        self.submit_btn.setGeometry(210, 460, 220, 40)
        self.submit_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.submit_btn.clicked.connect(self.submit)

    def upload_cinemetrics(self):
        self.lbl5 = QLabel('Do you Want to submit the result to Cinemetrics Server?',self)
        self.lbl5.setGeometry(20, 300, 350, 20)
        self.lbl5.setFont(QFont("MS Shell Dlg 2", 8, QFont.Bold))
            
        self.cinemetrics_upload_combobox = QComboBox(self)
        self.cinemetrics_upload_combobox.addItems(['No', 'Yes'])
        self.cinemetrics_upload_combobox.setCurrentIndex(self.datadict["cinemetrics-server-upload"])
        self.cinemetrics_upload_combobox.setGeometry(380, 300, 100, 20)
        if self.cinemetricscombobox.currentIndex() == 0:
            self.datadict["outdir"] = os.path.join(self.here, "csv_cuts")
            self.outdir.setText(self.datadict["outdir"])
        if self.cinemetricscombobox.currentIndex() == 1:
            self.datadict["outdir"] = os.path.join(self.here, "csv_shots")
            self.outdir.setText(self.datadict["outdir"])
        if self.cinemetricscombobox.currentIndex() == 2:
            self.datadict["outdir"] = os.path.join(self.here, "json_mep")
            self.outdir.setText(self.datadict["outdir"])
        elif self.cinemetricscombobox.currentIndex() == 3:
            self.datadict["outdir"] = os.path.join(self.here, "cinemetrics")
            self.outdir.setText(self.datadict["outdir"])

            self.lbl5.show()
            self.cinemetrics_upload_combobox.show()
            self.cinemetrics_upload_combobox.currentTextChanged.connect(self.upload_cinemetrics_info)

    def upload_cinemetrics_info(self):
        self.lbl6 = QLabel('Sumitter Name : ',self)
        self.lbl6.setGeometry(20, 330, 100, 20)
        self.lbl6.setFont(QFont("MS Shell Dlg 2", 8, QFont.Bold))

        self.submittername = QLineEdit(self)
        self.submittername.setGeometry(140, 330, 300, 20)
        self.submittername.setStyleSheet("color: rgb(128, 128, 128);")
        self.submittername.setText(self.datadict['submitter-name'])
        
        self.lbl7 = QLabel('Movie Title : ',self)
        self.lbl7.setGeometry(20, 360, 100, 20)
        self.lbl7.setFont(QFont("MS Shell Dlg 2", 8, QFont.Bold))

        self.movietitle = QLineEdit(self)
        self.movietitle.setGeometry(140, 360, 300, 20)
        self.movietitle.setStyleSheet("color: rgb(128, 128, 128);")
        self.movietitle.setText(self.datadict['movie-title'])

        self.lbl8 = QLabel('Movie Year : ',self)
        self.lbl8.setGeometry(20, 390, 100, 20)
        self.lbl8.setFont(QFont("MS Shell Dlg 2", 8, QFont.Bold))

        self.movieyear = QLineEdit(self)
        self.movieyear.setGeometry(140, 390, 300, 20)
        self.movieyear.setStyleSheet("color: rgb(128, 128, 128);")
        self.movieyear.setText(self.datadict['movie-year'])

        self.lbl9 = QLabel('Submitter Email : ',self)
        self.lbl9.setGeometry(20, 420, 100, 20)
        self.lbl9.setFont(QFont("MS Shell Dlg 2", 8, QFont.Bold))

        self.submitteremail = QLineEdit(self)
        self.submitteremail.setGeometry(140, 420, 300, 20)
        self.submitteremail.setStyleSheet("color: rgb(128, 128, 128);")
        self.submitteremail.setText(self.datadict['submitter-email'])
        
        if self.cinemetrics_upload_combobox.currentIndex() == 1:
            self.lbl6.show()
            self.lbl7.show()
            self.lbl8.show()
            self.lbl9.show()
            self.submittername.show()
            self.movietitle.show()
            self.movieyear.show()
            self.submitteremail.show()
            
    def getfilepath(self, field):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self,"Select media file","","",options=options)
        if filename:
            field.setText(filename)

    def getfolderpath(self, field):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        foldername = QFileDialog.getExistingDirectory(self,"Select model-folder")
        if foldername:
            field.setText(foldername)

    def submit(self):
        self.datadict['filmpath'] = self.filmpath.text()
        self.datadict['modelpath'] = self.modelpath.text()
        if self.cinemetricscombobox.currentIndex()==0:
            self.datadict['outputformat'] = 'cuts'
        elif self.cinemetricscombobox.currentIndex()==1:
            self.datadict['outputformat'] = 'shots'
        elif self.cinemetricscombobox.currentIndex()==2:
            self.datadict['outputformat'] = 'mepformat'
        elif self.cinemetricscombobox.currentIndex()==3:
            self.datadict['outputformat'] = 'cinemetrics'
            if self.cinemetrics_upload_combobox.currentIndex()==1:
                self.datadict['cinemetrics-server-upload'] = True
                self.datadict['submitter-name'] = self.submittername.text()
                self.datadict['movie-title'] = self.movietitle.text()
                self.datadict['movie-year'] = self.movieyear.text()
                self.datadict['submitter-email'] = self.submitteremail.text()
        print(self.datadict)
        run_tool(self.datadict['filmpath'], self.datadict['modelpath'], self.datadict['outputformat'], self.datadict['outdir'], self.datadict['config'], self.datadict['cinemetrics-server-upload'],
                     self.datadict['submitter-name'], self.datadict['movie-title'], self.datadict['movie-year'], self.datadict['submitter-email'])

    def closeEvent(self, event):
            reply = QMessageBox.question(
                self, "Message",
                "You are exiting the application. Are you sure you want to quit?",
                QMessageBox.Close | QMessageBox.Cancel,
                QMessageBox.Close)

            if reply == QMessageBox.Close:
                event.accept()
            else:
                event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())

'''
1. Add default output directory, and default config file to the UI
2. Add respective changes to API
3. Add processing and final result UI
'''