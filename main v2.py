import os
import sys
import subprocess
from PyQt5 import QtCore, QtGui, QtWidgets
from note import GhiChuGUI
import shutil
import win32com.client
import win32gui
import win32gui
import win32con
import win32api
import win32ui

class AppsMenu(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)

        # Set window properties
        self.title = 'Apps Menu'
        self.width = 826
        self.height = 517

        # Get the path of the menu folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.apps_folder = os.path.join(current_dir, "menu")
        icon_path = os.path.join(current_dir, "resources/icon.png")
        self.icon = QtGui.QIcon(icon_path)
        self.setWindowIcon(self.icon)
        
        # Calculate the center position of the screen
        desktop = QtWidgets.QApplication.desktop()
        x = (desktop.width() - self.width) / 2
        y = (desktop.height() - self.height) / 2
        self.setGeometry(x, y, self.width, self.height)
        self.setFixedSize(self.width, self.height)

        # Create app buttons
        self.app_buttons = []
        self.create_app_buttons()

        # Create the search input
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setFixedWidth(200)
        self.search_input.setPlaceholderText("Tìm kiếm...")
        self.search_input.textChanged.connect(self.filter_apps)

        # Create the scroll area
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

        # Create the main layout and add widgets
        main_layout = QtWidgets.QGridLayout(self)
        main_layout.addWidget(self.search_input, 0, 0, 1, 1)
        main_layout.addWidget(scroll, 1, 0, 1, 1)

        # Add menu bar and "Optimizer" menu
        menu_bar = QtWidgets.QMenuBar()
        menu = menu_bar.addMenu("Menu")
        run_optimizer_action = QtWidgets.QAction("Ram Clean", self)
        run_optimizer_action.triggered.connect(self.run_optimizer)
        menu.addAction(run_optimizer_action)

        # Add "Ghi Chú" item
        note_program = QtWidgets.QAction("Ghi Chú", self)
        note_program.triggered.connect(self.open_ghi_chu)
        menu.addAction(note_program)

        # Add "Add App" and "Xóa app khỏi menu" items
        add_app_action = QtWidgets.QAction("Add App", self)
        add_app_action.triggered.connect(self.add_app)
        menu.addAction(add_app_action)
        rm_app_action = QtWidgets.QAction("Xóa app khỏi menu", self)
        rm_app_action.triggered.connect(self.rm_menu)
        menu.addAction(rm_app_action)

        right_button_layout = QtWidgets.QHBoxLayout()
        right_button_layout.setContentsMargins(0, 0, 10, 0)  # Right margin of 10 pixels

        spacer = QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        right_button_layout.addItem(spacer)

        label1 = QtWidgets.QLabel("Apps Menu")
        right_button_layout.addWidget(label1)
        right_button_layout.addSpacing(310)

        # Create the minimize button
        button2 = QtWidgets.QPushButton("")
        button2.setStyleSheet("background-color: transparent;")
        button2.setIcon(QtGui.QIcon(os.path.join(current_dir, "resources/minimize.png")))
        button2.clicked.connect(self.minimize_program)
        right_button_layout.addWidget(button2)

        right_button_layout.addSpacing(2)

        # Create the exit button
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
                button.setToolTip(app_name[:-4])   # Set tooltip for the button
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
        subprocess.call([self.ram_cleaner_runtime, self.ram_cleaner])

    def open_ghi_chu(self):
        self.ghi_chu_gui = GhiChuGUI()
        self.ghi_chu_gui.show()

    def getIcon(self, exe_path):
        try:
            # Get the icon of the exe file
            ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
            large, _ = win32gui.ExtractIconEx(exe_path, 0)

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
            image = QtGui.QImage(bmpstr, bmpinfo['bmWidth'], bmpinfo['bmHeight'], QtGui.QImage.Format_ARGB32)
            pixmap = QtGui.QPixmap.fromImage(image)

            # Create QIcon from QPixmap
            return QtGui.QIcon(pixmap)
        except Exception as e:
            error_message = f"Error getting icon for shortcut: {os.path.basename(exe_path)}"
            print(error_message)
            return QtGui.QIcon()

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

    def rm_menu(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Remove App")
        dialog.setModal(True)
        dialog.setFixedSize(400, 300)

        # Create QListWidget to display app shortcuts
        list_widget = QtWidgets.QListWidget(dialog)
        list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        list_widget.itemSelectionChanged.connect(self.update_selected_items)

        # Add app shortcuts to the list widget
        app_names = os.listdir(self.apps_folder)
        for app_name in app_names:
            if app_name.endswith(".lnk"):
                item = QtWidgets.QListWidgetItem(app_name[:-4])
                list_widget.addItem(item)

        # Create buttons
        confirm_button = QtWidgets.QPushButton("Confirm", dialog)
        confirm_button.clicked.connect(dialog.accept)
        cancel_button = QtWidgets.QPushButton("Cancel", dialog)
        cancel_button.clicked.connect(dialog.reject)

        # Create layout
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.addWidget(list_widget)
        layout.addStretch(1)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_items = list_widget.selectedItems()
            for item in selected_items:
                app_name = item.text()
                app_path = os.path.join(self.apps_folder, app_name + ".lnk")
                if os.path.exists(app_path):
                    os.remove(app_path)
                self.remove_app_button(app_name)

    def remove_app_button(self, app_name):
        for button in self.app_buttons:
            if button.toolTip() == app_name:
                self.app_buttons.remove(button)
                button.deleteLater()

    def update_selected_items(self):
        selected_items = self.sender().selectedItems()
        self.selected_items = [item.text() for item in selected_items]

    def add_app(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        dialog.setNameFilter("Applications (*.exe *.lnk)")
        if dialog.exec_():
            file_paths = dialog.selectedFiles()
            for file_path in file_paths:
                _, ext = os.path.splitext(file_path)
                app_name = os.path.basename(file_path).split('.')[0]
                if ext == '.exe':
                    # Create a shortcut for the executable file
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut_path = os.path.join(self.apps_folder, app_name + ".lnk")
                    shortcut = shell.CreateShortCut(shortcut_path)
                    shortcut.Targetpath = file_path
                    shortcut.WorkingDirectory = os.path.dirname(file_path)
                    shortcut.save()
                elif ext == '.lnk':
                    # Copy the existing shortcut file to the menu folder
                    new_path = os.path.join(self.apps_folder, app_name + ".lnk")
                    shutil.copy(file_path, new_path)

            # Restart the application
            python_path = sys.executable
            subprocess.Popen([python_path] + sys.argv)
            QtWidgets.QApplication.quit()

        # Hide the search input when adding an app
        self.search_input.clear()
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
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    apps_menu = AppsMenu()
    sys.exit(app.exec_())
