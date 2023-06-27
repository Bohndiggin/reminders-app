import sys
import csv
import json
import typing
import smtplib
from dotenv import load_dotenv
import os
from datetime import date, time, datetime

from PyQt6 import QtCore

from utils import *

from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QMainWindow, QDialog, QWidget
)
from PyQt6.uic import loadUi
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QTextCursor

from ui_mw import Ui_MainWindow
import ui_edit_dt, ui_new_rmd

class EditDateTimeDialog(QDialog, ui_edit_dt.Ui_Dialog):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setupUi(self)

    def get_data(self):
        selected_date = self.calendarWidget.selectedDate().toPyDate()
        selected_time = self.timeEdit.time().toPyTime()
        selected_datetime = datetime.combine(selected_date, selected_time)
        return selected_datetime

class NewReminderDialog(QDialog, ui_new_rmd.Ui_Dialog):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setupUi(self)

    def get_data(self):
        reminder_name = self.lineEdit.text()
        reminder_time = self.timeEdit.time().toPyTime()
        reminder_freq = self.comboBox.currentIndex()
        reminder_fuzz = self.spinBox.value()
        data = {
            'name': reminder_name,
            'time': reminder_time,
            'freq': reminder_freq,
            'fuzz': reminder_fuzz
        }
        return data

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        self.actionNew_Reminder.triggered.connect(self.new_reminder_dialog)
        self.actionNew_Set.triggered.connect(self.placeholder_command)
        self.actionLoad_Set.triggered.connect(self.placeholder_command)
        self.actionSave.triggered.connect(self.placeholder_command)
        self.actionSave_as.triggered.connect(self.placeholder_command)

        self.pushButtonEditDueDate.clicked.connect(self.edit_date_time_dialog)
        self.pushButtonSaveChanges.clicked.connect(self.placeholder_command)
        self.pushButtonCancelChanges.clicked.connect(self.placeholder_command)
        self.pushButtonAPI.clicked.connect(self.placeholder_command)
        self.pushButtonTest.clicked.connect(self.placeholder_command)

    def edit_date_time_dialog(self):
        self.dialog = EditDateTimeDialog(self)
        self.dialog.setModal(True)
        if self.dialog.exec() == QDialog.DialogCode.Accepted:
            selected_date_time = self.dialog.get_data()
        # Change the datetime of the task selected here
        return selected_date_time

    def new_reminder_dialog(self):
        self.dialog = NewReminderDialog(self)
        self.dialog.setModal(True)
        if self.dialog.exec() == QDialog.DialogCode.Accepted:
            new_reminder_data = self.dialog.get_data()
        print(new_reminder_data['fuzz'])

    def placeholder_command(self):
        pass

if __name__ == '__main__':
    load_dotenv()
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    # win.test()
    sys.exit(app.exec())