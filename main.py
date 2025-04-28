from PyQt5.QtWidgets import QMainWindow, QApplication,QFileDialog, QErrorMessage
from ui.ui import Ui_MainWindow
import os
from utils import draw_graph, extract_delays, list_names
from datetime import datetime
import json

DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton_openfolder.clicked.connect(self.open_folder)
        self.ui.pushButton_star.clicked.connect(self.start)
        self.ui.pushButton_corridors.clicked.connect(self.show_names)

        self.folder_path = None

    def open_folder(self):
        self.folder_path = QFileDialog.getExistingDirectory(self, "Open Folder")
        if self.folder_path:
            self.ui.lineEdit.setText(self.folder_path)

    def show_names(self):
        # Check folder_path
        if self.folder_path is None:
            self.error = QErrorMessage()
            self.error.showMessage("No hay carpeta seleccionada")
            return

        folder_path = self.folder_path
        day = self.ui.calendarWidget.selectedDate().toString("dd/MM/yyyy")
        json_path = os.path.join(folder_path, day.replace('/', ''))
        last_json_path = [os.path.join(json_path, file) for file in os.listdir(json_path)][-1]
        with open(last_json_path) as f:
            json_data = json.load(f)
        name_list = list_names(json_data)
        return self.ui.textBrowser.setText("\n".join(name_list))

    def start(self):
        # Check folder_path
        if self.folder_path is None:
            self.error = QErrorMessage()
            self.error.showMessage("No hay carpeta seleccionada")
            return
        elif self.ui.lineEdit_2.text() == "":
            self.error = QErrorMessage()
            self.error.showMessage("No hay corredor seleccionado")
            return
        
        # Calling calendar
        selected_date = self.ui.calendarWidget.selectedDate()
        date_str = selected_date.toString("dd/MM/yyyy")
        
        # Checking if there is a date selected
        list_days = os.listdir(self.folder_path)
        if date_str.replace('/', '') not in list_days:
            self.error = QErrorMessage()
            self.error.showMessage("No hay datos para la fecha seleccionada")
            return
        else:
            message = "Sí existe coincidencia"
            status_bar = self.statusBar()
            status_bar.showMessage(message)

        day_folder = os.path.join(self.folder_path, date_str.replace('/', ''))
        selected_corridor = self.ui.lineEdit_2.text()
        results = extract_delays(day_folder, selected_corridor)

        date = datetime.strptime(date_str, "%d/%m/%Y")
        date_name = DIAS_SEMANA[date.weekday()]
        draw_graph(results, "travel_time", day = f"{date_name + ' ' + date_str}", selected_corridor = selected_corridor)


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()

"""
NOTES:
- Agregar nombre de corredores escogidos.
"""