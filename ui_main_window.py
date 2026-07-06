from PySide6.QtCore import (QCoreApplication, QLocale,
                            QMetaObject, QRect,
                            QSize, Qt, Signal)
from PySide6.QtGui import (QFont, QIcon)
from PySide6.QtWidgets import (QAbstractScrollArea, QComboBox,
                               QDoubleSpinBox, QFrame, QGridLayout, QHBoxLayout,
                               QLabel, QLayout, QPushButton,
                               QScrollArea, QSizePolicy, QSpacerItem, QStackedWidget,
                               QTabWidget, QVBoxLayout, QWidget, QMenuBar, QListWidget, QStatusBar, QListWidgetItem)
from superqt import QEnumComboBox

from CSFM_Parser import NoteCheck, TargetSpawnPrecision


class Ui_MainWindow(object):
    def setupUi(self, MainWindow,filter_dict:dict):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1200, 600)
        MainWindow.setWindowTitle("CSFM Scanner")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 24))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.info_layout = QHBoxLayout()

        self.csfm_file_label = QLabel()
        self.csfm_song_name_label = QLabel()
        self.csfm_difficulty_label = QLabel()

        font = self.csfm_file_label.font()
        font.setBold(True)
        self.csfm_file_label.setFont(font)
        self.csfm_song_name_label.setFont(font)
        self.csfm_difficulty_label.setFont(font)

        self.info_layout.addWidget(self.csfm_file_label)
        self.info_layout.addWidget(self.csfm_song_name_label)
        self.info_layout.addWidget(self.csfm_difficulty_label)


        self.side_config_frame = QFrame()
        self.side_config_frame.setMaximumWidth(400)
        self.side_config_layout = QVBoxLayout(self.side_config_frame)

        self.target_spawn_precision_label = QLabel("Target Spawn Precision")
        self.target_spawn_precision_combobox = QEnumComboBox(enum_class=TargetSpawnPrecision)

        self.filter_check_label = QLabel()
        self.filter_check_label.setText("Check for...")

        self.filter_scrollarea = QScrollArea()
        self.filter_scrollarea.setMinimumWidth(350)
        self.filter_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.filter_scrollarea_contents = QWidget()
        self.filter_scrollarea_contents_layout = QVBoxLayout()
        self.filter_scrollarea_contents.setLayout(self.filter_scrollarea_contents_layout)
        self.group_lists = []

        for category in NoteCheck.categories():
            if not category.startswith("(WIP)"):
                check_group_label = QLabel(category)

                font = check_group_label.font()
                font.setBold(True)
                check_group_label.setFont(font)
                group_listview = QListWidget()
                group_listview.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                group_listview.itemChanged.connect(lambda sub_issue_item : self.update_dict(filter_dict,sub_issue_item))
                self.group_lists.append(group_listview)
                for sub_issue in NoteCheck.of_category(category):
                    item = QListWidgetItem(sub_issue.value)
                    item.enum = sub_issue.name
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)

                    item.setCheckState(Qt.CheckState.Checked)
                    dict_key = sub_issue.name
                    filter_dict[dict_key] = item.checkState().value
                    group_listview.addItem(item)


                row_height = group_listview.sizeHintForRow(0)
                total_height = row_height * group_listview.count() + 2
                group_listview.setMaximumHeight(total_height)
                group_listview.setMinimumWidth(400)



                self.filter_scrollarea_contents_layout.addWidget(check_group_label)
                self.filter_scrollarea_contents_layout.addWidget(group_listview)
        print(f"Filter dict: {filter_dict}")
        self.filter_scrollarea.setWidget(self.filter_scrollarea_contents)

        self.side_config_layout.addWidget(self.target_spawn_precision_label)
        self.side_config_layout.addWidget(self.target_spawn_precision_combobox)
        self.side_config_layout.addWidget(self.filter_check_label)
        self.side_config_layout.addWidget(self.filter_scrollarea)







        self.layout = QVBoxLayout()

        self.button = QPushButton()
        self.button.setText("Load CSFM")

        self.csfm_issues_listview = QListWidget()
        self.csfm_issues_listview.setMinimumWidth(600)

        self.layout.addWidget(self.button)
        self.layout.addLayout(self.info_layout)
        self.layout.addWidget(self.csfm_issues_listview)

        self.main_hbox_layout = QHBoxLayout(self.centralwidget)
        self.main_hbox_layout.addLayout(self.layout)
        self.main_hbox_layout.addWidget(self.side_config_frame)

    def update_dict(self,filter_dict,sub_issue_item):
        sub_issue =  sub_issue_item
        dict_key = sub_issue.enum

        filter_dict[dict_key] = sub_issue_item.checkState().value