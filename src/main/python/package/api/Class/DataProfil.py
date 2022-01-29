import os
import json
from glob import glob

from package.api.constants import DATAS_DIR


def get_dataps():
    dataps = {}
    files = glob(os.path.join(DATAS_DIR, "*.json"))
    for file in files:
        with open(file, "r") as f:
            d_data = json.load(f)
            d_name = os.path.splitext(os.path.basename(file))[0]
            d_database = d_data.get("database")
            d_host = d_data.get("host")
            d_login = d_data.get("login")
            d_secret = d_data.get("secret")
            datap = Dataps(name=d_name, database=d_database, host=d_host, login=d_login, secret=d_secret)
            dataps[datap.name] = datap
    return dataps


class Dataps:
    def __init__(self, database="", host="", login="", secret="", name=""):
        self.name = name
        self.database = database
        self.host = host
        self.login = login
        self.secret = secret

    # representation for dev
    def __repr__(self):
        return f"{self.database}, {self.host}, {self.login}, {self.secret}, ({self.name})"

    def delete(self):
        os.remove(self.path)
        if os.path.exists(self.path):
            return False
        return True

    @property
    def path(self):
        return os.path.join(DATAS_DIR, self.name + ".json")

    def save(self):
        if not os.path.exists(DATAS_DIR):
            os.makedirs(DATAS_DIR)
        data = {"name": self.name,
                "database": self.database,
                "host": self.host,
                "login": self.login,
                "secret": self.secret}
        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)


if __name__ == '__main__':
    dataps = get_dataps()
    print(dataps)
