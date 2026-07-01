import sys
from pathlib import Path

from PySide6.QtGui import QColor

from ui_main_window import Ui_MainWindow
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QFileSystemWatcher
from PySide6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QPushButton, QListView, QWidget, QFileDialog, QListWidgetItem
from main import CsfmParser, DifficultyOutput


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.main_box = Ui_MainWindow()
        self.main_box.setupUi(self)
        self.main_box.button.pressed.connect(self.load_csfm)
        self.parser = CsfmParser()
        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self.watcher_update)

    def watcher_update(self,path):
        print("running")
        for path in self.watcher.files():
            self.watcher.removePath(path)

        self.watcher.addPath(str(path))
        self.load_csfm([path,'*.csfm'])
    def load_csfm(self,csfm_location:str=None):
        if csfm_location is None:
            csfm_location = QFileDialog.getOpenFileName(self,
                                                         f"Open CSFM",
                                                         None,
                                                         "*.csfm")
            self.watcher.addPath(str(csfm_location[0]))
            if csfm_location == "":
                print("User didn't select image")
                return


        self.main_box.csfm_issues_listview.clear()

        issues = self.parser.scan_csfm(csfm_location[0])

        self.main_box.csfm_file_label.setText(Path(csfm_location[0]).name)
        self.main_box.csfm_song_name_label.setText(self.parser.get_song_name())
        self.main_box.csfm_difficulty_label.setText(self.parser.get_difficulty())

        for issue in issues:
            issue_obj = QListWidgetItem(issue[1],self.main_box.csfm_issues_listview)
            if issue[0] == "Error":
                issue_obj.setBackground(QColor(32+150,32+110,36+110,50))
        if not issues:
            issue_obj = QListWidgetItem("No issues detected",self.main_box.csfm_issues_listview)








if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    main_window = MainWindow()
    main_window.show()
    app.exec()