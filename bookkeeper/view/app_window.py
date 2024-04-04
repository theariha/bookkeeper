import sys, datetime
from PySide6 import QtWidgets, QtCore

from PySide6.QtCore import QAbstractTableModel, Qt


def check_float(text: str) -> float | None:
    try:
        return float(text)
    except ValueError:
        return None


class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole or role == QtCore.Qt.EditRole:
                value = self._data[index.row()][index.column()]
                return str(value)

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            if check_float(value) is not None:
                self._data[index.row()][index.column()] = value
                return True
        return False

    def flags(self, index):
        return (
            QtCore.Qt.ItemIsSelectable
            | QtCore.Qt.ItemIsEnabled
            | QtCore.Qt.ItemIsEditable
        )


class CategoryWindow(QtWidgets.QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def __init__(self, parent, categoryes: list):
        super().__init__()
        self.par = parent
        self.categoryes = categoryes
        self.correct_category()

    def correct_category(self):
        delete_button = QtWidgets.QPushButton("Удалить категорию")
        plus_button = QtWidgets.QPushButton("Добавить категорию")
        self.success_del_label = QtWidgets.QLabel(" ")
        self.success_add_label = QtWidgets.QLabel(" ")
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(delete_button, 0, 1)
        self.layout.addWidget(self.category_combo_edit(), 0, 0)
        self.layout.addWidget(self.success_del_label, 1, 0)
        self.layout.addWidget(plus_button, 2, 1)
        self.layout.addWidget(self.category_input(), 2, 0)
        self.layout.addWidget(self.success_add_label, 3, 0)
        self.setLayout(self.layout)

        delete_button.clicked.connect(self.on_delete_button_click)
        plus_button.clicked.connect(self.on_plus_button_click)

        # self.setWindowTitle("Редактирование категорий")
        self.setGeometry(300, 100, 600, 200)

    def on_delete_button_click(self):
        text = self.combo_edit.currentText()
        self.combo_edit.removeItem(self.combo_edit.currentIndex())
        count = self.combo_edit.count()
        categoryes = [self.combo_edit.itemText(i) for i in range(count)]
        self.par.delete_category(categoryes=categoryes)
        self.success_del_label.setText(f'категория "{text}" удалена')
        self.layout.addWidget(self.success_del_label, 1, 0, 1, -1)

    def on_plus_button_click(self):
        text = self.category_input_field.text()
        count = self.combo_edit.count()
        categoryes = [self.combo_edit.itemText(i) for i in range(count)]
        if text not in categoryes:
            self.combo_edit.addItem(text)
            self.par.add_category(str(text))
            self.success_add_label.setText(f'категория "{text}" добавлена')
            self.layout.addWidget(self.success_add_label, 3, 0, 1, -1)
        else:
            self.success_add_label.setText(f'категория "{text}" уже существует')
            self.layout.addWidget(self.success_add_label, 3, 0, 1, -1)

    def category_combo_edit(self):
        self.combo_edit = QtWidgets.QComboBox()
        for i in self.categoryes:
            self.combo_edit.addItem(f"{i}")
        return self.combo_edit

    def category_input(self):
        self.category_input_field = QtWidgets.QLineEdit("Введите новую категорию")
        return self.category_input_field


class BudgetWindow(QtWidgets.QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def __init__(self, parent):
        super().__init__()
        self.par = parent
        self.correct_budget()

    def correct_budget(self):
        renew_day_button = QtWidgets.QPushButton("Обновить бюджет на день")
        renew_week_button = QtWidgets.QPushButton("Обновить бюджет на неделю")
        renew_month_button = QtWidgets.QPushButton("Обновить бюджет на месяц")
        self.success_day_label = QtWidgets.QLabel(" ")
        self.success_week_label = QtWidgets.QLabel(" ")
        self.success_month_label = QtWidgets.QLabel(" ")

        self.day_label = QtWidgets.QLabel("Бюджет на день")
        self.week_label = QtWidgets.QLabel("Бюджет на неделю")

        self.month_label = QtWidgets.QLabel("Бюджет на месяц")

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(renew_day_button, 0, 2)
        self.layout.addWidget(renew_week_button, 2, 2)
        self.layout.addWidget(renew_month_button, 4, 2)
        self.layout.addWidget(self.day_label, 0, 0)
        self.layout.addWidget(self.success_day_label, 1, 0)
        self.layout.addWidget(self.week_label, 2, 0)
        self.layout.addWidget(self.success_week_label, 3, 0)
        self.layout.addWidget(self.month_label, 4, 0)
        self.layout.addWidget(self.success_month_label, 5, 0)
        self.layout.addWidget(self.budget_day_input(), 0, 1)
        self.layout.addWidget(self.budget_week_input(), 2, 1)
        self.layout.addWidget(self.budget_month_input(), 4, 1)

        self.setLayout(self.layout)

        renew_day_button.clicked.connect(self.on_renew_day_button_click)
        renew_week_button.clicked.connect(self.on_renew_week_button_click)
        renew_month_button.clicked.connect(self.on_renew_month_button_click)

        # self.setWindowTitle("Редактирование категорий")
        self.setGeometry(300, 100, 500, 200)

    def on_renew_day_button_click(self):
        text_day = self.budget_day_input_field
        if (
            text_day.text() is not None
            and check_float(str(text_day.text())) is not None
        ):
            self.par.control_table.setItem(
                0, 1, QtWidgets.QTableWidgetItem(str(text_day.text()))
            )
            self.success_day_label.setText(f"Бюджет на день обновлен")
            self.layout.addWidget(self.success_day_label, 1, 0, 1, -1)
        else:
            dlg = QtWidgets.QErrorMessage()
            dlg.showMessage("Бюджет на день должен быть введен в числовом формате.\n")
            dlg.setWindowTitle("QDialog")
            dlg.resize(200, 50)
            dlg.exec()
            self.success_day_label.setText(f"")
            self.layout.addWidget(self.success_day_label, 1, 0, 1, -1)

    def on_renew_week_button_click(self):
        text_week = self.budget_week_input_field

        if (
            text_week.text() is not None
            and check_float(str(text_week.text())) is not None
        ):
            self.par.control_table.setItem(
                1, 1, QtWidgets.QTableWidgetItem(str(text_week.text()))
            )
            self.success_week_label.setText(f"Бюджет на неделю обновлен")
            self.layout.addWidget(self.success_week_label, 3, 0, 1, -1)
        else:
            dlg = QtWidgets.QErrorMessage()
            dlg.showMessage("Бюджет на неделю должен быть введен в числовом формате.\n")
            dlg.setWindowTitle("QDialog")
            dlg.resize(200, 50)
            dlg.exec()
            self.success_week_label.setText(f"")
            self.layout.addWidget(self.success_week_label, 3, 0, 1, -1)

    def on_renew_month_button_click(self):
        text_month = self.budget_month_input_field

        if (
            text_month.text() is not None
            and check_float(str(text_month.text())) is not None
        ):
            self.par.control_table.setItem(
                2, 1, QtWidgets.QTableWidgetItem(str(text_month.text()))
            )
            self.success_month_label.setText(f"Бюджет на месяц обновлен")
            self.layout.addWidget(self.success_month_label, 5, 0, 1, -1)
        else:
            dlg = QtWidgets.QErrorMessage()
            dlg.showMessage("Бюджет на месяц должен быть введен в числовом формате.\n")
            dlg.setWindowTitle("QDialog")
            dlg.resize(200, 50)
            dlg.exec()
            self.success_month_label.setText(f"")
            self.layout.addWidget(self.success_month_label, 5, 0, 1, -1)

    def budget_day_input(self):
        self.budget_day_input_field = QtWidgets.QLineEdit("")
        return self.budget_day_input_field

    def budget_week_input(self):
        self.budget_week_input_field = QtWidgets.QLineEdit("")
        return self.budget_week_input_field

    def budget_month_input(self):
        self.budget_month_input_field = QtWidgets.QLineEdit("")
        return self.budget_month_input_field


class MainWindow(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        expenses_label = QtWidgets.QLabel("Расходы")
        self.status_label = QtWidgets.QLabel(" ")
        control_label = QtWidgets.QLabel("Бюджет")
        add_button = QtWidgets.QPushButton("Добавить расход")
        invite_label = QtWidgets.QLabel("Сумма")
        category_label = QtWidgets.QLabel("Категория")
        correct_budget_button = QtWidgets.QPushButton("Редактировать бюджет")
        correct_category_button = QtWidgets.QPushButton("Редактировать категории")
        correct_list_button = QtWidgets.QPushButton("Редактировать записи")

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(expenses_label, 0, 0)
        self.layout.addWidget(
            self.status_label, 0, 2, alignment=QtCore.Qt.AlignmentFlag.AlignRight
        )
        self.layout.addWidget(self.expenses_table_func(), 1, 0, 1, -1)
        self.layout.addWidget(control_label, 2, 0)
        self.layout.addWidget(self.control_table_func(), 3, 0, 1, -1)
        self.layout.addWidget(
            invite_label, 4, 0, 1, 1, alignment=QtCore.Qt.AlignmentFlag.AlignRight
        )
        self.layout.addWidget(
            self.expenses_input("Введите сумму расходов"), 4, 1, 1, -1
        )
        self.layout.addWidget(
            category_label, 5, 0, 1, 1, alignment=QtCore.Qt.AlignmentFlag.AlignRight
        )
        self.category_combobox()
        self.layout.addWidget(self.combo, 5, 1, 1, -1)
        self.layout.addWidget(add_button, 6, 0, 1, -1)

        self.layout.addWidget(correct_budget_button, 7, 0, 1, 1)
        self.layout.addWidget(correct_category_button, 7, 1, 1, 1)
        self.layout.addWidget(correct_list_button, 7, 2, 1, 1)

        self.setLayout(self.layout)

        add_button.clicked.connect(self.on_add_button_click)
        correct_budget_button.clicked.connect(self.on_budget_button_click)
        correct_category_button.clicked.connect(self.on_category_button_click)
        # self.control_table.cellClicked.connect(self.on_control_cell_click)
        # self.expenses_table.cellChanged.connect(self.control_cell_change)
        self.setWindowTitle("The Bookkeeper App")
        self.setGeometry(900, 100, 700, 500)

    # def on_control_cell_click(self, row, column):
    #     self.prev_item = self.control_table.item(row, column)

    # def control_cell_change(self, row, column):
    #     self.new_item = self.control_table.item(row, column)
    #     if self.new_item is None:
    #         self.control_table.setItem(row, column, self.prev_item)
    #     elif check_float(self.new_item.text()) is None:
    #         self.control_table.setItem(
    #             row, column, QtWidgets.QTableWidgetItem(str(self.prev_item.text()))
    #         )
    # else:
    #     self.control_table.setItem(
    #         row, column, QtWidgets.QTableWidgetItem(self.new_item.text())
    #     )

    def on_add_button_click(self):
        category_text = str(self.reading_combobox())
        sum_text = str(self.reading_sum())
        if check_float(sum_text) is None:
            dlg = QtWidgets.QErrorMessage()
            dlg.showMessage("Сумма должна быть введена в числовом формате.\n")
            dlg.setWindowTitle("QDialog")
            dlg.resize(200, 50)
            dlg.exec()
        else:
            self.expenses_table.setItem(0, 1, QtWidgets.QTableWidgetItem(sum_text))
            self.expenses_table.setItem(0, 2, QtWidgets.QTableWidgetItem(category_text))
            self.expenses_table.setItem(
                0,
                0,
                QtWidgets.QTableWidgetItem(
                    str(datetime.date.today().strftime("%d/%m/%Y"))
                ),
            )
            self.status_label.setText("Расходы добавлены")

    def on_category_button_click(self):
        count = self.combo.count()
        categoryes = [self.combo.itemText(i) for i in range(count)]
        self.w = CategoryWindow(self, categoryes=categoryes)
        self.w.show()

    def on_budget_button_click(self):
        self.b = BudgetWindow(self)
        self.b.show()

    def expenses_table_func(self):
        self.expenses_table = QtWidgets.QTableWidget(4, 20)
        self.expenses_table.setColumnCount(4)
        self.expenses_table.setRowCount(20)
        self.expenses_table.setHorizontalHeaderLabels(
            "Дата Сумма Категория Комментарий".split()
        )
        header = self.expenses_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.expenses_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.expenses_table.verticalHeader().hide()
        return self.expenses_table

    def control_table_func(self):
        self.control_table = QtWidgets.QTableWidget(2, 3)

        self.control_table.setColumnCount(2)
        self.control_table.setRowCount(3)
        self.control_table.setHorizontalHeaderLabels("Сумма Бюджет".split())
        self.control_table.setVerticalHeaderLabels("День Неделя Месяц".split())
        hor_header = self.control_table.horizontalHeader()
        hor_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        hor_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        # hor_header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.control_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        ver_header = self.control_table.verticalHeader()
        ver_header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        ver_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        ver_header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.control_table.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents
        )
        self.control_table.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )

        return self.control_table

    def expenses_input(self, text):
        self.expenses_input_field = QtWidgets.QLineEdit(f"{text}")
        return self.expenses_input_field

    def category_combobox(self):
        self.combo = QtWidgets.QComboBox()
        self.combo.addItem("Продукты")
        self.combo.addItem("Образование")
        self.combo.addItem("Транспорт")
        self.combo.addItem("Дом")
        return self.combo

    def reading_combobox(self):
        return self.combo.currentText()

    def reading_sum(self):
        return self.expenses_input_field.text()

    def add_category(self, text):
        self.combo.addItem(f"{text}")

    def delete_category(self, categoryes):
        self.combo.clear()
        for i in categoryes:
            self.combo.addItem(f"{i}")


app = QtWidgets.QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
app.exec_()
