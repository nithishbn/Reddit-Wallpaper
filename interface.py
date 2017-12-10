import math
import os
import sqlite3
from threading import Thread

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.properties import ListProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import Screen
from kivymd.card import MDCard
from kivymd.navigationdrawer import NavigationLayout
from kivymd.theming import ThemeManager
from main import ImageScrapper

# Window.size = (900, 600)
Window.maximize()


class ImageTile(ButtonBehavior, MDCard):
    source = StringProperty('')
    title = StringProperty('')
    idThing = StringProperty('')

    def zoom(self, source):
        widget = Factory.Image(source=source, pos_hint={'center_x': 0.5, 'center_y': 0.45}, size_hint=(1, 0.85))
        App.get_running_app().root.ids.menu.add_widget(widget)


class SettingsScreen(Screen):
    pass


class MenuScreen(Screen):
    path = os.path.dirname(__file__) + '/img'
    conn = sqlite3.connect('data.sqlite')
    cur = conn.cursor()
    colsToUse = 4

    submissionid = ""

    def getTitle(self, submissionid):
        values = self.cur.execute('''SELECT title FROM main WHERE main.id=?''', (submissionid,))
        title = values.fetchall()[0][0]
        newtitle = ""
        for character in title:
            if len(newtitle) >= 40:
                newtitle += "..."
                break
            newtitle += character
        return str(newtitle)

    def getRowNumber(self, totalSubmissions):
        rows = math.ceil(totalSubmissions / self.colsToUse)
        print("rows", rows)
        return rows

    def getTotalSubmissions(self):
        values = self.cur.execute('''SELECT COUNT(id) FROM main''')
        values = values.fetchall()[0][0]
        print(values)
        return values

    def addstuff(self, *args):
        lst = self.getAllPaths()
        for path in lst:
            widget = Factory.ImageTile(source=str(path[1]), title=self.getTitle(path[0]), idThing=path[0])
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
    conn = sqlite3.connect('data.sqlite', check_same_thread=False)
    cur = conn.cursor()
    state = "reset"
    numberOfImages = 30

    def build(self):
        t = Thread(target=App.get_running_app().runApp,
                   args=(App.get_running_app().listtouse, self.state, "wallpapers", self.numberOfImages))
        t.start()
        Clock.schedule_interval(self.consume, 0)

    def consume(self, *args):
        while self.listtouse:
            item = self.listtouse.pop(0)
            if item == 1:
                Clock.schedule_once(self.root.ids.menu.addstuff, 0.1)

    def runApp(self, listtouse, state="normal", subreddit="wallpapers", number=20):
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
