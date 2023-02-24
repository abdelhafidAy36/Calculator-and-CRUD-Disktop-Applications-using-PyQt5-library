import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import Login
import Data_Base
import cx_Oracle

class mainApplication(QWidget):
    # pour réinitialiser l'application
    EXIT_CODE_REBOOT = -123

    def __init__(self):
        super().__init__()
        # creation de la fenêtre login
        self.Form1 = QWidget()
        self.login = Login.Ui_Form()
        self.login.setupUi(self.Form1)
        self.Form1.setWindowIcon(QIcon("Icons/login.png"))
        # connect la button (pushButton_OK) avec le slot (login_page)
        self.Form1.show()
        self.login.pushButton_OK.clicked.connect(self.login_page)

    # methode pour la connexion à la base de données
    def login_page(self):
        user = self.login.lineEdit_User.text()
        password = self.login.lineEdit_Pass.text()
        try:
            # !!!!!
            # makedsn('Host Name', 'Port Number', service_name='Service Name')
            # voire le fichier 'tnsnames.ora' pour votre configuration
            dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='HAFIDDB')
            self.conn = cx_Oracle.connect(user=user, password=password, dsn=dsn_tns)
            # creation de la fenêtre principale (base do donne)
            self.database_page()
        except:
            # affiche une fenêtre si la connexion échoue
            msgBox = QMessageBox()
            msgBox.setText("Nom d'utilisateur ou mot de passe n'est incorrect")
            msgBox.setWindowTitle("Erreur")
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()

    # la fenêtre principale(base de donne)
    def database_page(self):
        # pour devenir la fenêtre login invisible
        self.Form1.hide()
        # creation de la fenêtre principale (base do donne)
        self.Form2 = QWidget()
        self.data_base = Data_Base.Ui_Form()
        self.data_base.setupUi(self.Form2)
        self.Form2.show()

        # combo box items (les tables de l'utilisateur)
        c = self.conn.cursor()
        sql = "SELECT table_name FROM user_tables"
        tables = c.execute(sql)
        self.Tabbles_list = []
        for Row, Rowdata in enumerate(tables):
            for Colmn, data in enumerate(Rowdata):
                self.Tabbles_list.append(str(data))
        self.data_base.comboBox_table.addItems(self.Tabbles_list)

        # icons
        self.data_base.pushButton_ouvrir.setIcon(QIcon("Icons/open.png"))
        self.data_base.pushButton_changee.setIcon(QIcon("Icons/user-transfer.png"))
        self.data_base.pushButton_Actualiser.setIcon(QIcon("Icons/update.png"))
        self.data_base.pushButton_Ajouter.setIcon(QIcon("Icons/add.png"))
        self.data_base.pushButton_Suppimer.setIcon(QIcon("Icons/delete.png"))
        self.data_base.pushButton_Enregistrer.setIcon(QIcon("Icons/save.png"))
        self.Form2.setWindowIcon(QIcon("Icons/database.png"))

        # connect les boutons
        self.data_base.pushButton_ouvrir.clicked.connect(self.ouvrir)
        self.data_base.pushButton_changee.clicked.connect(self.change_user)
        self.data_base.pushButton_Actualiser.clicked.connect(self.affiche)
        self.data_base.pushButton_Ajouter.clicked.connect(self.Ajouter)
        self.data_base.pushButton_Enregistrer.clicked.connect(self.Enregistrer)
        self.data_base.pushButton_Suppimer.clicked.connect(self.Supprimer)

        # nbAdds : nombre des lignes que nous avons ajouté
        self.nbAdds = 0

    # sélectionne la table (créer une list pour COLUMN_NAME et une list pour DATA_TYPE)
    def ouvrir(self):
        # la table sélectionnée
        self.currTable = self.data_base.comboBox_table.currentText()

        c = self.conn.cursor()
        sql = "SELECT COLUMN_NAME, DATA_TYPE FROM user_tab_columns WHERE table_name = '{}'".format(self.currTable)
        col_types = c.execute(sql)

        # les Listes des COLUMN/TYPE
        self.listCols = []
        self.listTypes = []

        for Row_number, Row_Data in enumerate(col_types):
            self.listCols.append(str(Row_Data[0]))
            self.listTypes.append(str(Row_Data[1]))

        c.close()

        # affiche la table
        self.affiche()
        self.data_base.label.setText("")

    # réinitialiser l'application
    def change_user(self):
        qApp.exit(mainApplication.EXIT_CODE_REBOOT)

    # afficher le contenu de la table
    def affiche(self):
        try:
            # insert les Colonne de table
            self.data_base.tableWidget.setColumnCount(len(self.listCols))
            self.data_base.tableWidget.setHorizontalHeaderLabels(self.listCols)

            # insert les lignes de table
            c = self.conn.cursor()
            sql = "select * from " + self.currTable + " ORDER BY " + self.listCols[0]
            Select = c.execute(sql)
            # serRowCount(0) : réinitialiser les ligne de la table a 0
            self.data_base.tableWidget.setRowCount(0)
            for row_number, row_data in enumerate(Select):
                # insertRow() : ajoute une ligne vide  la fin du tableau (index row_number)
                self.data_base.tableWidget.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    item = str(data)
                    # pour affiche la date de form 'DD-MM-YYYY' dans la table
                    if self.listTypes[column_number] == 'DATE':
                        self.data_base.tableWidget.setItem(row_number, column_number, QTableWidgetItem(item[0:10]))
                    else:
                        self.data_base.tableWidget.setItem(row_number, column_number, QTableWidgetItem(item))
            c.close()

            self.data_base.label.setText("")
            self.nbAdds = 0
            self.data_base.pushButton_Enregistrer.setText("Enregistrer")
        except:
            self.data_base.label.setText("Sélectionnez la table !")

    # Ajouter une ligne vide à la fin du tableau
    def Ajouter(self):
        # rowCount() : retourner le nombre des ligne de table
        self.NewRow = self.data_base.tableWidget.rowCount()
        self.data_base.tableWidget.insertRow(self.NewRow)
        self.nbAdds += 1
        self.data_base.pushButton_Enregistrer.setText("Enregistrer ("+str(self.nbAdds)+")")

    # Supprimer une ligne sélectionnée
    def Supprimer(self):
        try:
            c = self.conn.cursor()
            # selectedItems() : retourner les elements sélectionné de table
            Row = self.data_base.tableWidget.selectedItems()
            # nom de première colonne
            ColName = self.listCols[0]
            # on va utiliser la première colonne Row[0] pour la suppression de la ligne
            if self.listTypes[0] == 'VARCHAR2':
                sql = "DELETE FROM {} WHERE {} = '{}'".format(self.currTable, ColName, Row[0].text())

            else:
                sql = "DELETE FROM {} WHERE {} = {}".format(self.currTable, ColName, Row[0].text())

            c.execute(sql)
            # indxRox : index de  ligne sélectionné
            indxRox = self.data_base.tableWidget.row(Row[0])
            self.data_base.tableWidget.removeRow(indxRox)

            c.close()
            self.conn.commit()
            self.data_base.label.setText("La suppression a réussi")
        except cx_Oracle.DatabaseError as er:
            msgBox = QMessageBox()
            msgBox.setText(str(er))
            msgBox.setWindowTitle("DatabaseError")
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
        except:
            self.data_base.label.setText("Erreur sur la suppression")

    # Enregistrez les modifications et les lignes que nous avons ajoutées
    def Enregistrer(self):
        # Enregistrer les modifications
        self.EnrgMod()
        # Enregistrer les lignes
        self.EnrgAdd()

    # Enregistrer les modifications
    def EnrgMod(self):
        # Pour enregistrer les modifications, nous comparerons toutes les données de la table  (de base de données)
        # avec les données du table  (QTableWidget)
        try:
            c = self.conn.cursor()
            sql = "select * from " + self.currTable + " ORDER BY " + self.listCols[0]
            Select = c.execute(sql)

            for row_number, row_data in enumerate(Select):
                # si l'element (colonne 0 ) de type DATE ou VARCHAR2 on ajoute les ('')
                itemcol0 = str(row_data[0])
                if self.listTypes[0] == 'VARCHAR2' or self.listTypes[0] == 'DATE':
                    itemcol0 = "'{}'".format(itemcol0)
                for col_number, data in enumerate(row_data):
                    # element de (base de donne)
                    itemSel = str(data)
                    # element de table (QTableWiget)
                    itemTab = self.data_base.tableWidget.item(row_number, col_number).text()
                    # si itemTab != itemSel, on va modifier cette colonne
                    try:
                        c = self.conn.cursor()
                        # 2 cas  ,car dans notre table on afficher seulement les 10 caractere pour le  type 'DATE'
                        # la modification se fera via la première colonne
                        if self.listTypes[col_number] == 'DATE':
                            if itemTab != itemSel[0:10]:
                                if itemTab == "":
                                    sqlupdate = "UPDATE {} SET {} = '' WHERE {} = {}"
                                    c.execute(sqlupdate.format(self.currTable, self.listCols[col_number], self.listCols[0],
                                                               itemcol0))

                                    self.data_base.label.setText("l'enregistrement a réussi")
                                    self.data_base.pushButton_Enregistrer.setText("Enregistrer")
                                else:
                                    # si l'element de type DATE ou VARCHAR2 on ajoute les ''
                                    # Pour la condition du requête UPDATE, nous allons utilisons le premiere colonne
                                    # (itemcol0)
                                    if self.listTypes[col_number] == 'VARCHAR2' or self.listTypes[col_number] == 'DATE':
                                        sqlupdate = "UPDATE {} SET {} = '{}' WHERE {} = {}"
                                    else:
                                        sqlupdate = "UPDATE {} SET {} = {} WHERE {} = {}"
                                    c.execute(sqlupdate.format(self.currTable, self.listCols[col_number], itemTab,
                                                               self.listCols[0], itemcol0))

                                    self.data_base.label.setText("l'enregistrement a réussi")
                                    self.data_base.pushButton_Enregistrer.setText("Enregistrer")
                        else:
                            if itemTab != itemSel:
                                if itemTab == "":
                                    sqlupdate = "UPDATE {} SET {} = '' WHERE {} = {}"
                                    c.execute(sqlupdate.format(self.currTable, self.listCols[col_number], self.listCols[0],
                                                               itemcol0))

                                    self.data_base.label.setText("l'enregistrement a réussi")
                                    self.data_base.pushButton_Enregistrer.setText("Enregistrer")
                                else:
                                    if self.listTypes[col_number] == 'VARCHAR2' or self.listTypes[col_number] == 'DATE':
                                        sqlupdate = "UPDATE {} SET {} = '{}' WHERE {} = {}"
                                    else:
                                        sqlupdate = "UPDATE {} SET {} = {} WHERE {} = {}"
                                    c.execute(sqlupdate.format(self.currTable, self.listCols[col_number], itemTab,
                                                               self.listCols[0], itemcol0))

                                    self.data_base.label.setText("l'enregistrement a réussi")
                                    self.data_base.pushButton_Enregistrer.setText("Enregistrer")

                        c.close()
                        self.conn.commit()
                    except cx_Oracle.DatabaseError as er:
                        msgBox = QMessageBox()
                        msgBox.setText(str(er))
                        msgBox.setWindowTitle("DatabaseError")
                        msgBox.setIcon(QMessageBox.Information)
                        msgBox.setStandardButtons(QMessageBox.Ok)
                        msgBox.exec_()
                    except:
                        self.data_base.label.setText("Erreur (modification)")
        except:
            self.data_base.label.setText("Sélectionnez la table !")

    def EnrgAdd(self):
        # lastRow : est le nombre total des lignes de la table
        # nbAdds : est nombre des lignes ajoutee
        lastRow = self.data_base.tableWidget.rowCount()
        # enregistrer seulement les dernières lignes ajoutée
        for Row in range(lastRow - self.nbAdds, lastRow):
            try:
                c = self.conn.cursor()

                # nb des colonne
                nbCol = len(self.listCols)

                sql = "INSERT INTO {} VALUES(".format(self.currTable)

                # première colonnes
                Col0 = self.data_base.tableWidget.item(Row, 0).text()
                if Col0 == "":
                    Col0 = "''"
                else:
                    if self.listTypes[0] == 'VARCHAR2' or self.listTypes[0] == 'DATE':
                        Col0 = "'" + Col0 + "'"
                sql = sql + Col0

                # reste des colonnes
                for Col in range(1, nbCol):
                    item = self.data_base.tableWidget.item(Row, Col)
                    if item is None:
                        item = "''"
                    else:
                        if self.listTypes[Col] == 'VARCHAR2' or self.listTypes[Col] == 'DATE':
                            item = "'" + item.text() + "'"
                        else:
                            item = item.text()
                    sql = sql + "," + item

                # notre requête SQL
                sql = sql + ")"

                c.execute(sql)
                self.conn.commit()
                c.close()

                self.data_base.label.setText("l'enregistrement a réussi")
                self.data_base.pushButton_Enregistrer.setText("Enregistrer")
                self.nbAdds = 0
            except cx_Oracle.DatabaseError as er:
                msgBox = QMessageBox()
                msgBox.setText(str(er))
                msgBox.setWindowTitle("DatabaseError")
                msgBox.setIcon(QMessageBox.Information)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
            except:
                self.data_base.label.setText("Erreur (ajoutation des ligne)")

# cette code pour gérer et réinitialiser l'application
currentExitCode = mainApplication.EXIT_CODE_REBOOT
while currentExitCode == mainApplication.EXIT_CODE_REBOOT:
    app = QApplication(sys.argv)
    app.setStyle("fusion") # style de fenêtre
    w = mainApplication()
    currentExitCode = app.exec_()
    app = None # delete the QApplication object