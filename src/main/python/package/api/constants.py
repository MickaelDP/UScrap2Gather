import os
from pathlib import Path
from package.api.constantslib import load_config

# profile to use for multithreading launcher
ACTIVE_LAUNCH = []
STOP_THREADS = [False]

# Initialize backup file tree in CFG_DIR if needed
CFG_DIR = os.path.join(Path.home(), ".scrap")
if not os.path.isdir(CFG_DIR):
    os.makedirs(CFG_DIR)

CONFIG = {}
load_config(CONFIG, 'config')
CONFIG["NbrProfil"] = int(CONFIG.get("NbrProfil", 1))
CONFIG["NbrDataSet"] = int(CONFIG.get("NbrDataSet", 1))

PROFILE_DIR = os.path.join(Path.home(), ".scrap/profil")
if not os.path.isdir(PROFILE_DIR):
    os.makedirs(PROFILE_DIR)

DATAS_DIR = os.path.join(Path.home(), ".scrap/datas")
if not os.path.isdir(DATAS_DIR):
    os.makedirs(DATAS_DIR)

KEYWORDS_DIR = os.path.join(Path.home(), ".scrap/kw")
if not os.path.isdir(KEYWORDS_DIR):
    os.makedirs(KEYWORDS_DIR)

LOG_DIR = os.path.join(Path.home(), ".scrap/log")
if not os.path.isdir(LOG_DIR):
    os.makedirs(LOG_DIR)

# this template is used to check the compliance of the database used
DATAS_TEMPLATE = """
    CREATE TABLE messages (
        id          SERIAL PRIMARY KEY,
        contributor VARCHAR(120) NOT NULL,
        username    VARCHAR(60) NOT NULL,
        content     TEXT NOT NULL,
        date        VARCHAR(30) NOT NULL,
        retweets    INT DEFAULT NULL,
        likes       INT DEFAULT NULL
    );   
"""

DATAS_A_LIST = ['id', 'contributor', 'username', 'content', 'date', 'retweets', 'likes']

DATAS_CHECK_TABLE = """
    SELECT EXISTS (
        SELECT FROM
            information_schema.tables
        WHERE
            table_schema Like 'public' AND
            table_type Like 'BASE TABLE' AND
            table_name = 'messages'
    );
"""
