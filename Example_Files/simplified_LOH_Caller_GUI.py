# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 11:37:12 2024

@author: joylove5

Goal: Simplified LOH Caller with User Interface
"""

### Depedentcies
import pandas as pd
import numpy as np
import sys
#import os
from PyQt5.QtCore import Qt, QCoreApplication, QtCore
from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTabWidget,
                             QTextEdit, QDialog, QLabel, QHBoxLayout, QLineEdit, QFileDialog)

############################# Functions for functionality #####################
### Haplotype-Aware Tables
def Make_haplotype_aware(clone_table, clone_name, path, minimum_coverage):
    # Taking in Variants  
    variant_df = pd.read_csv(clone_table, sep="\t", comment="#", header=None)
    variant_df.columns = ["CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT", clone_name]
    variant_df["ID"] = variant_df["CHROM"] + "_" + variant_df["POS"].astype(str)
    variant_df = variant_df.drop(variant_df[variant_df["ID"] == "chr9_431988"].index)
    variant_df = variant_df.drop(variant_df[variant_df["ID"] == "chr10_416768"].index)
    
    # Building Clone Variant Table
    new_df = pd.DataFrame()
    new_df["ID"] = variant_df["ID"]
    new_df["S288c_Parent_Allele"] = variant_df["REF"]
    new_df["SK1_Parent_Allele"] = variant_df["ALT"]
    new_df[clone_name + "_Variant_Allele"] = variant_df["ALT"]
    
    # Build coverage and frequency columns
    co_cov = [word.strip().split(',')[1] for word in variant_df[clone_name]]
    count, coverage = zip(*((int(num.strip().split(':')[0]), int(num.strip().split(':')[1])) for num in co_cov))
    new_df[clone_name + "_Variant_Coverage"] = coverage
    frequency = np.round([(count[i] / coverage[i]) * 100 if coverage[i] != 0 else 0 for i in range(len(count))], decimals=2)
    new_df[clone_name + "_Variant_Frequency"] = frequency

    # Genotype Determination
    zygosity = ["Homozygous for SK1" if percent > 89 else "Heterozygous" if 11 <= percent <= 89 else "Homozygous for S288c" for percent in new_df[clone_name + "_Variant_Frequency"]]
    zygosity = ["No Call Due to Low Coverage" if cov <= minimum_coverage else zygosity[i] for i, cov in enumerate(new_df[clone_name + "_Variant_Coverage"])]
    new_df[clone_name + "_Genotype"] = zygosity
    
    # Making Output CSV file
    new_df.to_csv(path + "/" + clone_name + "_Haplotype_Aware_Table(VCF).csv", index=False)
    return new_df

def Create_master_variant_table(clone_list_file, path, output_path, coverage_minimum):
    master_df = pd.DataFrame()
    with open(clone_list_file, "r") as file:
        clone_tables = [line.strip() for line in file]
    
    for clone_table in clone_tables:
        new_df = Make_haplotype_aware(clone_table, clone_table.split(' (')[0], path, coverage_minimum)
        if master_df.empty:
            master_df = new_df[["ID", "S288c_Parent_Allele", "SK1_Parent_Allele"]].copy()
        columns_to_merge = [
            "ID",
            f"{clone_table.split(' (')[0]}_Variant_Coverage",
            f"{clone_table.split(' (')[0]}_Variant_Frequency",
            f"{clone_table.split(' (')[0]}_Genotype"
        ]
        master_df = pd.merge(master_df, new_df[columns_to_merge], on="ID", how="outer")
    
    master_df.to_csv(output_path, index=False)
    return master_df

################ Classes and Functions for Graphical Interface ################
### Diplay Pandas Dataframes
class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return QtCore.QVariant(str(
                    self._data.iloc[index.row()][index.column()]))
        return QtCore.QVariant()

### For Haplotype-Aware Tables
class HapTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.wd_label = QLabel("Working Directory:")
        self.wd_edit = QLineEdit()
        self.wd_button = QPushButton("Browse")
        self.wd_button.clicked.connect(self.browse_wd)

        self.output_dir_label = QLabel("Output Directory:")
        self.output_dir_edit = QLineEdit()
        self.output_dir_button = QPushButton("Browse")
        self.output_dir_button.clicked.connect(self.browse_output_dir)

        self.clone_tables_list_label = QLabel("Clone Tables List:")
        self.clone_tables_list_edit = QLineEdit()
        self.clone_tables_list_button = QPushButton("Browse")
        self.clone_tables_list_button.clicked.connect(self.browse_clone_table_list)
        
        self.coverage_minimum_label = QLabel("Minimum Coverage:")
        self.coverage_minimum_edit = QLineEdit()
        
        self.master_haplotype_table_label = QLabel("Master Haplotype Table Name:")
        self.master_haplotype_table_edit = QLineEdit()

        self.button = QPushButton("Generate Haplotype-Aware Tables")
        
        self.output_label = QLabel("Output:")
        self.text_edit = QTextEdit()

        self.layout.addWidget(self.wd_label)
        self.layout.addWidget(self.wd_edit)
        self.layout.addWidget(self.wd_button)
        self.layout.addWidget(self.output_dir_label)
        self.layout.addWidget(self.output_dir_edit)
        self.layout.addWidget(self.output_dir_button)
        self.layout.addWidget(self.clone_tables_list_label)
        self.layout.addWidget(self.clone_tables_list_edit)
        self.layout.addWidget(self.clone_tables_list_button)
        self.layout.addWidget(self.coverage_minimum_label)
        self.layout.addWidget(self.coverage_minimum_edit)
        self.layout.addWidget(self.master_haplotype_table_label)
        self.layout.addWidget(self.master_haplotype_table_edit)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.output_label)
        self.layout.addWidget(self.text_edit)
        self.setLayout(self.layout)

        self.button.clicked.connect(self.tab2_function)

    def browse_wd(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Working Directory")
        if directory:
            self.wd_edit.setText(directory)

    def browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_dir_edit.setText(directory)
    
    def browse_clone_table_list(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select File with List of Clone Table Names", "", "TXT Files (*.txt);;All Files (*)")
        if file:
            self.clone_tables_list_edit.setText(file)
        
    def tab2_function(self):
        wd = self.wd_edit.text()
        output_dir = self.output_dir_edit.text()
        clone_tables_list = self.clone_tables_list_edit.text()
        coverage_minimum = int(self.coverage_minimum_edit.text())
        master_haplotype_table = self.master_haplotype_table_edit.text()

        """ 
        self.text_edit.append("Executing Tab 2 Function with inputs:")
        self.text_edit.append(f"Working Directory: {wd}")
        self.text_edit.append(f"Output Directory: {output_dir}")
        self.text_edit.append(f"Clone Tables List: {clone_tables_list}")
        self.text_edit.append(f"Minimum Coverage: {coverage_minimum}")
        self.text_edit.append(f"Master Haplotype Table: {master_haplotype_table}")
        """
        # Call Create_master_variant_table function
        master_df = Create_master_variant_table(clone_tables_list, wd, output_dir + "/" + master_haplotype_table, coverage_minimum)
        self.text_edit.append(f"Master Haplotype Table Created: {output_dir}/{master_haplotype_table}")
        
        master_df_str = master_df.to_string()
        self.text_edit.append(master_df_str)
        
### Main Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LOH Caller")
        self.setGeometry(100, 100, 800, 1000)
        
        self.apply_styles()
               
    ### Making Window Dark-Mode
    def apply_styles(self):
        dark_palette = QPalette()

        # Base colors
        dark_palette.setColor(QPalette.Window, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.black)
        dark_palette.setColor(QPalette.Button, QColor(70, 70, 70))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)

        # Disabled colors
        dark_palette.setColor(QPalette.Disabled, QPalette.Text, QColor(0, 0, 0))
        dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))

        # Highlight colors
        dark_palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        app.setPalette(dark_palette)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #2D2D2D;
            }
            QTabWidget::pane {
                border: 1px solid darkgray;
                top:-1px; 
                background: rgb(30, 30, 30);; 
            } 

            QTabBar::tab {
                background: rgb(30, 30, 30); 
                border: 1px solid darkgray; 
                padding: 15px;
                } 

            QTabBar::tab:selected { 
                background: rgb(20, 20, 20); 
                margin-bottom: -1px;     
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                background-color: #3E3E3E;
                color: white;
                border: 1px solid #1D1D1D;
                padding: 5px;
            }
            QTextEdit {
                background-color: #3E3E3E;
                color: white;
                border: 1px solid #1D1D1D;
                padding: 5px;
            }
            QPushButton {
                background-color: #4B0082;
                color: white;
                border: none;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #551A8B;
            }
            QPushButton:pressed {
                background-color: #3E0066;
            }
        """)

    def setup_ui(self):
        self.tabs = QTabWidget()
        self.haptab = HapTab()
        
        self.tabs.addTab(self.haptab, "Haplotype-Aware Tables Genotype Calls")
        self.tabs.setCurrentIndex(self.selected_tab)
        self.setCentralWidget(self.tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())