import sys
from pathlib import Path

from PySide6.QtGui import QColor

from ui_main_window import Ui_MainWindow
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QFileSystemWatcher
from PySide6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QPushButton, QListView, QWidget, QFileDialog, QListWidgetItem
from CSFM_Parser import CsfmParser, DifficultyOutput, NoteCheck, ChartIssue, TargetProperties, IssueLevel, NoteCheckOnScreenReason


class MainWindow(QMainWindow):
    FilterChanged = Signal()
    def __init__(self):
        super(MainWindow, self).__init__()
        self.main_box = Ui_MainWindow()
        self.filter_dict = {}
        self.issues = ()
        self.main_box.setupUi(self,self.filter_dict)
        self.main_box.button.pressed.connect(self.load_csfm)
        self.main_box.target_spawn_precision_combobox.currentEnumChanged.connect(self.target_precision_changed)
        for group_list in self.main_box.group_lists:
            group_list.itemChanged.connect(self.display_issues)
        self.parser = CsfmParser()
        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self.watcher_update)
        self.currently_loaded_csfm = None

        self.load_csfm("/home/jitterglitch/PycharmProjects/CSFM-Helper/Test Data/JitterGlitch Chart Pack/FOMENT - 7 HD.csfm")

    def watcher_update(self,path):
        print("running")
        for path in self.watcher.files():
            self.watcher.removePath(path)

        self.watcher.addPath(str(path))
        self.load_csfm([path,'*.csfm'])
    def target_precision_changed(self):
        if self.parser.metadata != {}:
            self.load_csfm(self.currently_loaded_csfm)
    def load_csfm(self,csfm_location:str=None):
        if csfm_location is None:
            csfm_location = QFileDialog.getOpenFileName(self,
                                                         f"Open CSFM",
                                                         None,
                                                         "*.csfm")[0]
            if csfm_location == "":
                print("User didn't select image")
                return

            self.watcher.addPath(str(csfm_location))


        self.currently_loaded_csfm = csfm_location
        self.main_box.csfm_issues_listview.clear()

        self.issues = self.parser.scan_csfm(csfm_location)
        self.issues = sorted(self.issues,key=lambda issue: issue.timestamp)

        self.main_box.csfm_file_label.setText(Path(csfm_location).name)
        self.main_box.csfm_song_name_label.setText(self.parser.get_song_name())
        self.main_box.csfm_difficulty_label.setText(self.parser.get_difficulty())

        self.display_issues()

    def get_issue_description(self,issue: ChartIssue):
        timestamp = issue.chart.get_time_from_tick(issue.timestamp)
        note_type = issue.get_note_type_string()
        target_type = issue.get_target().get_type()
        precision = self.main_box.target_spawn_precision_combobox.currentEnum().name

        print(timestamp)
        print(issue.extra_info)

        match issue.type:

            case NoteCheck.NOTE_SPAWN_ON_SCREEN:
                match issue.extra_info["Reason"]:
                    case NoteCheckOnScreenReason.ON_SCREEN:
                        return f"At {timestamp} {target_type} spawns on screen"
                    case NoteCheckOnScreenReason.DIFFERENT_TYPE:
                        return f"At {timestamp} {target_type} spawns from note of different type {issue.extra_info["Spawn Source"].get_type()}"
                    case NoteCheckOnScreenReason.SAME_TYPE:
                        return f"At {timestamp} {target_type} spawns from note of same type"
                    case NoteCheckOnScreenReason.ITSELF:
                        return f"At {timestamp} {target_type} spawns from itself"
                    case _:
                        return f"Note spawn check returned Error"
            case NoteCheck.NOTE_PHANTOM:
                return f"At {timestamp} {note_type} has 0 Distance"
            case NoteCheck.NEWBIE_UNSET_NOTE:
                return f"At {timestamp} {note_type} uses default placements"
            case _:
                return f"At {timestamp} unimplemented error description"
    def display_issues(self):
        self.main_box.csfm_issues_listview.clear()
        print(self.filter_dict)
        for issue in self.issues:
            if self.filter_dict[issue.type.name] == 2:
                issue_string = self.get_issue_description(issue)
                issue_obj = QListWidgetItem(issue_string,self.main_box.csfm_issues_listview)
                # if issue.level == IssueLevel.Error:
                #     issue_obj.setBackground(QColor(32+150,32+110,36+110,50))
            if not self.issues:
                issue_obj = QListWidgetItem("No issues detected",self.main_box.csfm_issues_listview)






if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    main_window = MainWindow()
    main_window.show()
    app.exec()