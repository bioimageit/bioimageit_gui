import os
import sys
import csv
from pathlib import Path
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
        
    # load the file uri
    file_uri = ""
    if len(sys.argv) > 1:
        file_uri = sys.argv[1]
    if file_uri == "":
        print("csv viewer: no input file")

    # Create and show the viewer
    widget = QWidget()
    widget.setObjectName('BiWidget')
    layout = QVBoxLayout()
    layout.setContentsMargins(0,0,0,0)
    widget.setLayout(layout)

    tableWidget = QTableWidget()  
    layout.addWidget(tableWidget)

    with open(file_uri, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        rows = list(spamreader)

        tableWidget.setRowCount(len(rows))
        if len(rows) > 0:
            tableWidget.setColumnCount( len(rows[0]) )
        row_idx = 0
        for row in rows:
            col_idx = 0
            for el in range(len(row)):
                tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(row[el]))  
                col_idx += 1
            row_idx += 1 

    widget.show()        
    
    # Run the main Qt loop
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = Path(dir_path).parent.parent
    stylesheet_path = os.path.join(dir_path, 'theme', 'dark', 'stylesheet.css')
    app.setStyleSheet("file:///" + stylesheet_path)
    icon_path = os.path.join(dir_path, "theme", "default", "icon.png" )
    app.setWindowIcon(QIcon(icon_path))
    sys.exit(app.exec_())