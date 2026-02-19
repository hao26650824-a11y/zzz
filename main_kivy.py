from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.clock import Clock
from kivy.core.text import Label as KivyLabel
import random
import math
from dataclasses import dataclass
from typing import List, Tuple

# Set Window Size
Window.size = (1000, 700)

# Game Configuration
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60
BACKGROUND_COLOR = (230/255, 240/255, 250/255)
PRIMARY_COLOR = (255/255, 105/255, 180/255)
SECONDARY_COLOR = (30/255, 144/255, 255/255)
TEXT_COLOR = (0, 0, 0)
WHITE = (1, 1, 1)
BLACK = (0, 0, 0)

FONT_LARGE = 80
FONT_MEDIUM = 48
FONT_SMALL = 36
FONT_TINY = 28

# Data Classes
@dataclass
class Balloon:
    x: float
    y: float
    radius: int
    color: Tuple[int, int, int]
    velocity_y: float = -1.5
    is_clicked: bool = False
    pop_time: int = 0

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: Tuple[int, int, int]
    radius: int
    life: int

@dataclass
class FloatingText:
    x: float
    y: float
    text: str
    color: Tuple[int, int, int]
    life: int

class MomBirthdayGame:
    def __init__(self):
        self.state = "menu"
        self.balloons = []
        self.particles = []
        self.floating_texts = []
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.time_left = 60
        self.start_ticks = 0
        self.balloons_popped = 0
        self.balloons_missed = 0
        self.difficulty = "normal"
        self.high_score = 0
        self.mom_privilege_count = 0
        self.load_high_score()

    def load_high_score(self):
        try:
            with open("high_score.txt", "r") as f:
                self.high_score = int(f.read())
        except:
            self.high_score = 0

    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            with open("high_score.txt", "w") as f:
                f.write(str(self.high_score))

    def reset_game(self):
        self.balloons.clear()
        self.particles.clear()
        self.floating_texts.clear()
        self.score = 0
        self.combo = 0
        self.balloons_popped = 0
        self.balloons_missed = 0
        self.time_left = 60
        self.mom_privilege_count = 0
        self.start_ticks = int(Clock.get_time() * 1000)
        self.state = "playing"

    def create_balloon(self):
        colors = [
            (255/255, 105/255, 180/255), (30/255, 144/255, 255/255),
            (50/255, 205/255, 50/255), (255/255, 215/255, 0),
            (255/255, 69/255, 0), (138/255, 43/255, 226/255),
            (255/255, 192/255, 203/255), (0, 206/255, 209/255)
        ]
        balloon = Balloon(
            x=random.randint(60, SCREEN_WIDTH - 60),
            y=SCREEN_HEIGHT + 50,
            radius=random.randint(20, 35),
            color=random.choice(colors),
            velocity_y=-random.uniform(1.5, 3)
        )
        self.balloons.append(balloon)

    def activate_mom_privilege(self):
        if not self.balloons:
            return
        self.mom_privilege_count += 1
        for balloon in self.balloons:
            if not balloon.is_clicked:
                balloon.is_clicked = True
                base_score = 10
                combo_bonus = self.combo * 2
                total_score = base_score + combo_bonus
                self.score += total_score
                self.balloons_popped += 1
                self.combo += 1
                self.max_combo = max(self.max_combo, self.combo)
                for _ in range(12):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(2, 6)
                    particle = Particle(
                        x=balloon.x, y=balloon.y,
                        vx=speed * math.cos(angle),
                        vy=speed * math.sin(angle),
                        color=balloon.color,
                        radius=random.randint(2, 5),
                        life=50
                    )
                    self.particles.append(particle)
                text = FloatingText(
                    x=balloon.x, y=balloon.y,
                    text=f"+{total_score}",
                    color=PRIMARY_COLOR,
                    life=40
                )
                self.floating_texts.append(text)
        text = FloatingText(
            x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT // 2,
            text=f"MOM'S PRIVILEGE! (x{self.mom_privilege_count})",
            color=(255/255, 69/255, 0),
            life=60
        )
        self.floating_texts.append(text)

    def update(self):
        if self.state != "playing":
            return
        elapsed = int((Clock.get_time() * 1000 - self.start_ticks) / 1000)
        self.time_left = max(0, 60 - elapsed)
        if random.random() < 0.08:
            self.create_balloon()
        for balloon in self.balloons[:]:
            if not balloon.is_clicked:
                balloon.y += balloon.velocity_y
                if balloon.y < -50:
                    self.balloons.remove(balloon)
                    self.balloons_missed += 1
                    self.combo = 0
                    text = FloatingText(
                        x=balloon.x, y=balloon.y + 100,
                        text="MISS!",
                        color=(255/255, 0, 0),
                        life=30
                    )
                    self.floating_texts.append(text)
            else:
                balloon.pop_time += 1
                if balloon.pop_time > 10:
                    self.balloons.remove(balloon)
        for particle in self.particles[:]:
            particle.x += particle.vx
            particle.y += particle.vy
            particle.vy += 0.15
            particle.life -= 1
            if particle.life <= 0:
                self.particles.remove(particle)
        for text in self.floating_texts[:]:
            text.y -= 1
            text.life -= 1
            if text.life <= 0:
                self.floating_texts.remove(text)
        if self.time_left <= 0:
            self.state = "game_over"
            self.save_high_score()

    def handle_click(self, pos):
        if self.state != "playing":
            return
        for balloon in self.balloons:
            if not balloon.is_clicked:
                dx = balloon.x - pos[0]
                dy = balloon.y - pos[1]
                distance = math.sqrt(dx ** 2 + dy ** 2)
                if distance <= balloon.radius:
                    balloon.is_clicked = True
                    base_score = 10
                    combo_bonus = self.combo * 2
                    total_score = base_score + combo_bonus
                    self.score += total_score
                    self.balloons_popped += 1
                    self.combo += 1
                    self.max_combo = max(self.max_combo, self.combo)
                    for _ in range(12):
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(2, 6)
                        particle = Particle(
                            x=balloon.x, y=balloon.y,
                            vx=speed * math.cos(angle),
                            vy=speed * math.sin(angle),
                            color=balloon.color,
                            radius=random.randint(2, 5),
                            life=50
                        )
                        self.particles.append(particle)
                    text = FloatingText(
                        x=balloon.x, y=balloon.y,
                        text=f"+{total_score}",
                        color=PRIMARY_COLOR,
                        life=40
                    )
                    self.floating_texts.append(text)
                    break

