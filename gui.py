import sys
from pathlib import Path

from PySide6.QtGui import QColor

from ui_main_window import Ui_MainWindow
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QFileSystemWatcher
from PySide6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QPushButton, QListView, QWidget, QFileDialog, QListWidgetItem
from CSFM_Parser import CsfmParser, DifficultyOutput, NoteCheck, ChartIssue, TargetProperties, IssueLevel

def get_issue_description(issue:ChartIssue):
    timestamp = issue.parser.get_time_from_tick(issue.timestamp)
    issue_level = issue.level.name
    note_type = issue.note_type

    spawn_position = "Unfilled"

    if issue.extra_info:
        spawn_position = issue.extra_info["Note Spawn Position"]


    match issue.type:
        case NoteCheck.NOTE_SPAWN_ON_SCREEN:
            return f"{issue_level} - At {timestamp} {note_type} spawns on screen. Exact spawn position {spawn_position}"
        case NoteCheck.NOTE_SPAWN_FROM_OTHER:
            different_note_type = issue.extra_info["Other Note Type"]
            return f"{issue_level} - At {timestamp} {note_type} spawns from {different_note_type}. Exact spawn position {spawn_position}"
        case NoteCheck.NOTE_SPAWN_FROM_SAME:
            return f"{issue_level} - At {timestamp} {note_type} spawns from same note type. Exact spawn position {spawn_position}"
        case NoteCheck.NOTE_SPAWN_0_DISTANCE:
            return f"{issue_level} - At {timestamp} {note_type} is a Phantom Note"
        case NoteCheck.NOTE_PLACEMENT_OUTSIDE_GRID:
            return f"{issue_level} - At {timestamp} {note_type} is outside of the grid"
        case NoteCheck.STYLE_MULTI_880_DISTANCE:
            return f"{issue_level} - At {timestamp} {note_type} has 880 distance or lower"
        case NoteCheck.NEWBIE_UNSET_NOTE:
            return f"{issue_level} - At {timestamp} {note_type} has placeholder placements"
        case _:
            return f"At {timestamp} unimplemented error description"


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
                                                         "*.csfm")

            if csfm_location == "":
                print("User didn't select image")
                return

            self.watcher.addPath(str(csfm_location[0]))


        self.currently_loaded_csfm = csfm_location
        self.main_box.csfm_issues_listview.clear()

        self.issues = self.parser.scan_csfm(csfm_location[0],self.main_box.target_spawn_precision_combobox.currentEnum())
        self.issues = sorted(self.issues,key=lambda issue: issue.timestamp)

        self.main_box.csfm_file_label.setText(Path(csfm_location[0]).name)
        self.main_box.csfm_song_name_label.setText(self.parser.get_song_name())
        self.main_box.csfm_difficulty_label.setText(self.parser.get_difficulty())

        self.display_issues()


    def display_issues(self):
        self.main_box.csfm_issues_listview.clear()
        print(self.filter_dict)
        for issue in self.issues:
            if self.filter_dict[issue.type.name] == 2:
                issue_string = get_issue_description(issue)
                issue_obj = QListWidgetItem(issue_string,self.main_box.csfm_issues_listview)
                if issue.level == IssueLevel.Error:
                    issue_obj.setBackground(QColor(32+150,32+110,36+110,50))
            if not self.issues:
                issue_obj = QListWidgetItem("No issues detected",self.main_box.csfm_issues_listview)






if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    main_window = MainWindow()
    main_window.show()
    app.exec()