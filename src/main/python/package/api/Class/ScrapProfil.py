import os
import json
from glob import glob

from package.api.constants import PROFILE_DIR


def get_s_profile():
    profile_d = {}
    files = glob(os.path.join(PROFILE_DIR, "*.json"))
    for file in files:
        with open(file, "r") as f:
            s_data = json.load(f)
            s_file_name = os.path.splitext(os.path.basename(file))[0]
            s_active = s_data.get("active")
            s_name = s_data.get("name")
            s_keywords = s_data.get("keywords")
            s_project = s_data.get("project")
            s_database = s_data.get("database")
            s_key_api = s_data.get("key_api")
            s_secret_api = s_data.get("secret_api")
            s_token_api = s_data.get("token_api")
            s_token_secret_api = s_data.get("token_secret_api")
            s_retweet = s_data.get("retweet")
            s_like = s_data.get("like")
            s_anonymous = s_data.get("anonymous")
            s_lang = s_data.get("lang")
            s_interval = s_data.get("interval")
            s_rate = s_data.get("rate")
            s_profile = SProfile(file_name=s_file_name, active=s_active, name=s_name, keywords=s_keywords,
                                 project=s_project, database=s_database, key_api=s_key_api, secret_api=s_secret_api,
                                 token_api=s_token_api, token_secret_api=s_token_secret_api, retweet=s_retweet,
                                 like=s_like, anonymous=s_anonymous, lang=s_lang, interval=s_interval,
                                 rate=s_rate)
            profile_d[s_profile.file_name] = s_profile
    return profile_d


class SProfile:
    def __init__(self, file_name="", active="", name="", keywords="", project="", database="", key_api="",
                 secret_api="", token_api="", token_secret_api="", retweet="", like="", anonymous="", lang="",
                 interval="", rate=""):
        self.file_name = file_name
        self.active = active
        self.name = name
        self.keywords = keywords
        self.project = project
        self.database = database
        self.key_api = key_api
        self.secret_api = secret_api
        self.token_api = token_api
        self.token_secret_api = token_secret_api
        self.retweet = retweet
        self.like = like
        self.anonymous = anonymous
        self.lang = lang
        self.interval = interval
        self.rate = rate

    # representation for dev
    def __repr__(self):
        return f"{self.file_name}, {self.active}, {self.name}, {self.keywords}, {self.project}, {self.database}," \
               f"{self.key_api}, {self.secret_api}, {self.token_api}, ({self.token_secret_api}, {self.retweet}," \
               f" {self.like}, {self.anonymous}, {self.interval}, {self.rate})"

    def delete(self):
        os.remove(self.path)
        if os.path.exists(self.path):
            return False
        return True

    @property
    def path(self):
        return os.path.join(PROFILE_DIR, self.file_name + ".json")

    def save(self):
        if not os.path.exists(PROFILE_DIR):
            os.makedirs(PROFILE_DIR)
        data = {"file_name": self.file_name,
                "active": self.active,
                "name": self.name,
                "keywords": self.keywords,
                "project": self.project,
                "database": self.database,
                "key_api": self.key_api,
                "secret_api": self.secret_api,
                "token_api": self.token_api,
                "token_secret_api": self.token_secret_api,
                "retweet": self.retweet,
                "like": self.like,
                "anonymous": self.anonymous,
                "lang": self.lang,
                "interval": self.interval,
                "rate": self.rate}
        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)


if __name__ == '__main__':
    profile = get_s_profile()
    print(profile)
