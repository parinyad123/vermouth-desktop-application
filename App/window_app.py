import multiprocessing
import sys
import os
import rootpath
import subprocess
from random import randint
import pandas as pd
import sys
import platform
from subprocess import Popen
from pathlib import Path
from PySide6 import QtCore, QtGui
from PySide6.QtCore import Qt, QStringListModel
from PySide6.QtWidgets import (QApplication, QLabel, QListWidget, QTreeWidget, QTreeWidgetItem, 
            QWidget, QListWidgetItem, QPushButton, QVBoxLayout, 
            QHBoxLayout, QCheckBox, QTextEdit)

from main_menu import show_mainmenu
from db_record_management import main_db_management


sys.path.append("".join([rootpath.detect(),"/database"]))
from database import connect_database as connprog


import settings
# settings.init()

# data = data_tm.data_dict()

def create_dictdata():
    
    data = {}
    conn = connprog('MIXERs2_tm_record_db')
    th1_tmname_sql = """
                SELECT th1_tmname.id, th1_tmname.tmname, th1_tmname.property, 
                th1_tmname.description, th1_tmname.tmsubsystem_id, 
				th1_tmname.tmoperation_id,
                th1_tmprogress.progress_id,
				th1_idprogress.progressname
				FROM th1_tmname
                INNER JOIN th1_tmprogress ON th1_tmprogress.id = th1_tmname.id
				INNER JOIN th1_idprogress ON th1_tmprogress.progress_id = th1_idprogress.id;
            """
    th1_tmname = pd.read_sql_query(th1_tmname_sql, conn)

    # id_subopr_sql = "SELECT DISTINCT  tmsubsystem_id, tmoperation_id FROM {} ORDER BY tmoperation_id;".format('th1_tmname')
    # id_subopr = pd.read_sql_query(id_subopr_sql, conn)
    # id_subopr = id_subopr.set_index('tmoperation_id')

    id_sub_sql = """SELECT * FROM {};""".format('th1_tmsubsystem')
    id_sub_df = pd.read_sql_query(id_sub_sql, conn)

    id_ope_sql = """SELECT * FROM {};""".format('th1_tmoperation')
    id_ope_df = pd.read_sql_query(id_ope_sql, conn)

    id_prog_sql = """SELECT * FROM {};""".format('th1_idprogress')
    id_prog_df = pd.read_sql_query(id_prog_sql, conn)
    
    conn.close()

    ######## convert dataframe to json
    # print(th1_tmname)
    split_t = '/-/'
    for id_sub in id_sub_df['id'].tolist():
        
        # print(f'------------{id_sub}-----------')
        new_df = th1_tmname[th1_tmname['tmsubsystem_id']==id_sub]
        new_df = new_df.reset_index()
        # print(new_df)
        id_oper = [i for i in new_df['tmoperation_id'].unique()]
        # print(id_oper)

        operation_dict = {}
        for j in id_oper:
            operation_dict[j] = []
        # print(operation_dict)
        # print('--------------------')
        # print(new_df)
        for t in range(len(new_df)):
            # print(new_df['progressname'][t])
            # print(id_prog_df[id_prog_df['id']==new_df['progress_id'][t]])
            # print("= ",str(id_prog_df[id_prog_df['id']==new_df['progress_id'][t]]['progressname'][new_df['progress_id'][t]]))
            operation_dict[new_df['tmoperation_id'][t]].append(new_df['tmname'][t]+split_t+
            # id_prog_df[id_prog_df['id']==1]['progressname'][1]
            # str(id_prog_df[id_prog_df['id']==new_df['progress_id'][t]]['progressname'][new_df['progress_id'][t]])+
            new_df['progressname'][t]+
            split_t+new_df['description'][t]+split_t+new_df['property'][t])
        # print(operation_dict)

        new_operation_dict = {}
        for k, v in operation_dict.items():
            # print(k)
            ope = str(id_ope_df[id_ope_df['id']==k]['operationname'][k-1])
            # print(k, type(ope), ope)
            new_operation_dict[ope] = v


        sub_name = id_sub_df[id_sub_df['id']==id_sub]['subsystemname'][id_sub-1]
        data[sub_name] = new_operation_dict

    return data, id_prog_df


