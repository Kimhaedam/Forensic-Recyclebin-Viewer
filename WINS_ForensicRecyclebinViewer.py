import fnmatch
import math
import os
import sys
import time
from datetime import datetime, timedelta

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QInputDialog, QApplication
from PyQt5.uic import loadUi

global ALL_FILES, R_FILES, I_FILES, ETC_FILES, PATH_DIR
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class MyWindow:
    def __init__(self):
        self.dlg = loadUi(BASE_DIR + r'\WINS_Ui_ForensicRecyclebinViewer.ui')

        global PATH_DIR
        PATH_DIR, b = QInputDialog.getText(self.dlg, '경로 입력', '분석할 휴지통이 있는 경로를 입력하세요. \n\n\n 휴지통까지의 경로를 입력해야합니다. ex. C:\\$Recycle.bin\\ \n\n 이 프로그램은 사용자가 경로를 제대로 입력했다는 가정 하에 동작합니다. \n ※제대로 된 경로를 설정하지 않아 발생하는 오류는 책임지지 않습니다.※ \n 경로를 잘못 설정했을 경우, 프로그램을 다시 실행해야합니다.')
        self.dlg.secIdList.addItems(os.listdir(PATH_DIR))
        self.dlg.secIdList.setCurrentIndex(-1)
        self.dlg.action_file_list.triggered.connect(self.view_main)
        self.dlg.osType.currentIndexChanged.connect(self.os_version)
        self.dlg.show()

    def view_main(self):
        self.dlg.stackedWidget.setCurrentIndex(0)

    def os_version(self):
        self.dlg.filesListView.clear()
        self.dlg.secIdList.setCurrentIndex(0)
        if self.dlg.osType.currentIndex() != 0:
            self.dlg.conditionSection.setEnabled(True)
            self.dlg.viewerSection.setEnabled(True)
            self.dlg.fileInfoSection.setEnabled(True)
            self.main_function()
            self.dlg.delMDate.setEnabled(True)
            self.dlg.delRouteSize.setEnabled(True)
            self.dlg.delRouteSizeText.setEnabled(True)
            if self.dlg.osType.currentIndex() == 1:
                self.dlg.delRouteSize.setEnabled(False)
                self.dlg.delRouteSizeText.setEnabled(False)
        else:
            self.dlg.conditionSection.setEnabled(False)
            self.dlg.viewerSection.setEnabled(False)
            self.dlg.fileInfoSection.setEnabled(False)
            self.dlg.secIdList.setCurrentIndex(-1)
            self.dlg.filesListView.clear()
            self.set_init()
            self.dlg.capacity.setText(f'{"-": >15}')
            self.dlg.searchBox.clear()

    def main_function(self):
        self.dlg.filesListView.currentRowChanged.connect(self.file_info)
        self.dlg.allFiles.clicked.connect(self.list_filter)
        self.dlg.rFiles.clicked.connect(self.list_filter)
        self.dlg.iFiles.clicked.connect(self.list_filter)
        self.dlg.etcFiles.clicked.connect(self.list_filter)
        self.dlg.secIdList.currentIndexChanged.connect(self.dlg.allFiles.click)
        self.dlg.secIdList.currentIndexChanged.connect(self.total_size)
        self.dlg.searchBox.textChanged.connect(self.searching)
        self.dlg.allFiles.click()

    def all_file_list(self):
        self.dlg.filesListView.clear()
        try:
            sec_id = self.dlg.secIdList.currentText()
            sec_file = os.listdir(PATH_DIR + sec_id)
            self.dlg.filesListView.addItems(sec_file)
            global ALL_FILES
            ALL_FILES = sec_file
            self.sorting()
            self.dlg.searchBox.setEnabled(True)
        except PermissionError:
            self.dlg.filesListView.addItem('엑세스 위반')
            self.dlg.searchBox.setEnabled(False)
        except NotADirectoryError:
            self.dlg.filesListView.addItem('엑세스 위반')
            self.dlg.searchBox.setEnabled(False)
        except FileNotFoundError:
            self.dlg.filesListView.addItem('엑세스 위반')
            self.dlg.searchBox.setEnabled(False)

    def list_filter(self):
        global R_FILES, I_FILES, ETC_FILES
        ETC_FILES = []
        try:
            self.dlg.filesListView.clear()
            sec_id = self.dlg.secIdList.currentText()
            if self.dlg.allFiles.isChecked():
                self.all_file_list()
            elif self.dlg.rFiles.isChecked():
                r_view = fnmatch.filter(os.listdir(PATH_DIR + '/' + sec_id), '$R*')
                self.dlg.filesListView.addItems(r_view)
                R_FILES = r_view
                self.dlg.searchBox.setEnabled(True)
            elif self.dlg.iFiles.isChecked():
                i_view = fnmatch.filter(os.listdir(PATH_DIR + '/' + sec_id), '$I*')
                self.dlg.filesListView.addItems(i_view)
                I_FILES = i_view
                self.dlg.searchBox.setEnabled(True)
            elif self.dlg.etcFiles.isChecked():
                for file_name in os.listdir(PATH_DIR + '/' + sec_id):
                    if file_name[:2] != '$R' and file_name[:2] != '$I':
                        self.dlg.filesListView.addItem(file_name)
                        ETC_FILES.append(file_name)
                        self.dlg.searchBox.setEnabled(True)
            self.counting()
        except PermissionError:
            self.dlg.filesListView.addItem('엑세스 위반')
            self.dlg.searchBox.setEnabled(False)
        except NotADirectoryError:
            self.dlg.filesListView.addItem('엑세스 위반')
            self.dlg.searchBox.setEnabled(False)
        except FileNotFoundError:
            self.dlg.filesListView.addItem('엑세스 위반')
            self.dlg.searchBox.setEnabled(False)

    def sorting(self):
        for i in range((self.dlg.filesListView.count())):
            i_format = self.dlg.filesListView.item(i).text()[:2]
            random_str = self.dlg.filesListView.item(i).text()[2:]
            if i_format == '$I' and len(
                    fnmatch.filter(os.listdir(PATH_DIR + self.dlg.secIdList.currentText()),
                                   '*' + random_str)) == 1:
                self.dlg.filesListView.item(i).setBackground(QColor(214, 230, 240))
            else:
                self.dlg.filesListView.item(i).setBackground(QColor(255, 255, 255))

    def counting(self):
        cnt = self.dlg.filesListView.count()
        if cnt == 1 and self.dlg.filesListView.item(0).text() == '엑세스 위반':
            cnt = '-'
        self.dlg.amount.setText(f'{cnt: >10}개')

    def file_info(self):
        if self.dlg.filesListView.currentRow() != -1 and self.dlg.filesListView.item(0).text() != '엑세스 위반':
            file = self.dlg.filesListView.currentItem()
            file_str = file.text()
            sec_id = self.dlg.secIdList.currentText()

            if self.dlg.allFiles.isChecked():
                self.sorting()

            if "$I" + file_str[2:] in os.listdir(PATH_DIR + sec_id):
                i_file_path = PATH_DIR + sec_id + "/" + "$I" + file_str[2:]

                with open(i_file_path, mode='rb') as file:
                    binary_data = file.read()
                    binary_data_string = [f"{x:0>2x}" for x in binary_data[:28]]

                delete_file_size = ''
                for i in range(15, 7, -1):
                    delete_file_size = delete_file_size + binary_data_string[i]
                delete_file_size = int(delete_file_size, 16)

                delete_time = ''
                for i in range(23, 15, -1):
                    delete_time = delete_time + binary_data_string[i]
                us = int(delete_time, 16) / 10.
                delete_time = str(datetime(1601, 1, 1) + timedelta(microseconds=us, hours=9))

                if self.dlg.osType.currentIndex() == 2:
                    delete_route_size = ''
                    for i in range(27, 23, -1):
                        delete_route_size = delete_route_size + binary_data_string[i]
                    delete_route_size = str(int(delete_route_size, 16))

                    delete_route = binary_data[28:].decode(encoding='utf-16', errors='replace')[:-1]
                else:
                    delete_route_size = '-'
                    delete_route = binary_data[24:].decode(encoding='utf-16', errors='replace')[:-1]

                self.dlg.delRoute.setText(delete_route)
                self.dlg.delFileSize.setText(f'{delete_file_size}  ({self.convert_size(delete_file_size)})')
                self.dlg.delDate.setText(delete_time)
                self.dlg.delRouteSize.setText(delete_route_size)
            else:
                self.set_init()

            if "$R" + file_str[2:] in os.listdir(PATH_DIR + sec_id) or file_str[:2] != '$I':
                path = PATH_DIR + sec_id + "/" + "$R" + file_str[2:]
                if file_str[:2] != '$R' and file_str[:2] != '$I':
                    path = PATH_DIR + sec_id + '/' + file_str

                created_time = time.localtime(os.path.getctime(path))
                modified_time = time.localtime(os.path.getmtime(path))
                self.dlg.delCDate.setText(str(time.strftime("%Y-%m-%d %H:%M:%S %z", created_time)))
                self.dlg.delMDate.setText(str(time.strftime("%Y-%m-%d %H:%M:%S %z", modified_time)))
            else:
                self.dlg.delCDate.setText('-')
                self.dlg.delMDate.setText('-')

            real_file_size = os.path.getsize(PATH_DIR + sec_id + '/' + file_str)
            self.dlg.realFileSize.setText(f'{real_file_size}  ({self.convert_size(real_file_size)})')

            if len(self.dlg.filesListView.findItems(file_str[2:], Qt.MatchContains)) == 2:
                same_ran_str = self.dlg.filesListView.findItems(file_str[2:], Qt.MatchContains)
                same_ran_str[0].setBackground(QColor(163, 204, 163))
                same_ran_str[1].setBackground(QColor(163, 204, 163))

        else:
            self.set_init()

    def set_init(self):
        self.dlg.realFileSize.setText("-")
        self.dlg.delFileSize.setText("-")
        self.dlg.delDate.setText("-")
        self.dlg.delCDate.setText("-")
        self.dlg.delMDate.setText("-")
        self.dlg.delRouteSize.setText("-")
        self.dlg.delRoute.clear()

    @staticmethod
    def convert_size(size_bytes):
        if size_bytes == 0:
            return "0bytes"
        size_name = ("bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f'{s} {size_name[i]}'

    def total_size(self):
        try:
            the_size = 0
            sec_id = self.dlg.secIdList.currentText()
            for file_name in os.listdir(PATH_DIR + '/' + sec_id):
                the_size = the_size + os.path.getsize(PATH_DIR + sec_id + '/' + file_name)

            self.dlg.capacity.setText(f'{self.convert_size(the_size): >15}')
        except PermissionError:
            self.dlg.capacity.setText(f'{"-": >15}')
        except NotADirectoryError:
            self.dlg.capacity.setText(f'{"-": >15}')
        except FileNotFoundError:
            self.dlg.capacity.setText(f'{"-": >15}')

    def searching(self):
        key_word = self.dlg.searchBox.text()
        result = []
        if key_word == "":
            self.list_filter()
        else:
            self.dlg.filesListView.clear()
            if self.dlg.allFiles.isChecked():
                result = fnmatch.filter(ALL_FILES, '*' + key_word + '*')
            elif self.dlg.rFiles.isChecked():
                result = fnmatch.filter(R_FILES, '*' + key_word + '*')
            elif self.dlg.iFiles.isChecked():
                result = fnmatch.filter(I_FILES, '*' + key_word + '*')
            elif self.dlg.etcFiles.isChecked():
                result = fnmatch.filter(ETC_FILES, '*' + key_word + '*')
            self.dlg.filesListView.addItems(result)
        self.counting()


app = QApplication(sys.argv)
myWin = MyWindow()
app.exec()
