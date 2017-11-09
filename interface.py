import math
from kivy.app import App
from kivy.factory import Factory
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivymd.card import MDCard
from kivymd.theming import ThemeManager
from threading import Thread
import os
import sqlite3
from main import ImageScrapper, Setter
from kivy.config import Config
Config.set('graphics','resizable',0)
from kivy.core.window import Window
Window.size = (960, 540)

class ImageTile(MDCard):
    source = StringProperty('')
    title = StringProperty('')

class MenuScreen(Screen):
    path = os.path.dirname(__file__) + '/img'
    conn = sqlite3.connect('data.sqlite')
    cur = conn.cursor()
    colsToUse = 3
    state = "reset"
    submissionid = ""
    def on_pre_enter(self, *args):
        t = Thread(target=App.get_running_app().runApp, args=(App.get_running_app().listtouse, self.state))
        t.start()

    def getTitle(self,submissionid):
        values = self.cur.execute('''SELECT title FROM main WHERE main.id=?''',(submissionid,))
        title = values.fetchall()[0][0]
        print(title)
        return title
    # def getColsNumber(self):
    #     return self.colsToUse
    def getRowNumber(self):
        rows = math.ceil(9 / self.colsToUse)
        print(rows)
        return rows

    def addstuff(self, *args):
        lst = self.getAllPaths()
        for path in lst:
            widget = Factory.ImageTile(source=path[1],title=self.getTitle(path[0]))
            self.ids.grid.add_widget(widget)

    def getAllPaths(self):
        values = self.cur.execute('''SELECT id,path FROM main''')
        values = values.fetchall()
        lst = []
        for i in values:
            lst.append(i)
        return lst



class InterfaceApp(App):
    theme_cls = ThemeManager()
    listtouse = ListProperty([])
    MAX_TIME = 1 / 60.
    conn = sqlite3.connect('data.sqlite',check_same_thread=False)
    cur = conn.cursor()

    def build(self):
        Clock.schedule_interval(self.consume, 0)

    def consume(self, *args):
        while self.listtouse:
            item = self.listtouse.pop(0)
            if item == 1:
                Clock.schedule_once(self.root.ids.menu.addstuff, 0.1)

    def runApp(self, listtouse, state="normal", subreddit="wallpapers", number=10):
        if state == "reset" or subreddit != "wallpapers":
            i = ImageScrapper(subreddit)
            self.cur.execute('''DELETE FROM main WHERE favorited==0''')
            self.conn.commit()
            self.conn.close()
            i.cleanDirectory()
            i.scrap(number)
            listtouse.append(1)


i = InterfaceApp()
i.run()
