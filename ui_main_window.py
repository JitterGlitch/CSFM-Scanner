from PySide6.QtCore import (QCoreApplication, QLocale,
                            QMetaObject, QRect,
                            QSize, Qt)
from PySide6.QtGui import (QFont, QIcon)
from PySide6.QtWidgets import (QAbstractScrollArea, QComboBox,
                               QDoubleSpinBox, QFrame, QGridLayout, QHBoxLayout,
                               QLabel, QLayout, QPushButton,
                               QScrollArea, QSizePolicy, QSpacerItem, QStackedWidget,
                               QTabWidget, QVBoxLayout, QWidget, QMenuBar, QListWidget, QStatusBar, QListWidgetItem)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
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
        self.side_config_frame.setMaximumWidth(200)
        self.side_config_layout = QVBoxLayout(self.side_config_frame)

        self.target_spawn_precision_label = QLabel("Target Spawn Precision")
        self.target_spawn_precision_combobox = QComboBox()
        self.target_spawn_precision_combobox.addItem("Normal")
        self.target_spawn_precision_combobox.addItem("Strict")

        self.filter_check_listview = QListWidget()
        for i in range(20):
            item = QListWidgetItem(f"Option {i + 1}")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.filter_check_listview.addItem(item)

        self.side_config_layout.addWidget(self.target_spawn_precision_label)
        self.side_config_layout.addWidget(self.target_spawn_precision_combobox)
        self.side_config_layout.addWidget(self.filter_check_listview)






        self.layout = QVBoxLayout()

        self.button = QPushButton()
        self.button.setText("Load CSFM")

        self.csfm_issues_listview = QListWidget()


        self.layout.addWidget(self.button)
        self.layout.addLayout(self.info_layout)
        self.layout.addWidget(self.csfm_issues_listview)

        self.main_hbox_layout = QHBoxLayout(self.centralwidget)
        self.main_hbox_layout.addLayout(self.layout)
        self.main_hbox_layout.addWidget(self.side_config_frame)