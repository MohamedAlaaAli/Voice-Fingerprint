from PyQt6.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QCheckBox, QWidget, QHBoxLayout, QAbstractItemView, QVBoxLayout, QProgressBar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from mainwindow1 import Ui_MainWindow
from Program_utils import security_voice_fingerprint, plot_spectrogram, record_audio
import numpy as np
import librosa
import librosa.display

users = [
    {"name": "Abdallah Magdy", "access": False},
    {"name": "Abdelrahman Emad", "access": False},
    {"name": "Mahmoud Mohamed", "access": False},
    {"name": "Mahmoud Magdy", "access": False},
    {"name": "Mohamed Ibrahim", "access": False},
    {"name": "Muhammed Alaa", "access": False},
    {"name": "Youssef Ahmed", "access": False},
    {"name": "Ziad Hossam", "access": False},
]

sentences = [
    "Open the door",
    "Unlock middle gate",
    "Grant me access",
    "None"
]

class VoiceThread(QThread):
    processingDone = pyqtSignal(object)
    
    def __init__(self, accessUsers, outputLabel, accessTabel, sentenceTabel, graphOneWidget):
        QThread.__init__(self)
        self.accessUsers = accessUsers
        self.outputLabel = outputLabel
        self.accessTabel = accessTabel
        self.sentenceTabel = sentenceTabel
        self.graphOneWidget = graphOneWidget
        
    
    def run(self):
        isAuthorized, usersProbabilities, sentence, sentencesProbabilities = security_voice_fingerprint(self.accessUsers, self.outputLabel)
        mean = np.mean(usersProbabilities)
        maximum = np.max(usersProbabilities)
        for row in range(self.accessTabel.rowCount()):
            item = self.accessTabel.item(row, 2)
            print(row)
            if item is not None:
                item.setText(f"{usersProbabilities[row]*100:.2f}%")
                
        for row in range(self.sentenceTabel.rowCount()):
            item = self.sentenceTabel.item(row, 1)
            print(row)
            if item is not None:
                item.setText(f"{sentencesProbabilities[row] * 100:.2f}%")
        canvas = plot_spectrogram()
        while self.graphOneWidget.layout().count():
            item = self.graphOneWidget.layout().takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.graphOneWidget.layout().addWidget(canvas)
        
        
    

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__()
        self.setupUi(self)
        self.accessTabel.setColumnCount(3)
        self.accessTabel.setHorizontalHeaderLabels(["Name", "Access", "Ratio"])
        self.accessTabel.setRowCount(len(users))
        self.accessTabel.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.accessTabel.setColumnWidth(0, 150)
        self.accessTabel.setColumnWidth(1, 50)
        self.accessTabel.setColumnWidth(2, 50)
        self.accessTabel.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.accessTabel.setAlternatingRowColors(True)
        self.accessTabel.setShowGrid(False)

        for i, user in enumerate(users):
            self.accessTabel.setItem(i, 0, QTableWidgetItem(user["name"]))
            widget = QWidget()
            checkbox = QCheckBox()
            checkbox.setChecked(user["access"])
            checkbox.stateChanged.connect(lambda state, i=i: self.update_user_access(i, state))
            layout = QHBoxLayout()
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(layout)
            self.accessTabel.setCellWidget(i, 1, widget)
            self.accessTabel.setItem(i, 2, QTableWidgetItem("0%"))

        self.sentenceTabel.setColumnCount(2)
        self.sentenceTabel.setHorizontalHeaderLabels(["Sentence", "Ratio"])
        self.sentenceTabel.setRowCount(len(sentences))
        self.sentenceTabel.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.sentenceTabel.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.sentenceTabel.setColumnWidth(0, 200)
        self.sentenceTabel.setColumnWidth(1, 50)
        self.sentenceTabel.setAlternatingRowColors(True)
        self.sentenceTabel.setShowGrid(False)
        for i, sentence in enumerate(sentences):
            self.sentenceTabel.setItem(i, 0, QTableWidgetItem(sentence))
            self.sentenceTabel.setItem(i, 1, QTableWidgetItem("0%"))

        self.recordBtn.clicked.connect(self.record)
        self.outputLabel.setText("Hello, how can I help you?")

        layout = QVBoxLayout()
        self.graphOneWidget.setLayout(layout)
        
        
    
    def record(self):
        accessUsers = []
        for i, user in enumerate(users):
            if user["access"]:
                accessUsers.append(user["name"])
        record_audio(self.outputLabel, 2, "live_audio.wav")
        
        self.progressTimer = QTimer()
        self.progressTimer.timeout.connect(self.updateProgressBar)
        self.progressTimer.start(100)
        
        self.stopped = False
        self.thread = VoiceThread(accessUsers, self.outputLabel, self.accessTabel, self.sentenceTabel, self.graphOneWidget)
        self.thread.start()
        
    def updateProgressBar(self):
        print("Processing....")

    def update_user_access(self, index, state):
        users[index]["access"] = bool(state)
        print(users)


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()