class Widget(QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        self.setWindowTitle("VERMOUTH Application")
        self.treeWidget = QTreeWidget()
        self.menu_widget = QListWidget()
        self.oper = "operatorA"
        # print('print self. ',self.oper)
        self.data, self.id_prog_df = create_dictdata()
        self.tm_name = ''
        
        for i in self.data.keys():
            item = QListWidgetItem(f"{i}")
            item.setTextAlignment(Qt.AlignCenter)
            self.menu_widget.addItem(item)

        self.menu_widget.currentItemChanged.connect( self.index_changed )
        
        self.menu_widget.itemClicked.connect( self.treeWidget_change )

        self.treeWidget.setColumnCount(1)
        # self.treeWidget.setHeaderLabels(["TM parameter", "progression"])
        self.treeWidget.setHeaderLabels([""])

        self.treeWidget.itemClicked.connect( self.currant_item_change )

        self.button = QPushButton("OK")
        self.button.setDisabled(True)

        content_layout = QVBoxLayout()
        content_layout.addWidget(self.treeWidget)
        content_layout.addWidget(self.button)
        self.button.clicked.connect( lambda: self.send_order(self.itemState) )
        main_widget = QWidget()
        main_widget.setLayout(content_layout)

        layout = QHBoxLayout()
        layout.addWidget(self.menu_widget, 1)
        layout.addWidget(main_widget, 5)
        self.setLayout(layout)

    # @property


    def index_changed(self, inx): # Not an index, i is a QListItem
        # print(inx.text())
        self.oper = inx.text()
        # print('self.oper = ', self.oper.text())
        return self.oper
        # print(data)

    # def close_event(self,event):
    #     event.accept()

    def send_order(self, tmStatus):
        self.button.setDisabled(True)
        self.button.setText('In process ...')
        # main_order_management(tmStatus)
        self.tm_name = tmStatus.split('.')[0]
        # print('---> tm name ', self.tm_name)
        # p = multiprocessing.Process(target=show_mainmenu)
        # p.start()
        path_application = "".join([rootpath.detect(),"/App/main_menu.py"])
        # path_application='/home/mmgs/WindowsVermouth/App/main_menu.py'
        subprocess.call(f'python3 {path_application} {self.tm_name}', shell=True)


        # print("-------- procress main menu ---ja ")
        # p.join()

        # show_mainmenu()
        # return 0
        
        # self.w = AnotherWindow()
        # self.w.show()
        # # QtCore.QCoreApplication.instance().quit
        # # QApplication.quit()
        # self.close()
        # self.w.show()
        # self.close_event(self)
        # sent_global_tmname(self.tm_name)
        # main_db_management(self.tm_name)
        # show_mainmenu(self.tm_name)
        

    def currant_item_change(self,itemW, column): # Not an index, i is a QListItem
        self.itemW = itemW
        self.itemState = itemW.text(0)+'.'+itemW.text(1)
        # print("{}, {}: {}".format(self.itemW.text(0),self.itemW.text(1), column))

        if self.itemW.text(1) != '':
            # print(True)
            self.button.setDisabled(False)
            self.button.setText('OK')           
        else:
            # print(False)
            self.button.setDisabled(True)
            self.button.setText('OK')

    def treeWidget_change(self, oper_name):
        self.button.setDisabled(True)
        self.button.setText('OK')
        # print('click = ', oper_name.text())
        # self.treeWidget.editItem(self.items)
        self.treeWidget.clear()
        self.treeWidget.setColumnCount(1)
        self.treeWidget.setHeaderLabels(["TM parameter", "progress status", 'description', 'property'])

        # id_prog_df_copy = self.id_prog_df.copy()
        id_prog_df_copy = self.id_prog_df.set_index('id')
     
        self.items = []

        for key, values in self.data[oper_name.text()].items():
           
            # print('-------------------------------')
            item = QTreeWidgetItem(self.treeWidget,[key])
            # print(item)
            for value in values:
                value = value.split("/-/")
                TM_parameter = value[0]
                progression = value[1]
                description = value[2]
                property = value[3]

                child = QTreeWidgetItem([TM_parameter, progression, description, property])

                if progression == id_prog_df_copy['progressname'][0]:
                # if progression == "waiting to preprocess":
                    color = "#FFF"
                elif progression == id_prog_df_copy['progressname'][1]:
                # elif progression == "waiting to create feature":                
                    color = "#FFFFCC"
                elif progression == id_prog_df_copy['progressname'][2]:
                # elif progression == "waiting to train model":                
                    color = "#CCFFFF" 
                elif progression == id_prog_df_copy['progressname'][3]:
                # elif progression == "success":                
                    color = "#CCFFCC" 
                elif progression == id_prog_df_copy['progressname'][90]:
                # elif progression == "No record telemetry in MIXERS/MIXERS-II":
                    color = "#FFCCCC"
                elif progression == id_prog_df_copy['progressname'][91]:
                    # elif progression == "No record telemetry in MIXERS/MIXERS-II":
                    color = "#FFE4C4"
                else:
                    color = "#808080"
                child.setBackground(1,QtGui.QBrush(QtGui.QColor(color)))
                item.addChild(child)          
            
            self.items.append(item)
            # print(self.items)
        self.treeWidget.insertTopLevelItems(0, self.items)
        self.treeWidget.expandToDepth(0)
class AnotherWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("Another Window % d" % randint(0,100))
        layout.addWidget(self.label)
        self.setLayout(layout)

def open_windows_app():
    app = QApplication()
  
    w = Widget()
    w.resize(800, 600)
    w.show()

    # path = Path(__file__).parent
    path_window_style = ("".join([rootpath.detect(),"/App/window_style.qss"]))
    with open(path_window_style, "r") as f:
    # with open(path/"style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)
    # app.quit()
    # app.exec()
    # p = multiprocessing.Process(target=show_mainmenu)
    # p.start()
    # p.join()
    sys.exit(app.exec())

      
if __name__ == "__main__":   
    print("0")
    app = QApplication()
    print("1")
    w = Widget()
    w.resize(1200, 850)
    w.show()
    print("2")
    # path = Path(__file__).parent
    # path_window_style = ("".join([rootpath.detect(),"\windowapp-vermouth\App\window_style.qss"]))
    path_window_style = ("".join([rootpath.detect(),"/App/window_style.qss"]))
    with open(path_window_style, "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)
    sys.exit(app.exec())
    print("3")
    # open_windows_app()
    # print(tm)


    # conn = connprog('MIXERs2_tm_record_db')
    # print('--> connect --> ',conn)
    # # print(create_dictdata())
    # path = ("".join([rootpath.detect(),"\windowapp-vermouth\App"]))
    # print(path)