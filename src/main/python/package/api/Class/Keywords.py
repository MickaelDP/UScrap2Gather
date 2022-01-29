import os
import json
from uuid import uuid4
from glob import glob
from package.api.constants import KEYWORDS_DIR


def get_keywords():
    keywords = []
    files = glob(os.path.join(KEYWORDS_DIR, "*.json"))
    for file in files:
        with open(file, "r") as f:
            k_data = json.load(f)
            k_uuid = os.path.splitext(os.path.basename(file))[0]
            k_title = k_data.get("title")
            k_content = k_data.get("content")
            keyword = Keywords(uuid=k_uuid, title=k_title, content=k_content)
            keywords.append(keyword)
    return keywords


class Keywords:
    def __init__(self, title="", content="", uuid=None):
        if uuid:
            self.uuid = uuid
        else:
            self.uuid = str(uuid4())
        self.title = title
        self.content = content

    # representation for dev
    def __repr__(self):
        return f"{self.title} ({self.uuid})"

    def __str__(self):
        return self.title

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

    def delete(self):
        os.remove(self.path)
        if os.path.exists(self.path):
            return False
        return True

    def save(self):
        if not os.path.exists(KEYWORDS_DIR):
            os.makedirs(KEYWORDS_DIR)
        data = {"title": self.title, "content": self.content}
        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)

    # use of method without ()
    @property
    def path(self):
        return os.path.join(KEYWORDS_DIR, self.uuid + ".json")


if __name__ == '__main__':
    keywords = get_keywords()
    print(keywords)
