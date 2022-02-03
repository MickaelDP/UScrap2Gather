import os
import psycopg2
import tweepy

from functools import partial
from PySide6 import QtCore
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QPushButton, QTabWidget, QCheckBox, QLabel, \
    QLineEdit, QToolButton, QListWidget, QTextEdit, QErrorMessage, QListWidgetItem, QInputDialog, \
    QFileDialog, QDialog, QMessageBox, QComboBox

from package.api.Class.DataProfil import Dataps, get_dataps
from package.api.Class.Keywords import Keywords, get_keywords
from package.api.Class.ScrapProfil import SProfile, get_s_profile
from package.api.Class.Log import get_logs
from package.api.constants import KEYWORDS_DIR, CONFIG, DATAS_DIR, CFG_DIR, DATAS_CHECK_TABLE, DATAS_TEMPLATE, \
    DATAS_A_LIST, PROFILE_DIR, ACTIVE_LAUNCH, STOP_THREADS
from package.api.scraper.scraplib import connect_bdd, create_cursor, check_api_twitter_connexion
from package.api.scraper.scraper import scraper


# functions
def populate_dp():
    return get_dataps()


def populate_sc():
    return get_s_profile()


# list of database
def refresh_database(widget):
    combo_db = get_dataps()
    for i in range(int(CONFIG.get("NbrProfil", 1))):
        widget.clear()
        for e in combo_db:
            widget.addItem(f"{e[1]} {combo_db[e].database}")

# refresh list of log
def refresh_log(widget, mainwidget):
    widget.clear()
    mainwidget.populate_log()


# refresh list of keyword
def refresh_keyword(widget):
    combo_kw = get_keywords()
    for i in range(int(CONFIG.get("NbrProfil", 1))):
        widget.clear()
        for e in range(len(combo_kw)):
            widget.addItem(combo_kw[e].title)


# thread
class Worker(QtCore.QObject):
    finished = QtCore.Signal(bool, str)

    def __init__(self, nb):
        super().__init__()
        self.worker_id = nb

    def scrap(self):
        work = scraper(self.worker_id)
        self.finished.emit(work[0], work[1])