class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = MomBirthdayGame()
        Clock.schedule_interval(self.update_game, 1.0 / FPS)
        self.bind(size=self.on_size)

    def on_size(self, widget, size):
        pass

    def on_touch_down(self, touch):
        x = touch.x
        y = SCREEN_HEIGHT - touch.y
        if self.game.state == "menu":
            if 100 <= x <= 280 and 50 <= y <= 90:
                self.game.difficulty = "easy"
                self.game.reset_game()
            elif 410 <= x <= 590 and 50 <= y <= 90:
                self.game.difficulty = "normal"
                self.game.reset_game()
            elif 720 <= x <= 900 and 50 <= y <= 90:
                self.game.difficulty = "hard"
                self.game.reset_game()
        elif self.game.state == "playing":
            self.game.handle_click((x, y))
        elif self.game.state == "game_over":
            if 200 <= x <= 480 and 30 <= y <= 80:
                self.game.reset_game()
            elif 520 <= x <= 800 and 30 <= y <= 80:
                self.game.state = "menu"
        return True

    def on_touch_move(self, touch):
        return True

    def on_touch_up(self, touch):
        return True

    def keyboard_on_key_down(self, window, key, scancode, codepoint, modifier):
        if key == 109:
            if self.game.state == "playing":
                self.game.activate_mom_privilege()
        return True

    def update_game(self, dt):
        self.game.update()
        self.canvas.clear()
        if self.game.state == "menu":
            self.draw_menu()
        elif self.game.state == "playing":
            self.draw_game()
        elif self.game.state == "game_over":
            self.draw_game_over()

    def draw_text(self, text, size, color, x, y, center=False):
        y = SCREEN_HEIGHT - y
        from kivy.core.text import Label as TextLabel
        label = TextLabel(text=str(text), font_size=str(int(size)))
        label.refresh()
        with self.canvas:
            Color(*color)
            if center:
                x = x - label.texture_size[0] // 2
                y = y - label.texture_size[1] // 2
            Rectangle(texture=label.texture, pos=(x, y), size=label.texture_size)

    def draw_circle(self, x, y, radius, color, border_width=0):
        y = SCREEN_HEIGHT - y
        with self.canvas:
            Color(*color)
            Ellipse(pos=(x - radius, y - radius), size=(radius * 2, radius * 2))
            if border_width > 0:
                Color(*BLACK)
                Line(circle=(x, y, radius), width=border_width)

    def draw_rectangle(self, x, y, width, height, color, border_width=0):
        y = SCREEN_HEIGHT - y - height
        with self.canvas:
            Color(*color)
            Rectangle(pos=(x, y), size=(width, height))
            if border_width > 0:
                Color(*BLACK)
                Line(rectangle=(x, y, width, height), width=border_width)

    def draw_line(self, x1, y1, x2, y2, color=BLACK, width=2):
        y1 = SCREEN_HEIGHT - y1
        y2 = SCREEN_HEIGHT - y2
        with self.canvas:
            Color(*color)
            Line(points=[x1, y1, x2, y2], width=width)

    def draw_menu(self):
        with self.canvas:
            Color(*BACKGROUND_COLOR)
            Rectangle(pos=(0, 0), size=Window.size)
        self.draw_text("MOM'S HAPPY BIRTHDAY", FONT_LARGE, PRIMARY_COLOR, SCREEN_WIDTH // 2, 20, center=True)
        self.draw_text("Balloon Pop Game", FONT_SMALL, SECONDARY_COLOR, SCREEN_WIDTH // 2, 75, center=True)
        self.draw_text("Instructions:", FONT_SMALL, TEXT_COLOR, 120, 420)
        self.draw_text("- Click balloons to pop them", FONT_TINY, TEXT_COLOR, 120, 460)
        self.draw_text("- Build combos for extra points", FONT_TINY, TEXT_COLOR, 120, 495)
        self.draw_text("- Press M key for Mom's Special Power", FONT_TINY, (1, 140/255, 0), 120, 565)
        self.draw_text(f"High Score: {self.game.high_score}", FONT_SMALL, SECONDARY_COLOR, SCREEN_WIDTH // 2, 620, center=True)
        self.draw_rectangle(100, 650, 180, 40, PRIMARY_COLOR)
        self.draw_text("EASY", FONT_SMALL, WHITE, 100 + 90, 650 + 20, center=True)
        self.draw_rectangle(410, 650, 180, 40, SECONDARY_COLOR)
        self.draw_text("NORMAL", FONT_SMALL, WHITE, 410 + 90, 650 + 20, center=True)
        self.draw_rectangle(720, 650, 180, 40, (220/255, 20/255, 60/255))
        self.draw_text("HARD", FONT_SMALL, WHITE, 720 + 90, 650 + 20, center=True)

    def draw_game(self):
        with self.canvas:
            Color(*BACKGROUND_COLOR)
            Rectangle(pos=(0, 0), size=Window.size)
        for balloon in self.game.balloons:
            if not balloon.is_clicked:
                self.draw_circle(int(balloon.x), int(balloon.y), balloon.radius, balloon.color, 2)
                self.draw_line(int(balloon.x), int(balloon.y) + balloon.radius, int(balloon.x), int(balloon.y) + balloon.radius + 30, BLACK, 2)
            else:
                if balloon.pop_time > 0:
                    for i in range(balloon.pop_time):
                        self.draw_circle(int(balloon.x), int(balloon.y), balloon.radius + i * 3, balloon.color, 1)
        for particle in self.game.particles:
            self.draw_circle(int(particle.x), int(particle.y), particle.radius, particle.color)
        for text in self.game.floating_texts:
            self.draw_text(text.text, FONT_SMALL, text.color, int(text.x), int(text.y), center=True)
        self.draw_text(f"Score: {self.game.score}", FONT_MEDIUM, PRIMARY_COLOR, 30, 30)
        time_color = (1, 0, 0) if self.game.time_left < 10 else SECONDARY_COLOR
        self.draw_text(f"Time: {self.game.time_left}s", FONT_MEDIUM, time_color, SCREEN_WIDTH - 300, 30)
        if self.game.combo > 0:
            self.draw_text(f"Combo x{self.game.combo}", FONT_SMALL, (1, 215/255, 0), SCREEN_WIDTH // 2, 30, center=True)
        self.draw_text(f"Popped: {self.game.balloons_popped} | Missed: {self.game.balloons_missed}", FONT_TINY, TEXT_COLOR, 30, SCREEN_HEIGHT - 40)
        mom_power_text = f"Mom's Power (M): {self.game.mom_privilege_count} used"
        self.draw_text(mom_power_text, FONT_TINY, (1, 140/255, 0), SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT - 40)

    def draw_game_over(self):
        with self.canvas:
            Color(*BACKGROUND_COLOR)
            Rectangle(pos=(0, 0), size=Window.size)
        self.draw_text("GAME OVER", FONT_LARGE, PRIMARY_COLOR, SCREEN_WIDTH // 2, 20, center=True)
        self.draw_text(f"Final Score: {self.game.score}", FONT_MEDIUM, PRIMARY_COLOR, SCREEN_WIDTH // 2, 360, center=True)
        stats_y = 420
        self.draw_text(f"Balloons Popped: {self.game.balloons_popped}", FONT_SMALL, TEXT_COLOR, SCREEN_WIDTH // 2, stats_y, center=True)
        self.draw_text(f"Balloons Missed: {self.game.balloons_missed}", FONT_SMALL, TEXT_COLOR, SCREEN_WIDTH // 2, stats_y + 40, center=True)
        self.draw_text(f"Max Combo: x{self.game.max_combo}", FONT_SMALL, TEXT_COLOR, SCREEN_WIDTH // 2, stats_y + 80, center=True)
        power_text = f"Mom's Power Used: {self.game.mom_privilege_count} times"
        self.draw_text(power_text, FONT_SMALL, (1, 140/255, 0), SCREEN_WIDTH // 2, stats_y + 120, center=True)
        if self.game.score == self.game.high_score and self.game.high_score > 0:
            self.draw_text("NEW HIGH SCORE!", FONT_MEDIUM, (1, 215/255, 0), SCREEN_WIDTH // 2, stats_y + 170, center=True)
        else:
            self.draw_text(f"High Score: {self.game.high_score}", FONT_SMALL, SECONDARY_COLOR, SCREEN_WIDTH // 2, stats_y + 170, center=True)
        if self.game.score >= 500:
            rating = "EXCELLENT!"
        elif self.game.score >= 300:
            rating = "GREAT!"
        elif self.game.score >= 100:
            rating = "GOOD!"
        else:
            rating = "Keep practicing!"
        self.draw_text(rating, FONT_SMALL, PRIMARY_COLOR, SCREEN_WIDTH // 2, stats_y + 210, center=True)
        self.draw_rectangle(200, SCREEN_HEIGHT - 70, 280, 50, SECONDARY_COLOR)
        self.draw_text("PLAY AGAIN", FONT_SMALL, WHITE, 200 + 140, SCREEN_HEIGHT - 70 + 25, center=True)
        self.draw_rectangle(520, SCREEN_HEIGHT - 70, 280, 50, PRIMARY_COLOR)
        self.draw_text("MAIN MENU", FONT_SMALL, WHITE, 520 + 140, SCREEN_HEIGHT - 70 + 25, center=True)

class MomBirthdayGameApp(App):
    def build(self):
        root = GameWidget()
        keyboard = Window.request_keyboard(self._keyboard_closed, root)
        keyboard.bind(on_key_down=root.keyboard_on_key_down)
        return root

    def _keyboard_closed(self):
        pass

if __name__ == '__main__':
    MomBirthdayGameApp().run()