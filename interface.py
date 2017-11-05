from kivy.app import App
from kivy.uix.label import Label
from kivy.factory import Factory
from kivy.properties import ListProperty
from kivy.clock import Clock, _default_time as time
from kivy.uix.screenmanager import Screen
from kivymd.theming import ThemeManager
from threading import Thread
import re
import os
import requests
import shutil
import ctypes
import praw
import sqlite3
import config


class ImageScrapper:
    path = os.path.join(os.path.dirname(__file__) + '/img')

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
        for submission in subreddit.top('month'):
            title = submission.title
            imagelink = submission.url
            submissionid = submission.id
            width = 1920
            if '.jpg' or '.png' in imagelink:
                if submission.preview['images'][0]['source']['width'] >= width:
                    urls.append(submission.url)
                    self.cur.execute('''INSERT OR IGNORE INTO main.main VALUES (?,?,?,?) ''',
                                     (submissionid, imagelink, title, 0))
                if count == requested:
                    break
                count += 1
        self.conn.commit()
        urlcount = 1
        for url in urls:
            print("Downloading {} of {}".format(urlcount, len(urls)))
            fileName = re.findall("(?:com|it|net).*\/(.*[(jpg),(png)]$)", url)
            if len(fileName) == 0:
                continue
            else:
                response = requests.get(url, stream=True)
                with open("{path}/{filename}".format(path=self.path, filename=fileName[0]), 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response
                urlcount += 1
        return 0

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


MAX_TIME = 1 / 60.


class MenuScreen(Screen):
    path = os.path.dirname(__file__) + '/img'

    def on_enter(self, *args):
        t = Thread(target=App.get_running_app().runApp, args=(App.get_running_app().listtouse, "reset"))
        t.start()

    def pathGet(self, img):
        return os.path.join(self.path, img)
    def printStuff(self,checker):
        print(checker)
        self.ids.labelthing.text = "Hello"
        self.add_widget(Label(text="Hello"))


class InterfaceApp(App):
    theme_cls = ThemeManager()
    listtouse = ListProperty([])

    def build(self):
        Clock.schedule_interval(self.consume, 0)

    def consume(self, *args):
        while self.listtouse and time() < (Clock.get_time() + MAX_TIME):
            item = self.listtouse.pop(0)  # i want the first one
            # label = Factory.MyLabel(text=item)
            # self.root.ids.target.add_widget(label)
            if item == 1:
                MenuScreen().printStuff(item)

    def runApp(self, listtouse, state="normal", subreddit="wallpapers", number=100, timer=5):
        i = ImageScrapper(subreddit)

        if state == "reset" or subreddit != "wallpapers":
            i.cleanDirectory()
            i.scrap(number)
            print("Finished with runApp")
            listtouse.append(1)


i = InterfaceApp()
i.run()
