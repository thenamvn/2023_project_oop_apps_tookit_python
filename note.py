import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QListWidget, QDateTimeEdit, QPushButton, QMessageBox,QLineEdit
from PyQt5.QtCore import QDateTime,QTimer
from PyQt5 import QtGui
import os
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import pygame
import threading

class GhiChuGUI(QWidget):
    def __init__(self):
        super().__init__()
        pygame.mixer.init()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.displayed_events = set()  # Danh sách các sự kiện đã hiển thị thông báo
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(self.current_dir, "resources/icon.png")
        self.icon = QtGui.QIcon(icon_path)
        self.setWindowIcon(self.icon)

        self.setWindowTitle("Ghi Chú")
        self.layout = QVBoxLayout()

        self.label = QLabel("Lịch sự kiện:")
        self.label.setStyleSheet(style_sheet)
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(style_sheet)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.list_widget)

        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setStyleSheet(style_sheet)
        self.datetime_edit.setDisplayFormat("dd/MM/yyyy hh:mm")  # Định dạng hiển thị ngày tháng và thời gian
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        self.ghi_chu_edit = QLineEdit()
        self.ghi_chu_edit.setStyleSheet(style_sheet)


        self.label_ngay_time = QLabel("Ngày và thời gian:")
        self.label_ngay_time.setStyleSheet(style_sheet)

        self.layout.addWidget(self.label_ngay_time)
        self.layout.addWidget(self.datetime_edit)

        self.label_ghi_chu = QLabel("Sự kiện:")
        self.label_ghi_chu.setStyleSheet(style_sheet)
        self.layout.addWidget(self.label_ghi_chu)
        self.layout.addWidget(self.ghi_chu_edit)

        self.save_button = QPushButton("Lưu")
        self.save_button.setStyleSheet(style_sheet);
        self.save_button.clicked.connect(self.luu_ghi_chu)

        self.delete_button = QPushButton("Xóa")
        self.delete_button.setStyleSheet(style_sheet);
        self.delete_button.clicked.connect(self.xoa_ghi_chu)

        self.close_button = QPushButton("Đóng")
        self.close_button.setStyleSheet(style_sheet);
        self.close_button.clicked.connect(self.close)

        self.layout.addWidget(self.save_button)
        self.layout.addWidget(self.delete_button)
        self.layout.addWidget(self.close_button)

        self.setLayout(self.layout)

        self.load_ghi_chu()
        self.timer = QTimer()
        self.timer.timeout.connect(self.kiem_tra_lich_ghi_chu)
        self.timer.start(1000)

    def load_ghi_chu(self):
        try:
            with open("ghi_chu.txt", "r",encoding="utf-8") as file:
                for line in file:
                 data = line.strip().split("\t")
                 if len(data) == 2:
                   ngay_gio, ghi_chu = data
                   self.list_widget.addItem(f"{ngay_gio}: {ghi_chu}")

        except FileNotFoundError:
            print("File ghi_chú.txt không tồn tại!")

    def luu_ghi_chu(self):
        ngay_gio = self.datetime_edit.dateTime().toString("dd/MM/yyyy hh:mm")  # Lấy giá trị ngày tháng và thời gian
        ghi_chu = self.ghi_chu_edit.text()

        if ngay_gio and ghi_chu:
            with open("ghi_chu.txt", "a",encoding="utf-8") as file:
                file.write(f"{ngay_gio}\t{ghi_chu}\n")

            self.list_widget.addItem(f"{ngay_gio}: {ghi_chu}")
            self.datetime_edit.setDateTime(QDateTime.currentDateTime())  # Đặt giá trị mặc định cho ngày tháng và thời gian
            self.ghi_chu_edit.clear()

    def xoa_ghi_chu(self):
        selected_item = self.list_widget.currentItem()
        if selected_item:
            ngay_gio, ghi_chu = selected_item.text().split(": ")
            confirmation = QMessageBox.question(
                self, "Xác nhận", "Bạn có chắc chắn muốn xóa ghi chú này?", QMessageBox.Yes | QMessageBox.No
            )
            if confirmation == QMessageBox.Yes:
                self.list_widget.takeItem(self.list_widget.row(selected_item))
                self.xoa_ghi_chu_trong_file(ngay_gio, ghi_chu)
    
    def xoa_ghi_chu_trong_file(self,ngay_gio, ghi_chu):
     with open("ghi_chu.txt", "r", encoding="utf-8") as file:
         lines = file.readlines()

     new_lines = []
     for line in lines:
         data = line.strip().split("\t")
         if len(data) == 2 and data[0] != ngay_gio and data[1] != ghi_chu:
             new_lines.append(line)

     with open("ghi_chu.txt", "w", encoding="utf-8") as file:
         file.writelines(new_lines)

    def kiem_tra_lich_ghi_chu(self):
        current_datetime = QDateTime.currentDateTime().toString("dd/MM/yyyy hh:mm")
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            if item is not None:
              item_text = item.text()
            ngay_gio, ghi_chu = item_text.split(": ")

            if ngay_gio <= current_datetime and item_text not in self.displayed_events:
                message_box = QMessageBox()
                message_box.setWindowIcon(self.icon)
                message_box.setIcon(QMessageBox.Information)
                message_box.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)   #set on top khi thông báo (tránh đang chơi game fullscreen ko thấy thông báo)
                message_box.setWindowTitle("Thông báo")
                message_box.setStyleSheet(style_sheet)
                message_box.setText(ngay_gio)
                message_box.setInformativeText(ghi_chu)
                self.displayed_events.add(item_text)        #thêm sự kiện vô danh sách đã hiển thị tránh bị lặp lại thông báo
                message_box.setStandardButtons(QMessageBox.Ok)
                sound_thread = threading.Thread(target=self.play_sound)
                sound_thread.start()
                result = message_box.exec_()
                if result == QMessageBox.Ok:
                    self.xoa_ghi_chu_trong_file(ngay_gio, ghi_chu)
                    self.list_widget.takeItem(index)
                    self.stop_sound()


    def play_sound(self):
        self.alarm_sound= os.path.join(self.current_dir, "resources/alarm.mp3")
        pygame.mixer.music.load(self.alarm_sound)
        pygame.mixer.music.play(-1)

    def stop_sound(self):
        pygame.mixer.music.stop()
style_sheet = """
QWidget {
    background-color: #2b2b2b;
}

QLabel {
    color: #f2f2f2;
    font-size: 18px;
}

QListWidget {
    background-color: #1e1e1e;
    border: 1px solid #555555;
    border-radius: 5px;
    padding: 5px;
    font-size: 16px;
    color: #f2f2f2;
}

QDateTimeEdit {
    font-size: 16px;
    border: 1px solid #555555;
    border-radius: 5px;
    padding: 5px;
    color: #f2f2f2;
}

QLineEdit {
    font-size: 16px;
    border: 1px solid #555555;
    border-radius: 5px;
    padding: 5px;
    color: #f2f2f2;
}

QPushButton {
    background-color: #007bff;
    color: #fff;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    font-size: 18px;
}

QPushButton:hover {
    background-color: #0056b3;
}

QMessageBox {
    background-color: #2b2b2b;
    border: 1px solid #555555;
    border-radius: 5px;
}

QMessageBox QLabel {
    color: #f2f2f2;
    font-size: 20px;
}

QMessageBox QPushButton {
    background-color: #007bff;
    color: #fff;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    font-size: 18px;
}

QMessageBox QPushButton:hover {
    background-color: #0056b3;
}

"""



if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = GhiChuGUI()
    gui.show()
    sys.exit(app.exec_())
    