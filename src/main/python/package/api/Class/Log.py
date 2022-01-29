import os
import json
from uuid import uuid4
from glob import glob

from package.api.constants import LOG_DIR


def get_logs():
    logs_list = []
    files = glob(os.path.join(LOG_DIR, "*.json"))
    for file in files:
        with open(file, "r") as f:
            l_data = json.load(f)
            l_uuid = os.path.splitext(os.path.basename(file))[0]
            l_error = l_data.get("error")
            l_contributor = l_data.get("contributor")
            l_database = l_data.get("database")
            l_name = l_data.get("name")
            l_content = l_data.get("content")
            l_date = l_data.get("date")
            l_like = l_data.get("like")
            l_retweet = l_data.get("retweet")
            log = Logs(uuid=l_uuid, error=l_error, contributor=l_contributor, database=l_database, name=l_name,
                       content=l_content, date=l_date, like=l_like, retweet=l_retweet)
            logs_list.append(log)
    return logs_list


class Logs:
    def __init__(self, uuid=None, error="", contributor="", database="", name="", content="", date="", like="",
                 retweet=""):
        if uuid:
            self.uuid = uuid
        else:
            self.uuid = str(uuid4())
        self.error = error
        self.contributor = contributor
        self.database = database
        self.name = name
        self.content = content
        self.date = date
        self.like = like
        self.retweet = retweet

    def __repr__(self):
        return f"{self.error}, {self.contributor}, {self.database}, {self.name}, {self.content}, {self.date}, " \
               f"{self.like}, {self.retweet}, ({self.uuid})"

    def __str__(self):
        return f"{self.error}, {self.contributor}, {self.database}, {self.name}, {self.content}, {self.date}, " \
               f"{self.like}, {self.retweet}"

    # private attribute _*
    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if isinstance(value, str):
            self._content = value
        else:
            raise TypeError("Wrong value: Please enter a character string!")

    # use of method without ()
    @property
    def path(self):
        return os.path.join(LOG_DIR, self.uuid + ".json")

    def delete(self):
        os.remove(self.path)
        if os.path.exists(self.path):
            return False
        return True

    def save(self):
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        data = {"uuid": self.uuid,
                "error": self.error,
                "contributor": self.contributor,
                "database": self.database,
                "name": self.name,
                "content": self.content,
                "date": self.date,
                "like": self.like,
                "retweet": self.retweet}
        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)


if __name__ == '__main__':
    logs = get_logs()
    print(logs)
