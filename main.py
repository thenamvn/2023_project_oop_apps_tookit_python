import os
import sys
import subprocess
from PyQt5 import QtCore, QtGui, QtWidgets
from note import GhiChuGUI
import sys
from PyQt5.QtGui import QIcon, QPixmap, QImage
import win32ui
import win32gui
import win32com.client
from PyQt5.QtCore import Qt


class AppsMenu(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)

        # Set window properties
        self.title = 'Apps Menu'
        self.width = 826
        self.height = 517

        # lấy vị trí folder menu
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.apps_folder = os.path.join(current_dir, "menu")
        icon_path = os.path.join(current_dir, "resources/icon.png")
        self.icon = QtGui.QIcon(icon_path)
        self.setWindowIcon(self.icon)
        # tính vị trí giữa màn hình
        desktop = QtWidgets.QApplication.desktop()
        x = (desktop.width() - self.width) / 2
        y = (desktop.height() - self.height) / 2
        self.setGeometry(x, y, self.width, self.height)
        self.setFixedSize(self.width, self.height)


        # Create app buttons
        self.app_buttons = []
        self.create_app_buttons()

        # khung tìm kiếm
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setFixedWidth(200)
        self.search_input.setPlaceholderText("Tìm kiếm...")
        self.search_input.textChanged.connect(self.filter_apps)

        # scroll
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QGridLayout(scroll_widget)
        scroll_layout.setHorizontalSpacing(25)
        scroll_layout.setVerticalSpacing(25)
        for i, button in enumerate(self.app_buttons):
            row, col = divmod(i, 8)
            scroll_layout.addWidget(button, row, col)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)

        # tạo main layout,widgets
        main_layout = QtWidgets.QGridLayout(self)
        main_layout.addWidget(self.search_input, 0, 0, 1, 1)
        main_layout.addWidget(scroll, 1, 0, 1, 1)

        # Thêm menu bar và menu "Optimizer"
        menu_bar = QtWidgets.QMenuBar()
        menu = menu_bar.addMenu("Menu")
        run_optimizer_action = QtWidgets.QAction("Ram Clean", self)
        run_optimizer_action.triggered.connect(self.run_optimizer)
        menu.addAction(run_optimizer_action)

        #thêm item "ghi chú"

        note_program = QtWidgets.QAction("Ghi Chú", self)
        note_program.triggered.connect(self.open_ghi_chu)
        menu.addAction(note_program)


        right_button_layout = QtWidgets.QHBoxLayout()
        right_button_layout.setContentsMargins(0, 0, 10, 0)  # Right margin of 5 pixels
        spacer = QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        right_button_layout.addItem(spacer)

        label1 = QtWidgets.QLabel("Apps Menu")
        right_button_layout.addWidget(label1)
        right_button_layout.addSpacing(310)

        # Create the second button
        button2 = QtWidgets.QPushButton("")
        button2.setStyleSheet("background-color: transparent;")
        button2.setIcon(QtGui.QIcon(os.path.join(current_dir, "resources/minimize.png")))
        button2.clicked.connect(self.minimize_program)
        right_button_layout.addWidget(button2)
 
        right_button_layout.addSpacing(2)
        # Create the third button
        button3 = QtWidgets.QPushButton("")
        button3.setStyleSheet("background-color: transparent;")
        button3.setIcon(QtGui.QIcon(os.path.join(current_dir, "resources/exit.png")))
        button3.clicked.connect(self.exit_program)
        right_button_layout.addWidget(button3)
        menu_bar.setLayout(right_button_layout)
        self.layout().setMenuBar(menu_bar)

        self.setWindowTitle(self.title)
        self.setGeometry(x, y, self.width, self.height)
        self.setStyleSheet(stylesheet)
        self.show()
        app.setStyle("Fusion")
        app.setPalette(QtGui.QPalette(QtGui.QColor("#2b2b2b")))

    def exit_program(self):
        self.close()

    def minimize_program(self):
        self.showMinimized()

    def create_app_buttons(self):
        app_names = os.listdir(self.apps_folder)
        for app_name in app_names:
            if app_name.endswith(".lnk"):
                button = QtWidgets.QPushButton()
                button.setFixedSize(75, 75)
                button.setToolTip(app_name[:-4])   #set tooltip cho button
               # button.setText(app_name[:-4])
                button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                button.setIcon(self.getIcon(self.get_target_filepath(os.path.join(self.apps_folder, app_name))))
                button.setIconSize(button.rect().size())
                button.clicked.connect(self.run_app)
                self.app_buttons.append(button)


    def get_target_filepath(self, shortcut_path):
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        target_filepath = shortcut.Targetpath
        return target_filepath

    def run_app(self):
     sender = self.sender()
     app_name = sender.toolTip()
     app_path = os.path.join(self.apps_folder, app_name + ".lnk")
     os.startfile(app_path)
     self.showMinimized()
     self.search_input.clear()

    def run_optimizer(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.ram_cleaner_runtime = os.path.join(current_dir, "x64")
        self.ram_cleaner = os.path.join(current_dir, "memory.dll")
        subprocess.call([self.ram_cleaner_runtime,self.ram_cleaner])

    def open_ghi_chu(self):
        self.ghi_chu_gui = GhiChuGUI()
        self.ghi_chu_gui.show()

    def getIcon(self, exe_path):
        # Get the icon of the exe file
        ico_x = 32
        large, _ = win32gui.ExtractIconEx(exe_path,0)

        # Convert the icon to QIcon
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_x)
        hdc = hdc.CreateCompatibleDC()
        hdc.SelectObject(hbmp)
        hdc.DrawIcon((0, 0), large[0])

        # Create QPixmap from hdc
        bmpinfo = hbmp.GetInfo()
        bmpstr = hbmp.GetBitmapBits(True)
        image = QImage(bmpstr, bmpinfo['bmWidth'], bmpinfo['bmHeight'], QImage.Format_ARGB32)
        pixmap = QPixmap.fromImage(image)

        # Create QIcon from QPixmap
        return QIcon(pixmap)
    def filter_apps(self):
     search_term = self.search_input.text()
     if search_term == "":
         for button in self.app_buttons:
             button.show()
     else:
         for i, button in enumerate(self.app_buttons):
             if search_term.lower() in button.toolTip().lower():
                 button.show()
             else:
                 button.hide()

stylesheet = """
QWidget {
    background-color: #2b2b2b;
    color: #f2f2f2;
}

QLabel {
    color: #f2f2f2;
    font-size: 18px;
}

QListWidget {
    background-color: #3a3a3a;
    border: 1px solid #555555;
    border-radius: 5px;
    padding: 5px;
    font-size: 16px;
    color: #f2f2f2;
}

QLineEdit {
    font-size: 16px;
    border: 1px solid #555555;
    border-radius: 5px;
    padding: 5px;
    color: #f2f2f2;
    background-color: #555555;
}

QPushButton {
    border: none;
    color: #f2f2f2;
    background-color: #555555;
    border-radius:10px;
}

QPushButton:hover {
    background-color: #007acc;
}

QMenuBar {
    background-color: #2b2b2b;
    color: #f2f2f2;
}

QMenuBar QMenu {
    background-color: #2b2b2b;
    color: #f2f2f2;
}

QMenuBar QMenu::item {
    padding: 10px 20px;
}

QMenuBar QMenu::item:selected {
    background-color: #555555;
}

QMenuBar QAction {
    color: #f2f2f2;
    font-size: 18px;
}
"""

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = AppsMenu()
    second_gui = GhiChuGUI()
    second_gui.hide()
    sys.exit(app.exec_())