# Class GUI
class MainWindows(QTabWidget):
    def __init__(self):
        super().__init__()

        # error messages
        self.error_box = QErrorMessage(self)

        # main
        self.main_layout = QGridLayout(self)
        self.scraper = QWidget()
        self.kw = QWidget()
        self.logs = QWidget()
        self.info = QWidget()

        # scraper init
        self.layout_c = QGridLayout()
        self.scrap_btn_start = QPushButton("Scrap")
        self.scrap_btn_stop = QPushButton("Stop!")
        self.p_s_tab = QTabWidget()
        self.p1 = QWidget()
        self.p2 = QWidget()
        self.p3 = QWidget()
        self.p4 = QWidget()
        self.p5 = QWidget()
        self.p6 = QWidget()
        self.p7 = QWidget()
        self.p8 = QWidget()
        self.r_corner_s = QWidget()
        self.layout_rcs = QHBoxLayout()
        self.more_s = QToolButton()
        self.less_s = QToolButton()

        # data init
        self.dtb = QWidget()
        self.layout_d = QGridLayout()
        self.dtb_tab = QTabWidget()
        self.dtb_tab.setMinimumHeight(30)
        self.d1 = QWidget()
        self.d2 = QWidget()
        self.d3 = QWidget()
        self.d4 = QWidget()
        self.d5 = QWidget()
        self.d6 = QWidget()
        self.d7 = QWidget()
        self.d8 = QWidget()
        self.r_corner_d = QWidget()
        self.layout_rcd = QHBoxLayout()
        self.more_d = QToolButton()
        self.less_d = QToolButton()

        # kw init
        self.layout_k = QGridLayout()
        self.btn_create_keywords = QPushButton("Create")
        self.btn_import_keywords = QPushButton("Import")
        self.btn_export_keywords = QPushButton("Export")
        self.btn_del_keywords = QPushButton("Delete")
        self.lw_notes = QListWidget()
        self.content = QTextEdit()

        # log init
        self.layout = QGridLayout()
        # left
        self.lw_view = QListWidget()
        self.btn_clear = QPushButton("Delete")
        self.btn_clear_all = QPushButton("Delete All")
        # right
        self.log_error_lab = QLabel('Error: ')
        self.log_error_box = QLineEdit()
        self.log_contrib_lab = QLabel('Contributor: ')
        self.log_contrib_box = QLineEdit()
        self.log_db_lab = QLabel('   Database: ')
        self.log_db_box = QLineEdit()
        self.log_name_lab = QLabel('Name: ')
        self.log_name_box = QLineEdit()
        self.log_message_lab = QLabel('Message: ')
        self.log_message = QTextEdit()
        self.log_date_lab = QLabel('Date: ')
        self.log_date_box = QLineEdit()
        self.log_like_lab = QLabel('Like: ')
        self.log_like_box = QLineEdit()
        self.log_retweet_lab = QLabel('Retweet: ')
        self.log_retweet_box = QLineEdit()
        self.btn_rec_log = QPushButton("Record")

        # preset worker n thread
        self.thread_1 = QtCore.QThread()
        self.thread_2 = QtCore.QThread()
        self.thread_3 = QtCore.QThread()
        self.thread_4 = QtCore.QThread()
        self.thread_5 = QtCore.QThread()
        self.thread_6 = QtCore.QThread()
        self.thread_7 = QtCore.QThread()
        self.thread_8 = QtCore.QThread()

        self.worker_1 = Worker(1)
        self.worker_2 = Worker(2)
        self.worker_3 = Worker(3)
        self.worker_4 = Worker(4)
        self.worker_5 = Worker(5)
        self.worker_6 = Worker(6)
        self.worker_7 = Worker(7)
        self.worker_8 = Worker(8)


        # info init
        self.layout_in = QGridLayout()
        self.title = QLabel()

        # window parameters
        self.setWindowTitle("UScrap2Gather")
        self.setFixedSize(800, 450)
        self.setup_ui()

    # -------------------------------------------------------------------------------------------------------------------
    #                                            setup ui
    # -------------------------------------------------------------------------------------------------------------------

    # static setup
    def setup_ui(self):
        self.add_widgets_to_layouts()
        self.setup_connections()

    # static add
    def add_widgets_to_layouts(self):
        # Nav buttons
        self.addTab(self.scraper, "Scraper")
        self.addTab(self.dtb, "Database")
        self.addTab(self.kw, "Keywords")
        self.addTab(self.logs, "Logs")
        self.addTab(self.info, "Infos")
        self.scraper_ui()
        self.dtb_ui()
        self.kw_ui()
        self.logs_ui()
        self.info_ui()

    # static connect
    def setup_connections(self):
        # keywords
        self.populate_notes()
        self.btn_create_keywords.clicked.connect(self.create_keywords)
        self.btn_del_keywords.clicked.connect(self.delete_selected_note)
        self.btn_import_keywords.clicked.connect(self.import_keywords)
        self.btn_export_keywords.clicked.connect(self.export_keywords)
        self.content.textChanged.connect(self.save_note)
        self.lw_notes.itemSelectionChanged.connect(self.populate_note_content)
        QShortcut(QKeySequence("Backspace"), self.lw_notes, self.delete_selected_note)

        # scraper
        self.more_s.clicked.connect(self.nw_p_set)
        self.less_s.clicked.connect(self.dl_p_set)
        self.scrap_btn_start.clicked.connect(self.scrap)
        self.scrap_btn_stop.clicked.connect(partial(self.stop_scrap, True, "ok"))

        # database
        self.more_d.clicked.connect(self.nw_dt_set)
        self.less_d.clicked.connect(self.dl_dt_set)

        # log
        self.populate_log()
        self.lw_view.itemSelectionChanged.connect(self.populate_log_content)
        self.lw_view.itemSelectionChanged.connect(self.populate_log_content)
        self.btn_clear.clicked.connect(self.del_log)
        self.btn_clear_all.clicked.connect(self.del_all_log)
        self.btn_rec_log.clicked.connect(self.rec_log)

    # -------------------------------------------------------------------------------------------------------------------
    #                                            Windows n tab
    # -------------------------------------------------------------------------------------------------------------------
    #                                          scrapper n profile
    # -------------------------------------------------------------------------------------------------------------------

    def scraper_ui(self):
        # add
        self.layout_c.addWidget(self.scrap_btn_start, 0, 0, 1, 2)
        self.layout_c.addWidget(self.scrap_btn_stop, 1, 0, 1, 2)
        self.layout_c.addWidget(self.p_s_tab, 0, 2, 4, 9)
        for tab in range(1, int(CONFIG.get("NbrProfil", 1)) + 1):
            eval('self.p_s_tab.addTab(self.p' + str(tab) + ', "Profile ' + str(tab) + '")')
            widget = eval(f"self.p{tab}")
            self.psc_ui(widget, tab)
        # parameters
        self.more_s.setText('+')
        self.more_s.setAutoRaise(True)
        self.less_s.setText('-')
        self.less_s.setAutoRaise(True)
        self.layout_rcs.setContentsMargins(0, 0, 0, 0)
        self.scrap_btn_stop.setEnabled(False)
        # add
        self.r_corner_s.setLayout(self.layout_rcs)
        self.layout_rcs.addWidget(self.more_s)
        self.layout_rcs.addWidget(self.less_s)
        self.p_s_tab.setCornerWidget(self.r_corner_s, QtCore.Qt.TopRightCorner)
        # tab parameters
        self.setTabText(0, "Scraper")
        self.scraper.setLayout(self.layout_c)

    # *************************************  scraper's methods  *******************************************************

    # generate profile tab for scraper page
    def psc_ui(self, widget, nb):
        data = populate_sc()
        named = "P" + str(nb)
        ct = data.get(named, {})

        widget.layout = QGridLayout()
        # create
        widget.scrap_check_box = QCheckBox("activate")
        # name
        widget.scrap_p_name_lab = QLabel('Name: ')
        widget.scrap_p_name_box = QLineEdit()
        widget.scrap_p_name_box.setMaximumWidth(200)
        # keywords
        widget.scrap_p_keywords_lab = QLabel('keywords: ')
        widget.scrap_p_keywords_box = QComboBox()
        # populate recoded choice
        refresh_keyword(widget.scrap_p_keywords_box)
        # project
        widget.scrap_p_project_lab = QLabel('Project: ')
        widget.scrap_p_project_box = QLineEdit()
        widget.scrap_p_project_box.setMaximumWidth(200)
        # database
        widget.scrap_p_database_lab = QLabel('Database: ')
        widget.scrap_p_database_box = QComboBox()
        # populate recorded choice
        refresh_database(widget.scrap_p_database_box)
        # options
        widget.scrap_p_option = QLabel("Options:")
        widget.scrap_check_box_rt = QCheckBox("Retweet")
        widget.scrap_check_box_like = QCheckBox("Like")
        widget.scrap_check_box_anon = QCheckBox("make anonymous data")

        widget.scrap_p_lab_api = QLabel("Twitter API: ")
        # key
        widget.scrap_p_APIT_key_lab = QLabel('Key: ')
        widget.scrap_p_APIT_key_box = QLineEdit()
        widget.scrap_p_APIT_key_box.setMaximumWidth(200)
        # secret
        widget.scrap_p_APIT_secret_lab = QLabel('Secret: ')
        widget.scrap_p_APIT_secret_box = QLineEdit()
        widget.scrap_p_APIT_secret_box.setMaximumWidth(200)
        widget.scrap_p_APIT_secret_box.setEchoMode(QLineEdit.Password)
        # token
        widget.scrap_p_APIT_token_lab = QLabel('Token: ')
        widget.scrap_p_APIT_token_box = QLineEdit()
        widget.scrap_p_APIT_token_box.setMaximumWidth(200)
        # secret token
        widget.scrap_p_APIT_token_sec_lab = QLabel('Token secret: ')
        widget.scrap_p_APIT_token_sec_box = QLineEdit()
        widget.scrap_p_APIT_token_sec_box.setMaximumWidth(200)
        widget.scrap_p_APIT_token_sec_box.setEchoMode(QLineEdit.Password)

        widget.scrap_p_lab_spec = QLabel("Settings: ")
        # language
        widget.scrap_p_lang = QComboBox()
        widget.scrap_p_lang_lab = QLabel('Lang: ')
        widget.scrap_p_lang.addItem("fr")
        widget.scrap_p_lang.addItem("en")
        widget.scrap_p_lang.addItem("de")
        widget.scrap_p_lang.addItem("es")
        widget.scrap_p_lang.addItem("it")
        # interval
        widget.scrap_p_APIT_interval_lab = QLabel('Interval: ')
        widget.scrap_p_APIT_interval_box = QLineEdit()
        widget.scrap_p_APIT_interval_box.setMaximumWidth(200)
        # rate
        widget.scrap_p_APIT_rate_lab = QLabel('Rate limit: ')
        widget.scrap_p_APIT_rate_box = QLineEdit()
        widget.scrap_p_APIT_rate_box.setMaximumWidth(200)
        # test n save
        widget.scrap_valid_p = QPushButton("Check")

        # scraper content
        try:
            file, test0, test1, test2, test3, test4, test5, test6, test7, test8, test9, test10 = \
                True, ct.name, ct.keywords, ct.project, ct.database, ct.key_api, ct.secret_api, ct.token_api, \
                ct.token_secret_api, ct.lang, ct.interval, ct.rate
        except AttributeError:
            file = False
        if file:
            widget.scrap_check_box.setChecked(ct.active)
            widget.scrap_p_name_box.setText(ct.name)
            widget.scrap_p_keywords_box.setCurrentText(ct.keywords)
            widget.scrap_p_project_box.setText(ct.project)
            widget.scrap_p_database_box.setCurrentText(ct.database)
            widget.scrap_p_APIT_key_box.setText(ct.key_api)
            widget.scrap_p_APIT_secret_box.setText(ct.secret_api)
            widget.scrap_p_APIT_token_box.setText(ct.token_api)
            widget.scrap_p_APIT_token_sec_box.setText(ct.token_secret_api)
            widget.scrap_check_box_rt.setChecked(ct.retweet)
            widget.scrap_check_box_like.setChecked(ct.like)
            widget.scrap_check_box_anon.setChecked(ct.anonymous)
            widget.scrap_p_lang.setCurrentText(ct.lang)
            widget.scrap_p_APIT_interval_box.setText(ct.interval)
            widget.scrap_p_APIT_rate_box.setText(ct.rate)
        else:
            widget.scrap_p_name_box.setPlaceholderText("Record ID")
            widget.scrap_p_project_box.setPlaceholderText("Project ID")
            widget.scrap_p_APIT_key_box.setPlaceholderText("xxx")
            widget.scrap_p_APIT_secret_box.setPlaceholderText("xxx")
            widget.scrap_p_APIT_token_box.setPlaceholderText("xxx")
            widget.scrap_p_APIT_token_sec_box.setPlaceholderText("xxx")
            widget.scrap_p_APIT_interval_box.setPlaceholderText("900")
            widget.scrap_p_APIT_rate_box.setPlaceholderText("450")

        if widget.scrap_check_box.isChecked():
            ACTIVE_LAUNCH.append(nb)

        # add
        widget.layout.addWidget(widget.scrap_check_box, 0, 0, 1, 1)
        widget.layout.addWidget(widget.scrap_p_name_lab, 1, 0, 1, 1)
        widget.layout.addWidget(widget.scrap_p_name_box, 1, 1, 1, 1)
        widget.layout.addWidget(widget.scrap_p_keywords_lab, 2, 0, 1, 1)
        widget.layout.addWidget(widget.scrap_p_keywords_box, 2, 1, 1, 1)
        widget.layout.addWidget(widget.scrap_p_project_lab, 3, 0, 1, 1)
        widget.layout.addWidget(widget.scrap_p_project_box, 3, 1, 1, 1)
        widget.layout.addWidget(widget.scrap_p_database_lab, 4, 0, 1, 1)
        widget.layout.addWidget(widget.scrap_p_database_box, 4, 1, 1, 1)
        widget.layout.addWidget(widget.scrap_p_option, 5, 0, 1, 1)
        widget.layout.addWidget(widget.scrap_check_box_rt, 5, 1)
        widget.layout.addWidget(widget.scrap_check_box_like, 6, 1)
        widget.layout.addWidget(widget.scrap_check_box_anon, 7, 1)
        widget.layout.addWidget(widget.scrap_p_lab_api, 0, 2, 1, 1)
        widget.layout.addWidget(widget.scrap_p_APIT_key_lab, 1, 2, 1, 1)
        widget.layout.addWidget(widget.scrap_p_APIT_key_box, 1, 3, 1, 1)
        widget.layout.addWidget(widget.scrap_p_APIT_secret_lab, 2, 2, 1, 1)
        widget.layout.addWidget(widget.scrap_p_APIT_secret_box, 2, 3, 1, 1)
        widget.layout.addWidget(widget.scrap_p_APIT_token_lab, 3, 2, 1, 1)
        widget.layout.addWidget(widget.scrap_p_APIT_token_box, 3, 3, 1, 1)
        widget.layout.addWidget(widget.scrap_p_APIT_token_sec_lab, 4, 2, 1, 1)
        widget.layout.addWidget(widget.scrap_p_APIT_token_sec_box, 4, 3, 1, 1)
        widget.layout.addWidget(widget.scrap_p_lang_lab, 5, 2, 1, 1)
        widget.layout.addWidget(widget.scrap_p_lang, 5, 3, 1, 1)
        widget.layout.addWidget(widget.scrap_p_APIT_interval_lab, 6, 2, 1, 1)
        widget.layout.addWidget(widget.scrap_p_APIT_interval_box, 6, 3, 1, 1)
        widget.layout.addWidget(widget.scrap_p_APIT_rate_lab, 7, 2, 1, 1)
        widget.layout.addWidget(widget.scrap_p_APIT_rate_box, 7, 3, 1, 1)
        widget.layout.addWidget(widget.scrap_valid_p, 8, 1, 1, 2)

        # connect
        widget.scrap_valid_p.clicked.connect(partial(self.chk_n_save_scp, widget, named))
        widget.scrap_check_box.clicked.connect(partial(self.launch_update, widget, nb))

        # tab
        self.p_s_tab.setTabText(nb - 1, f"Profile {str(nb)}")
        widget.setLayout(widget.layout)

    def launch_update(self, widget, nb):
        if widget.scrap_check_box.isChecked():
            ACTIVE_LAUNCH.append(nb)
        else:
            ACTIVE_LAUNCH.remove(nb)

    # check api connection parameters and save file
    def chk_n_save_scp(self, widget, name):
        save = 0
        # api connexion
        key, secret = widget.scrap_p_APIT_key_box.text(), widget.scrap_p_APIT_secret_box.text()
        token, token_secret = widget.scrap_p_APIT_token_box.text(), widget.scrap_p_APIT_token_sec_box.text()
        value = [widget.scrap_p_name_box.text(),
                 widget.scrap_p_project_box.text(),
                 widget.scrap_p_APIT_interval_box.text(),
                 widget.scrap_p_APIT_rate_box.text()]
        # test api connexion
        try:
            auth = tweepy.OAuthHandler(key, secret)
            auth.set_access_token(token, token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)
            check_api_twitter_connexion(api)
            # content text:
            try:
                for e in range(len(value)):
                    if not value[e]:
                        raise SystemExit
                save = 1
            except SystemExit:
                self.error_box.setWindowTitle("Setup failed")
                self.error_box.showMessage("Missing parameters!")
        except SystemExit:
            self.error_box.setWindowTitle("Setup failed")
            self.error_box.showMessage("Parameters failed to establish a connection to Twitter!")
        # save

        if save:
            s_profile = SProfile(file_name=name, active=widget.scrap_check_box.isChecked(),
                                 name=widget.scrap_p_name_box.text(),
                                 keywords=widget.scrap_p_keywords_box.currentText(),
                                 project=widget.scrap_p_project_box.text(),
                                 database=widget.scrap_p_database_box.currentText(),
                                 key_api=widget.scrap_p_APIT_key_box.text(),
                                 secret_api=widget.scrap_p_APIT_secret_box.text(),
                                 token_api=widget.scrap_p_APIT_token_box.text(),
                                 token_secret_api=widget.scrap_p_APIT_token_sec_box.text(),
                                 retweet=widget.scrap_check_box_rt.isChecked(),
                                 like=widget.scrap_check_box_like.isChecked(),
                                 anonymous=widget.scrap_check_box_anon.isChecked(),
                                 lang=widget.scrap_p_lang.currentText(),
                                 interval=widget.scrap_p_APIT_interval_box.text(),
                                 rate=widget.scrap_p_APIT_rate_box.text())
            s_profile.save()
            QMessageBox.information(self, "Success", "Configuration saved successfully", QMessageBox.Yes,
                                    QMessageBox.Yes)

    # delete profile
    def dl_p_set(self):
        total = int(CONFIG.get("NbrProfil", 1))
        widget = eval(f"self.p{total}")
        if total <= 1:
            self.error_box.setWindowTitle("Unable to delete")
            self.error_box.showMessage("Unable to delete last tab!")
        else:
            for i in reversed(range(widget.layout.count())):
                to_remove = widget.layout.itemAt(i).widget()
                # remove it from the layout list
                widget.layout.removeWidget(to_remove)
                # remove it from the gui
                to_remove.setParent(None)
            widget.layout.deleteLater()
            self.p_s_tab.removeTab(total - 1)
            # parameter adjustment
            CONFIG['NbrProfil'] = total - 1
            cfg_p = os.path.join(CFG_DIR, "config")
            with open(cfg_p, "w") as file:
                file.write(f"NbrProfil\t{total - 1}\n")
                file.write(f"NbrDataSet\t{CONFIG['NbrDataSet']}\n")
            # delete parameter file
            if os.path.exists(os.path.join(PROFILE_DIR, f"P{total}.json")):
                os.remove(os.path.join(PROFILE_DIR, f"P{total}.json"))

    # new profile
    def nw_p_set(self):
        total = int(CONFIG.get("NbrProfil", 1))
        if total >= 8:
            self.error_box.setWindowTitle("Unable to add")
            self.error_box.showMessage("Cannot create more than 8 DataSet!")
        else:
            CONFIG["NbrProfil"] = total + 1
            configpath = os.path.join(CFG_DIR, "config")
            with open(configpath, "w") as file:
                file.write(f"NbrProfil\t{total + 1}\n")
                file.write(f"NbrDataSet\t{CONFIG['NbrDataSet']}\n")
            eval('self.p_s_tab.addTab(self.p' + str(total + 1) + ', "Profile ' + str(total + 1) + '")')
            widget = eval(f"self.p{total + 1}")
            self.psc_ui(widget, total + 1)

    # multi thread scrap
    def scrap(self):
        if False in STOP_THREADS:
            STOP_THREADS.append(True)
            STOP_THREADS.remove(False)
        self.scrap_btn_start.setEnabled(False)
        self.scrap_btn_stop.setEnabled(True)
        for n in range(len(ACTIVE_LAUNCH)):
            thread = eval(f"self.thread_{ACTIVE_LAUNCH[n]}")
            worker = eval(f"self.worker_{ACTIVE_LAUNCH[n]}")
            worker.moveToThread(thread)
            thread.started.connect(worker.scrap)
            worker.finished.connect(thread.quit)
            worker.finished.connect(self.stop_scrap)
            thread.start()

    # stop scrap
    def stop_scrap(self, success, msg):
        if True in STOP_THREADS:
            STOP_THREADS.append(False)
            STOP_THREADS.remove(True)
        self.scrap_btn_start.setEnabled(True)
        self.scrap_btn_stop.setEnabled(False)
        refresh_log(self.lw_view, self)
        if not success:
            self.error_box.setWindowTitle("Scrap failed")
            self.error_box.showMessage(f"""
                                        An error has occurred:\n
                                        {msg}
                                        """)

    # -------------------------------------------------------------------------------------------------------------------
    #                                              database
    # -------------------------------------------------------------------------------------------------------------------

    # init data tab
    def dtb_ui(self):
        # add
        self.layout_d.addWidget(self.dtb_tab, 0, 0, 1, 2)
        for tab in range(1, int(CONFIG.get('NbrDataSet', 1)) + 1):
            eval('self.dtb_tab.addTab(self.d' + str(tab) + ', "Data set ' + str(tab) + '")')
            widget = eval(f"self.d{tab}")
            self.pdt_ui(widget, tab)
        # parameters
        self.more_d.setText('+')
        self.more_d.setAutoRaise(True)
        self.less_d.setText('-')
        self.less_d.setAutoRaise(True)
        self.layout_rcd.setContentsMargins(0, 0, 0, 0)
        # add
        self.r_corner_d.setLayout(self.layout_rcd)
        self.layout_rcd.addWidget(self.more_d)
        self.layout_rcd.addWidget(self.less_d)
        self.dtb_tab.setCornerWidget(self.r_corner_d, QtCore.Qt.TopRightCorner)

        # tab parameters
        self.setTabText(1, "Database")
        self.dtb.setLayout(self.layout_d)

    # *************************************  database's methods  *******************************************************

    # generate profile tab for data page
    def pdt_ui(self, widget, nb):
        data = populate_dp()
        named = "D" + str(nb)
        ct = data.get(named, {})
        widget.layout = QGridLayout()
        # create
        widget.database_dbi = QLabel("Database settings: ")
        # host
        widget.dtb_host_lab = QLabel('Host address: ')
        widget.dtb_host_box = QLineEdit()
        widget.dtb_host_box.setMaximumWidth(400)
        # login
        widget.dtb_login_lab = QLabel('Login: ')
        widget.dtb_login_box = QLineEdit()
        widget.dtb_login_box.setMaximumWidth(400)
        # secret
        widget.dtb_secret_lab = QLabel('secret: ')
        widget.dtb_secret_box = QLineEdit()
        widget.dtb_secret_box.setMaximumWidth(400)
        widget.dtb_secret_box.setEchoMode(QLineEdit.Password)
        # bdd
        widget.dtb_bdd_lab = QLabel('Database: ')
        widget.dtb_bdd_box = QLineEdit()
        widget.dtb_bdd_box.setMaximumWidth(400)

        # QLineEdit content
        try:
            file, test0, test1, test2, test3 = True, ct.host, ct.login, ct.secret, ct.database
        except AttributeError:
            file = False
        if file:
            widget.dtb_host_box.setText(ct.host)
            widget.dtb_login_box.setText(ct.login)
            widget.dtb_bdd_box.setText(ct.database)
            widget.dtb_secret_box.setText(ct.secret)
        else:
            widget.dtb_host_box.setPlaceholderText("localhost")
            widget.dtb_bdd_box.setPlaceholderText("Database")
            widget.dtb_login_box.setPlaceholderText("admin")
            widget.dtb_secret_box.setPlaceholderText("xxx")

        # check button
        widget.dtb_valid = QPushButton("Check")

        # add
        widget.layout.addWidget(widget.database_dbi, 0, 0, 2, 2)
        widget.layout.addWidget(widget.dtb_bdd_lab, 1, 1, 1, 1)
        widget.layout.addWidget(widget.dtb_bdd_box, 1, 2, 1, 4)
        widget.layout.addWidget(widget.dtb_host_lab, 2, 1, 1, 1)
        widget.layout.addWidget(widget.dtb_host_box, 2, 2, 1, 4)
        widget.layout.addWidget(widget.dtb_login_lab, 3, 1, 1, 1)
        widget.layout.addWidget(widget.dtb_login_box, 3, 2, 1, 4)
        widget.layout.addWidget(widget.dtb_secret_lab, 4, 1, 1, 1)
        widget.layout.addWidget(widget.dtb_secret_box, 4, 2, 1, 4)
        widget.layout.addWidget(widget.dtb_valid, 5, 2, 2, 3)

        # connect
        widget.dtb_valid.clicked.connect(partial(self.chk_n_save, widget, named))

        # tab
        self.dtb_tab.setTabText(nb - 1, "Settings " + str(nb))
        widget.setLayout(widget.layout)

    # check database connection parameters and save file
    def chk_n_save(self, widget, name):
        # Postgres connexion
        database, host = widget.dtb_bdd_box.text(), widget.dtb_host_box.text()
        user, password = widget.dtb_login_box.text(), widget.dtb_secret_box.text()
        try:
            c = connect_bdd(host, database, user, password)
            cur = create_cursor(c)
            save = 0
            cur.execute(DATAS_CHECK_TABLE)
            test = cur.fetchone()
            # tab checking
            if not test[0]:
                question = QMessageBox.question(self, 'Missing table', 'Do you want to create the messages table? ',
                                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if question == QMessageBox.Yes:
                    save = 1
                    cur.execute(DATAS_TEMPLATE)
                    c.commit()
            else:
                # attribute checking
                for element in DATAS_A_LIST:
                    attrib = element
                    cur.execute(f"""
                                SELECT TRUE
                                FROM   pg_attribute
                                WHERE  attrelid = 'messages'::regclass
                                AND    attname =  '{attrib}'
                                AND    NOT attisdropped;
                    """)
                    test = cur.fetchone()
                    if test != (True,):
                        question = QMessageBox.question(self, 'Wrong table',
                                                        'Selected table does not match, reformat it? (data erased)',
                                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                        if question == QMessageBox.Yes:
                            save = 1
                            cur.execute("DROP TABLE messages;")
                            c.commit()
                            cur.execute(DATAS_TEMPLATE)
                            c.commit()
                        break
                    else:
                        save = 1
            # file
            if save:
                data = Dataps(name=name, database=database, host=host, login=user, secret=password)
                data.save()
                for i in range(int(CONFIG.get("NbrProfil", 1))):
                    widget = eval(f"self.p{i + 1}.scrap_p_database_box")
                    refresh_database(widget)
                QMessageBox.information(self, "Success", "Configuration saved successfully", QMessageBox.Yes,
                                        QMessageBox.Yes)
            else:
                raise SystemExit
        except SystemExit:
            self.error_box.setWindowTitle("Setup failed")
            self.error_box.showMessage("Parameters failed to establish a connection to the database!")

    # remove last tab
    def dl_dt_set(self):
        total = int(CONFIG.get("NbrDataSet", 1))
        widget = eval(f"self.d{total}")
        if total <= 1:
            self.error_box.setWindowTitle("Unable to delete")
            self.error_box.showMessage("Unable to delete last tab!")
        else:
            for i in reversed(range(widget.layout.count())):
                to_remove = widget.layout.itemAt(i).widget()
                # remove it from the layout list
                widget.layout.removeWidget(to_remove)
                # remove it from the gui
                to_remove.setParent(None)
            widget.layout.deleteLater()
            self.dtb_tab.removeTab(total - 1)
            # parameter adjustment
            CONFIG['NbrDataSet'] = total - 1
            cfg_p = os.path.join(CFG_DIR, "config")
            with open(cfg_p, "w") as file:
                file.write(f"NbrProfil\t{CONFIG['NbrProfil']}\n")
                file.write(f"NbrDataSet\t{total - 1}\n")
            # delete parameter file
            if os.path.exists(os.path.join(DATAS_DIR, f"D{total}.json")):
                os.remove(os.path.join(DATAS_DIR, f"D{total}.json"))
                for i in range(int(CONFIG.get("NbrProfil", 1))):
                    widget = eval(f"self.p{i + 1}.scrap_p_database_box")
                    refresh_database(widget)

    def nw_dt_set(self):
        total = int(CONFIG.get("NbrDataSet", 1))
        if total >= 8:
            self.error_box.setWindowTitle("Unable to add")
            self.error_box.showMessage("Cannot create more than 8 DataSet!")
        else:
            CONFIG['NbrDataSet'] = total + 1
            config_path = os.path.join(CFG_DIR, "config")
            with open(config_path, "w") as file:
                file.write(f"NbrProfil\t{CONFIG['NbrProfil']}\n")
                file.write(f"NbrDataSet\t{total + 1}\n")
            cmd = 'self.dtb_tab.addTab(self.d' + str(total + 1) + ', "Data set ' + str(total + 1) + '")'
            eval(cmd)
            widget = eval(f"self.d{total + 1}")
            self.pdt_ui(widget, total + 1)

    # -------------------------------------------------------------------------------------------------------------------
    #                                          keywords
    # -------------------------------------------------------------------------------------------------------------------

    def kw_ui(self):  # create interface for keywords page
        # add
        self.layout_k.addWidget(self.btn_create_keywords, 0, 0)
        self.layout_k.addWidget(self.btn_import_keywords, 0, 1)
        self.layout_k.addWidget(self.lw_notes, 1, 0, 10, 2)
        self.layout_k.addWidget(self.btn_export_keywords, 10, 0)
        self.layout_k.addWidget(self.btn_del_keywords, 10, 1)
        self.layout_k.addWidget(self.content, 0, 2, 11, 80)
        # tab
        self.setTabText(2, "Keywords")
        self.kw.setLayout(self.layout_k)

    # *************************************  keywords' methods  *******************************************************

    def populate_notes(self):
        keywords = get_keywords()
        for keyword in keywords:
            self.add_kw_to_lw(keyword)

    def add_kw_to_lw(self, keyword):
        lw_item = QListWidgetItem(keyword.title)
        lw_item.keyword = keyword
        self.lw_notes.addItem(lw_item)

    def create_keywords(self):
        title, result = QInputDialog.getText(self, "Create a keywords list", "Title: ")
        if result and title:
            keyword = Keywords(title=title)
            keyword.save()
            self.add_kw_to_lw(keyword)
        for i in range(int(CONFIG.get("NbrProfil", 1))):
            widget = eval(f"self.p{i + 1}.scrap_p_keywords_box")
            refresh_keyword(widget)

    def delete_selected_note(self):
        selected_item = self.get_selected_lw_item()
        if selected_item:
            result = selected_item.keyword.delete()
            if result:
                self.lw_notes.takeItem(self.lw_notes.row(selected_item))
        for i in range(int(CONFIG.get("NbrProfil", 1))):
            widget = eval(f"self.p{i + 1}.scrap_p_keywords_box")
            refresh_keyword(widget)

    def get_selected_lw_item(self):
        selected_items = self.lw_notes.selectedItems()
        if selected_items:
            return selected_items[0]
        return None

    def populate_note_content(self):
        selected_item = self.get_selected_lw_item()
        if selected_item:
            self.content.setText(selected_item.keyword.content)
        else:
            self.content.clear()

    def save_note(self):
        selected_item = self.get_selected_lw_item()
        if selected_item:
            selected_item.keyword.content = self.content.toPlainText()
            selected_item.keyword.save()

    # create a new kw list from a txt file
    def import_keywords(self):
        window = QFileDialog(self)
        window.setMimeTypeFilters(["text/txt"])
        window.setDirectory(KEYWORDS_DIR)
        if window.exec_() == QDialog.Accepted:
            file = window.selectedUrls()[0]
            title = str(file).rsplit("/")[-1].split(".")[0]
            with open(str(file)[29:-2:], "r") as exp:
                c = exp.read()
            keyword = Keywords(title=title[:-2], content=c)
            keyword.save()
            self.add_kw_to_lw(keyword)
        else:
            pass

    # create and write save files
    def export_keywords(self):
        selected_item = self.get_selected_lw_item()
        if selected_item:
            window = QFileDialog(self)
            window.setMimeTypeFilters(["text/txt"])
            window.setDirectory(KEYWORDS_DIR)
            if window.exec_() == QDialog.Accepted:
                file = window.selectedUrls()[0]
                if file:
                    dr = str(file)
                    with open(dr[29:-2:], "w") as exp:
                        exp.write(f"{selected_item.keyword.content}")
                # if cancel
                else:
                    pass
        # no selected
        else:
            pass

    # -------------------------------------------------------------------------------------------------------------------
    #                                          logs
    # -------------------------------------------------------------------------------------------------------------------

    def logs_ui(self):
        # create
        self.log_error_box.setPlaceholderText("ErrorType")
        self.log_error_box.setMaximumWidth(500)
        self.log_contrib_box.setPlaceholderText("Contributor")
        self.log_db_box.setPlaceholderText("Database")
        self.log_name_box.setPlaceholderText("John Doe")
        self.log_date_box.setPlaceholderText("date")
        self.log_like_box.setPlaceholderText("0")
        self.log_retweet_box.setPlaceholderText("0")

        # add
        self.layout.addWidget(self.lw_view, 0, 0, 9, 2)
        self.layout.addWidget(self.btn_clear, 9, 0, 1, 1)
        self.layout.addWidget(self.btn_clear_all, 9, 1, 1, 1)
        self.layout.addWidget(self.log_error_lab, 0, 2, 1, 1)
        self.layout.addWidget(self.log_error_box, 0, 3, 1, 6)
        self.layout.addWidget(self.log_contrib_lab, 1, 2, 1, 1)
        self.layout.addWidget(self.log_contrib_box, 1, 3, 1, 2)
        self.layout.addWidget(self.log_db_lab, 1, 6, 1, 1)
        self.layout.addWidget(self.log_db_box, 1, 7, 1, 2)
        self.layout.addWidget(self.log_name_lab, 2, 2, 1, 1)
        self.layout.addWidget(self.log_name_box, 2, 3, 1, 6)
        self.layout.addWidget(self.log_message_lab, 3, 2, 1, 1)
        self.layout.addWidget(self.log_message, 3, 3, 4, 6)
        self.layout.addWidget(self.log_date_lab, 7, 2, 1, 1)
        self.layout.addWidget(self.log_date_box, 7, 3, 1, 2)
        self.layout.addWidget(self.log_like_lab, 8, 2, 1, 1)
        self.layout.addWidget(self.log_like_box, 8, 3, 1, 2)
        self.layout.addWidget(self.log_retweet_lab, 8, 6, 1, 1)
        self.layout.addWidget(self.log_retweet_box, 8, 7, 1, 2)
        self.layout.addWidget(self.btn_rec_log, 9, 8, 1, 1)
        # tab
        self.setTabText(3, "Logs")
        self.logs.setLayout(self.layout)

    # *************************************  logs' methods  *******************************************************

    def populate_log(self):
        logs = get_logs()
        for log in logs:
            self.add_log_to_lw(log)

    def add_log_to_lw(self, log):
        lw_item = QListWidgetItem(log.uuid)
        lw_item.log = log
        self.lw_view.addItem(lw_item)

    def populate_log_content(self):
        selected_item = self.get_selected_log_item()
        if selected_item:
            self.log_error_box.setText(selected_item.log.error)
            self.log_contrib_box.setText(selected_item.log.contributor)
            self.log_db_box.setText(selected_item.log.database)
            self.log_name_box.setText(selected_item.log.name)
            self.log_message.setText(selected_item.log.content)
            self.log_date_box.setText(selected_item.log.date)
            self.log_like_box.setText(selected_item.log.like)
            self.log_retweet_box.setText(selected_item.log.retweet)
        else:
            self.log_error_box.clear()
            self.log_contrib_box.clear()
            self.log_db_box.clear()
            self.log_name_box.clear()
            self.log_message.clear()
            self.log_date_box.clear()
            self.log_like_box.clear()
            self.log_retweet_box.clear()

    def get_selected_log_item(self):
        selected_items = self.lw_view.selectedItems()
        if selected_items:
            return selected_items[0]
        return None

    def del_log(self):
        selected_item = self.get_selected_log_item()
        if selected_item:
            result = selected_item.log.delete()
            if result:
                self.lw_view.takeItem(self.lw_view.row(selected_item))

    def del_all_log(self):
        for i in range(self.lw_view.count()-1, -1, -1):
            item = self.lw_view.item(i)
            if item:
                result = item.log.delete()
                if result:
                    self.lw_view.takeItem(self.lw_view.row(item))

    def rec_log(self):
        db = f"D{self.log_db_box.text()[0]}"
        c_db = populate_dp().get(db, {})
        if not c_db:
            self.error_box.setWindowTitle("Database failure")
            self.error_box.showMessage("The database does not seem to exist!")
        else:
            # try to connect to db
            try:
                c = connect_bdd(c_db.host, c_db.database, c_db.login, c_db.secret)
                cur = create_cursor(c)
                cur.execute(f"""
                            INSERT INTO messages (contributor, username, content, date, retweets, likes)
                                VALUES ('{str(self.log_contrib_box.text())}', '{str(self.log_name_box.text())}',
'{str(self.log_message.toPlainText())}', '{str(self.log_date_box.text())}','{str(self.log_retweet_box.text())}',
'{str(self.log_like_box.text())}')
                            """)
                c.commit()
                self.del_log()
            except psycopg2.Error:
                self.error_box.setWindowTitle("Database failure")
                self.error_box.showMessage("database settings are not correct")
        QMessageBox.information(self, "success!", "recording completed", QMessageBox.Yes, QMessageBox.Yes)

    # -------------------------------------------------------------------------------------------------------------------
    #                                          info
    # -------------------------------------------------------------------------------------------------------------------

    def info_ui(self):
        self.title.setText("""
            Uscrap2gather
            
            is a program to easily scrape Twitter posts using API
            you will need a psql database as well as a developer account on Twitter
            
            psql:
            https://www.postgresql.org/
            
            Twitter Dev Portal:
            https://developer.twitter.com/en"
            
            source code:
            https://github.com/MickaelDP/UScrap2Gather
            
            General Public License: GNU GPLv3
            https://www.gnu.org/licenses/gpl-3.0.htmlé
            
            icon:
            https://www.flaticon.com/authors/eucalyp
            
            """)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        # add
        self.layout_in.addWidget(self.title, 0, 0, 1, 10)
        # tab
        self.setTabText(4, "Infos")
        self.info.setLayout(self.layout_in)
