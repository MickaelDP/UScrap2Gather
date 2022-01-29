import time

from package.api.Class.DataProfil import get_dataps
from package.api.Class.Keywords import get_keywords
from package.api.Class.ScrapProfil import get_s_profile
from package.api.scraper.scraplib import *

from package.api.constants import STOP_THREADS

# **********************************************************************************************************#
#                                                    Main                                                   #
# **********************************************************************************************************#


def scraper(nb):
    # variable initialization
    profile_info = get_s_profile()[f"P{nb}"]
    database_info = get_dataps()[f"D{int(profile_info.database[0])}"]
    keywords_info = get_selected_kw(profile_info.keywords)

    t_interval = int(profile_info.interval)

    # API Twitter
    auth = tweepy.OAuthHandler(profile_info.key_api, profile_info.secret_api)
    auth.set_access_token(profile_info.token_api, profile_info.token_secret_api)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    check_api_twitter_connexion(api)

    # Psql connexion
    c = connect_bdd(database_info.host, database_info.database, database_info.login, database_info.secret)
    cur = create_cursor(c)

    # setting for interval
    start = round(time.time())
    modulo_start = start % t_interval

    # main loop
    print(f"thread {nb}: start")
    if not check_rate(len(keywords_info), t_interval, int(profile_info.rate)):
        sys.exit(5)
    else:
        while STOP_THREADS[0]:
            if round(time.time()) % t_interval == modulo_start:
                try:
                    scrap(keywords_info, api, profile_info, c, cur, database_info)
                    print(f"thread {nb}: new data")
                except KeyboardInterrupt:
                    return False
                except (tweepy.TweepyException, psycopg2.DatabaseError, psycopg2.OperationalError,  NameError):
                    return False
            else:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    return False
    # clean cursor
    try:
        c.close()
    except NameError:
        pass

    print(f"thread {nb}: stop")
    return True


# select the right list of keywords
def get_selected_kw(kw):
    for element in get_keywords():
        if element.title == kw:
            return element.content.split("\n")
