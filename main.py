import ctypes
import os
import re
import shutil
import sqlite3
import time

import praw
import requests

import config


class ImageScrapper:
    path = os.path.join(os.path.dirname(__file__) + '\img\\')
    conn = sqlite3.connect('data.sqlite', check_same_thread=False)
    cur = conn.cursor()

    def __init__(self, subreddit):
        self.r = praw.Reddit(username=config.username, password=config.password, client_id=config.client_id,
                             client_secret=config.client_secret, user_agent="Nithishbn's ImageScrapper")
        self.subreddit = subreddit

    def scrap(self, requested):
        subreddit = self.r.subreddit(self.subreddit)
        count = 0
        urls = []
        ids = []
        # urlcount = 1

        for submission in subreddit.top('month'):
            title = submission.title
            url = submission.url
            submissionid = submission.id
            ids.append(submissionid)
            height = 1080
            width = 1920
            fileName = re.findall("(?:com|it|net).*/(.*[(jpg),(png)]$)", url)
            if ('.jpg' or '.png' in url) and len(fileName) != 0:
                print(url)
                if (submission.preview['images'][0]['source']['height'] / submission.preview['images'][0]['source'][
                    'width']) == (height / width):
                    # urls.append(submission.url)
                    print("Downloading {} of {}".format(count + 1, requested))
                    self.cur.execute('''INSERT OR IGNORE INTO main.main VALUES (?,?,?,?,?) ''',
                                     (submissionid, url, title, 0, 0))
                    submissionid = self.cur.execute('''SELECT id FROM main WHERE image=?''', (url,)).fetchall()[0][0]
                    if len(fileName) == 0:
                        self.cur.execute('''DELETE FROM main WHERE main.image=?''', (url,))

                    else:
                        response = requests.get(url, stream=True)
                        actualPath = self.path + fileName[0]
                        self.cur.execute('''UPDATE OR IGNORE main SET path=? WHERE id=?''', (actualPath, submissionid))
                        with open("{path}/{filename}".format(path=self.path, filename=fileName[0]), 'wb') as out_file:
                            shutil.copyfileobj(response.raw, out_file)
                        del response
                    count += 1
                if count == requested:
                    break
        self.conn.commit()

    def cleanDirectory(self):
        for file in os.listdir(self.path):
            os.remove("{path}/{filename}".format(path=self.path, filename=file))


class Setter:
    path = os.path.join(os.path.dirname(__file__) + '/img')

    def __init__(self):
        print("Setting backgrounds!")

    def setWallpaper(self, timer):
        while True:
            for file in os.listdir(self.path):
                print(file)
                SPI_SETDESKWALLPAPER = 20
                ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0,
                                                           self.path.format(
                                                               file),
                                                           0)
                time.sleep(timer)
