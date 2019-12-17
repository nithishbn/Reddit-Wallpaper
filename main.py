import ctypes
import glob
import os
import re
import shutil
import sqlite3
import time
from os import listdir

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

        for submission in subreddit.top('week'):
            title = submission.title
            url = submission.url
            submissionid = submission.id
            ids.append(submissionid)
            height = 1080
            width = 1920
            fileName = re.findall("(?:com|it|net).*/(.*[(jpg),(png)]$)", url)
            if ('.jpg' or '.png' in url) and len(fileName) != 0:
                print(url)
                submissionHeight = submission.preview['images'][0]['source']['height']
                submissionWidth = submission.preview['images'][0]['source']['width']
                if (submissionHeight/ submissionWidth) >= (height / width) and (submissionHeight>=height and submissionWidth>=width):
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
    path = os.path.join(os.path.dirname(__file__)) + r"\img"
    SPI_SETDESKWALLPAPER = 20

    def __init__(self):
        print("Setting backgrounds!")
        print(self.path)
        self.setWallpaperIndefinitely(5)

    def setWallpaperIndefinitely(self, timer):
        while True:
            for r, d, f in os.walk(self.path):
                for file in f:
                    if ".jpg" in file or ".png" in file:
                        self.setWallpaper(os.path.join(r, file))
                        time.sleep(timer)
            # images = [os.path.abspath(f) for f in os.listdir(self.path) if ".png" in f]
            # print(images)
            # for f in glob.glob("*.jpg"):
            #     print(f)
            # time.sleep(2)
            # for file in images:
            #     print(file)
            #     #self.setWallpaper(file)
            #     #time.sleep(timer)

    def setWallpaper(self, imagefile):
        ctypes.windll.user32.SystemParametersInfoW(self.SPI_SETDESKWALLPAPER, 0,
                                                   imagefile,
                                                   0)


if __name__ == '__main__':
    conn = sqlite3.connect('data.sqlite', check_same_thread=False)
    cur = conn.cursor()
    state = ""
    numberOfImages = 10


    def runApp(state="normal", subreddit="earthporn", number=20):
        if state=="reset":
            i = ImageScrapper(subreddit)
            cur.execute('''DELETE FROM main WHERE favorited==0''')
            conn.commit()
            conn.close()
            i.cleanDirectory()
            i.scrap(number)
        s = Setter()

    runApp(state="reset")

