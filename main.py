import re
import os
import requests
import shutil
import ctypes
import time
import praw
import sqlite3
import config


class ImageScrapper:
    path = os.path.join(os.path.dirname(__file__) + '\img\\')

    def __init__(self, subreddit):
        self.r = praw.Reddit(username=config.username, password=config.password, client_id=config.client_id,
                             client_secret=config.client_secret, user_agent="Nithishbn's ImageScrapper")
        self.subreddit = subreddit
        self.conn = sqlite3.connect('data.sqlite')
        self.cur = self.conn.cursor()

    def scrap(self, requested):
        subreddit = self.r.subreddit(self.subreddit)
        count = 0
        urls = []
        ids = []
        for submission in subreddit.top('month'):
            title = submission.title
            imagelink = submission.url
            submissionid = submission.id
            ids.append(submissionid)
            width = 1920
            if '.jpg' or '.png' in imagelink:
                if submission.preview['images'][0]['source']['width'] >= width:
                    urls.append(submission.url)
                    self.cur.execute('''INSERT OR IGNORE INTO main.main VALUES (?,?,?,?,?) ''',
                                     (submissionid, imagelink, title, 0, 0))
                if count == requested:
                    break
                count += 1
        self.conn.commit()
        urlcount = 1
        for url in urls:
            print("Downloading {} of {}".format(urlcount, len(urls)))
            fileName = re.findall("(?:com|it|net).*\/(.*[(jpg),(png)]$)", url)
            submissionid = self.cur.execute('''SELECT id FROM main WHERE image=?''', (url,)).fetchall()[0][0]
            if len(fileName) == 0:
                continue
            else:
                response = requests.get(url, stream=True)
                actualPath = self.path + fileName[0]
                self.cur.execute('''UPDATE OR IGNORE main SET path=? WHERE id=?''', (actualPath, submissionid))
                with open("{path}/{filename}".format(path=self.path, filename=fileName[0]), 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response
                urlcount += 1
        self.conn.commit()
        # return urlcount

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
