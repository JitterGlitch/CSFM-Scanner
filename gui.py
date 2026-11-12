import sys
from collections import defaultdict

import resources_rc
from pathlib import Path

from ui_main_window import Ui_MainWindow
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QFileSystemWatcher, QByteArray, QBuffer
from PySide6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QPushButton, QListView, QWidget, QFileDialog, QListWidgetItem, QTreeWidgetItem, QHBoxLayout, QLabel
from CSFM_Parser import CsfmParser, DifficultyOutput, NoteCheck, ChartIssue, TargetProperties, IssueLevel, NoteCheckOnScreenReason, TargetTypes, Note


def target_list_to_rich_text(target_list):
    rich_text = ""
    #TODO: Labels support images via rich-text.
    # Use that instead

    for target in target_list:
        base_note = TargetTypes.get_base_note(target)
        match base_note:
            case TargetTypes.Triangle:
                note_image = u":resources/Images/Notes/Triangle.png"
            case TargetTypes.Circle:
                note_image = u":resources/Images/Notes/Circle.png"
            case TargetTypes.Cross:
                note_image = u":resources/Images/Notes/Cross.png"
            case TargetTypes.Square:
                note_image = u":resources/Images/Notes/Square.png"
            case TargetTypes.SlideL:
                note_image = u":resources/Images/Notes/SlideL.png"
            case TargetTypes.SlideR:
                note_image = u":resources/Images/Notes/SlideR.png"
            case TargetTypes.SlideChainL:
                note_image = u":resources/Images/Notes/ChainSlideL.png"
            case TargetTypes.SlideChainR:
                note_image = u":resources/Images/Notes/ChainSlideR.png"
            case _:
                note_image = u":resources/Images/Notes/Circle.png"


        note_image_string =f'<img src={note_image} width="15" height="15" style="vertical-align: middle;">'
        rich_text = rich_text + note_image_string

    return rich_text

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
        self.main_box.csfm_issues_treeview.clear()

        self.issues = self.parser.scan_csfm(csfm_location)
        self.issues = sorted(self.issues,key=lambda issue: issue.timestamp)

        self.main_box.csfm_file_label.setText(Path(csfm_location).name)
        self.main_box.csfm_song_name_label.setText(self.parser.get_song_name())
        self.main_box.csfm_difficulty_label.setText(self.parser.get_difficulty())

        self.display_issues()

    def get_issue_description(self,issue: ChartIssue):
        timestamp = issue.timestamp
        note_type = issue.get_note_type_string()
        target_type = issue.get_target().get_type()
        target_icon = target_list_to_rich_text([target_type])
        precision = self.main_box.target_spawn_precision_combobox.currentEnum().name

        print(timestamp)
        print(issue.extra_info)

        match issue.type:

            case NoteCheck.NOTE_SPAWN_ON_SCREEN:
                match issue.extra_info["Reason"]:
                    case NoteCheckOnScreenReason.ON_SCREEN:
                        return f"{target_icon} spawns on screen"
                    case NoteCheckOnScreenReason.DIFFERENT_TYPE:
                        other_target = issue.extra_info["Spawn Source"].get_type()
                        other_target_icon = target_list_to_rich_text([other_target])

                        return f"{target_icon} spawns from note of different type {other_target_icon}"
                    case NoteCheckOnScreenReason.SAME_TYPE:
                        return f"{target_icon} spawns from note of same type"
                    case NoteCheckOnScreenReason.ITSELF:
                        return f"{target_icon} spawns from itself"
                    case _:
                        return f"Note spawn check returned Error"
            case NoteCheck.NOTE_PHANTOM:
                return f"At {timestamp} {note_type} has 0 Distance"
            case NoteCheck.NEWBIE_UNSET_NOTE:
                return f"At {timestamp} {note_type} uses default placements"
            case _:
                return f"At {timestamp} unimplemented error description"

    def build_issue_data_tree(self,chart_issues_list:list[ChartIssue]):
        grouped = defaultdict(list)
        for issue in chart_issues_list:
            grouped[issue.timestamp].append(issue)
        return dict(grouped)



    def display_issues(self):
        self.main_box.csfm_issues_treeview.clear()

        grouped_issues = self.build_issue_data_tree(self.issues)

        for timestamp,issue in grouped_issues.items():
            issue_item = QTreeWidgetItem([str(timestamp)])
            target_list = issue[0].note.get_type()
            note_image_list = target_list_to_rich_text(target_list)
            note_string = ""
            for note in note_image_list:
                note_string = note_string + note

            label = QLabel(note_string)
            label.setTextFormat(Qt.TextFormat.RichText)

            self.main_box.csfm_issues_treeview.addTopLevelItem(issue_item)
            self.main_box.csfm_issues_treeview.setItemWidget(issue_item,1, label)

            for i in issue:
                issue_label = QLabel(self.get_issue_description(i))
                issue_label.setTextFormat(Qt.TextFormat.RichText)
                leaf = QTreeWidgetItem()
                issue_item.addChild(leaf)
                self.main_box.csfm_issues_treeview.setItemWidget(leaf,0, issue_label)

            self.main_box.csfm_issues_treeview.expandAll()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    main_window = MainWindow()
    main_window.show()
    app.exec()