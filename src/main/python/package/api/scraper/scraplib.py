import psycopg2
import sys
import tweepy
import re
from uuid import uuid4
from package.api.Class.Log import Logs


# connected to the BDD
def connect_bdd(host, database, user, password):
    try:
        c = psycopg2.connect("host=%s dbname=%s user=%s password=%s" % (host, database, user, password))
    except (psycopg2.DatabaseError, psycopg2.OperationalError, SyntaxError):
        sys.exit(2)
    return c


# cursor on BDD
def create_cursor(con):
    try:
        cur = con.cursor()
    except NameError:
        sys.exit(2)
    return cur


# connected to the API?
def check_api_twitter_connexion(api):
    try:
        api.verify_credentials()
    except (TypeError, SystemExit, tweepy.TweepyException):
        sys.exit(1)


# checks if the configuration respects the limitation
def check_rate(elements, interval, limit):
    return ((900.0/interval) * elements) <= limit


# search and registration request
def scrap(keywords, api, profile, c, cur, db):
    for element in keywords:
        try:
            for tweet in api.search_tweets(q=element, lang=profile.lang, result_type='recent', count=100,
                                           tweet_mode='extended'):
                tweetsafe = clean_tweet(tweet)
                if tweetsafe != "NoRt0":
                    cur.execute(f"""
                                    SELECT count(*) FROM messages
                                    WHERE content LIKE '{tweetsafe}%';
                                """)
                    duplicate_test = cur.fetchone()
                    if duplicate_test[0] == 0:
                        scrap_record(profile, c, cur, tweet, tweetsafe, db)
        except tweepy.TweepyException:
            sys.exit(1)


def scrap_record(profile, c, cur, tweet, tweetsafe, db):
    attributes = cat_at(profile)
    values = cat_val(profile, tweet, tweetsafe)
    try:
        cur.execute(f"INSERT INTO messages {attributes} VALUES {values}")
        c.commit()
    except (psycopg2.DatabaseError, psycopg2.OperationalError,  NameError) as e:
        log = Logs(uuid=str(uuid4()),
                   error=str(e),
                   contributor=f"{profile.project}.{profile.name}",
                   database=db.database,
                   name=str(tweet.user.name),
                   content=tweetsafe,
                   date=str(tweet.created_at),
                   like=str(tweet.favorite_count),
                   retweet=str(tweet.retweet_count))
        log.save()
        c.rollback()
    except tweepy.TweepyException as e:
        log = Logs(uuid=str(uuid4()),
                   error=str(e),
                   contributor=f"{profile.project}.{profile.name}",
                   database=db.database,
                   name=str(tweet.user.name),
                   content=tweetsafe,
                   date=str(tweet.created_at),
                   like=str(tweet.favorite_count),
                   retweet=str(tweet.retweet_count))
        log.save()
        sys.exit(1)
    except SystemExit as e:
        log = Logs(uuid=str(uuid4()),
                   error=str(e),
                   contributor=f"{profile.project}.{profile.name}",
                   database=db.database,
                   name=str(tweet.user.name),
                   content=tweetsafe,
                   date=str(tweet.created_at),
                   like=str(tweet.favorite_count),
                   retweet=str(tweet.retweet_count))
        log.save()
        sys.exit(6)


# pre-record cleaning
def clean_tweet(tweet):
    result = ""
    if hasattr(tweet, 'retweeted_status'):
        result = "NoRt0"
    else:
        tweetsafe = tweet.full_text.replace("\n", "")
        tweetsafe = tweetsafe.replace("'", "''")
        for word in tweetsafe.split():
            if remove_at(word):
                result = result + word + " "
    return result[0: -1]


# cleaning functions
def remove_at(mot):
    # mail, url or @user
    pattern = r'.*@.*\..{3,4}'
    mail_regex = re.compile(pattern)
    if mot.startswith('@') \
       or mot.startswith("http") \
       or re.fullmatch(mail_regex, mot):
        r = False
    else:
        r = True
    return r


# construction of attributes
def cat_at(profile):
    attributes = "(contributor, username, content, date"
    if profile.retweet:
        attributes += ", retweets"
    if profile.like:
        attributes += ", likes"
    attributes += ")"
    return attributes


# construction of values
def cat_val(profile, tweet, tweetsafe):
    values = f"('{profile.project}.{profile.name}'"
    if profile.anonymous:
        values += f", '{str(uuid4())[:10]}'"
    else:
        values += f", '{str(tweet.user.name)}'"
    values += f", '{tweetsafe}', '{tweet.created_at}'"
    if profile.retweet:
        values += f", '{tweet.retweet_count}'"
    if profile.like:
        values += f", '{tweet.favorite_count}'"
    values += ')'
    return values
