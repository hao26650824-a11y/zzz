import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse
import random
import sys

class Balloon(Widget):
    def __init__(self, **kwargs):
        super(Balloon, self).__init__(**kwargs)
        self.size = (50, 70)
        with self.canvas:
            Color(1, 0, 0)  # Red color
            self.ellipse = Ellipse(pos=self.pos, size=self.size)

    def on_size(self, *args):
        self.ellipse.size = self.size

    def on_pos(self, *args):
        self.ellipse.pos = self.pos

class BalloonPopGame(Widget):
    def __init__(self, **kwargs):
        super(BalloonPopGame, self).__init__(**kwargs)
        self.balloons = []
        self.score = 0
        self.score_label = Label(text='Score: 0', font_size='20sp', size_hint=(None, None), size=(200, 50))
        self.score_label.pos = (self.center_x - self.score_label.width / 2, self.height - self.score_label.height)
        self.add_widget(self.score_label)
        Clock.schedule_interval(self.add_balloon, 1)

    def add_balloon(self, dt):
        balloon = Balloon()
        balloon.x = random.randint(0, self.width - balloon.width)
        balloon.y = 0
        self.add_widget(balloon)
        self.balloons.append(balloon)

    def on_touch_down(self, touch):
        for balloon in self.balloons:
            if balloon.collide_point(touch.x, touch.y):
                self.score += 1
                self.score_label.text = f'Score: {self.score}'
                self.remove_widget(balloon)
                self.balloons.remove(balloon)
                break

class BalloonPopApp(App):
    def build(self):
        game = BalloonPopGame()
        return game

if __name__ == '__main__':
    BalloonPopApp().run()