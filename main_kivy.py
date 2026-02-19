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
BACKGROUND_COLOR = (230 / 255, 240 / 255, 250 / 255)
PRIMARY_COLOR = (255 / 255, 105 / 255, 180 / 255)
SECONDARY_COLOR = (30 / 255, 144 / 255, 255 / 255)
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
            (255 / 255, 105 / 255, 180 / 255), (30 / 255, 144 / 255, 255 / 255),
            (50 / 255, 205 / 255, 50 / 255), (255 / 255, 215 / 255, 0),
            (255 / 255, 69 / 255, 0), (138 / 255, 43 / 255, 226 / 255),
            (255 / 255, 192 / 255, 203 / 255), (0, 206 / 255, 209 / 255)
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
            color=(255 / 255, 69 / 255, 0),
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

        # 菜单按钮
        self.menu_buttons = [
            (150, 350, 200, 60, "easy"),
            (400, 350, 200, 60, "normal"),
            (650, 350, 200, 60, "hard")
        ]

        # 游戏结束按钮 - 移到底部
        self.game_over_buttons = [
            (150, 620, 280, 50, "replay"),
            (570, 620, 280, 50, "menu")
        ]

        # 请求键盘
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def on_size(self, widget, size):
        pass

    def _keyboard_closed(self):
        """键盘关闭时"""
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """键盘按下事件"""
        print(f"按键: keycode={keycode}, text={text}")

        # 检查 M 或 m 键
        if text and text.lower() == 'm':
            print("检测到 M 键！")
            if self.game.state == "playing":
                print("激活 Mom's Privilege")
                self.game.activate_mom_privilege()

        return True

    def on_touch_down(self, touch):
        x = touch.x
        y = SCREEN_HEIGHT - touch.y

        print(f"点击位置: x={x}, y={y}")

        if self.game.state == "menu":
            for btn_x, btn_y, btn_w, btn_h, difficulty in self.menu_buttons:
                if btn_x <= x <= btn_x + btn_w and btn_y <= y <= btn_y + btn_h:
                    print(f"点击了 {difficulty} 难度")
                    self.game.difficulty = difficulty
                    self.game.reset_game()
                    return True

        elif self.game.state == "playing":
            self.game.handle_click((x, y))
            return True

        elif self.game.state == "game_over":
            for btn_x, btn_y, btn_w, btn_h, action in self.game_over_buttons:
                if btn_x <= x <= btn_x + btn_w and btn_y <= y <= btn_y + btn_h:
                    print(f"点击了 {action} 按钮")
                    if action == "replay":
                        self.game.reset_game()
                    elif action == "menu":
                        self.game.state = "menu"
                    return True

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

    def draw_text_simple(self, text, size, color, x, y, center=False):
        """Draw text using Kivy Label texture"""
        try:
            label = KivyLabel(text=str(text), font_size=str(int(size)))
            label.refresh()

            y_pos = SCREEN_HEIGHT - y

            with self.canvas:
                Color(*color)
                if center:
                    x_pos = x - label.texture.size[0] // 2
                    y_pos = y_pos - label.texture.size[1] // 2
                else:
                    x_pos = x

                Rectangle(texture=label.texture, pos=(x_pos, y_pos), size=label.texture.size)
        except Exception as e:
            print(f"Error drawing text: {e}")

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

        self.draw_text_simple("MOM'S HAPPY BIRTHDAY", FONT_LARGE, PRIMARY_COLOR, SCREEN_WIDTH // 2, 100, center=True)
        self.draw_text_simple("Balloon Pop Game", FONT_SMALL, SECONDARY_COLOR, SCREEN_WIDTH // 2, 150, center=True)

        self.draw_text_simple("Select Difficulty:", FONT_MEDIUM, TEXT_COLOR, SCREEN_WIDTH // 2, 280, center=True)

        # EASY 按钮
        self.draw_rectangle(150, 350, 200, 60, PRIMARY_COLOR, 3)
        self.draw_text_simple("EASY", FONT_SMALL, WHITE, 250, 380, center=True)

        # NORMAL 按钮
        self.draw_rectangle(400, 350, 200, 60, SECONDARY_COLOR, 3)
        self.draw_text_simple("NORMAL", FONT_SMALL, WHITE, 500, 380, center=True)

        # HARD 按钮
        self.draw_rectangle(650, 350, 200, 60, (220 / 255, 20 / 255, 60 / 255), 3)
        self.draw_text_simple("HARD", FONT_SMALL, WHITE, 750, 380, center=True)

        self.draw_text_simple(f"High Score: {self.game.high_score}", FONT_SMALL, SECONDARY_COLOR, SCREEN_WIDTH // 2,
                              550, center=True)

    def draw_game(self):
        with self.canvas:
            Color(*BACKGROUND_COLOR)
            Rectangle(pos=(0, 0), size=Window.size)

        for balloon in self.game.balloons:
            if not balloon.is_clicked:
                self.draw_circle(int(balloon.x), int(balloon.y), balloon.radius, balloon.color, 2)
                self.draw_line(int(balloon.x), int(balloon.y) + balloon.radius, int(balloon.x),
                               int(balloon.y) + balloon.radius + 30, BLACK, 2)

        for particle in self.game.particles:
            self.draw_circle(int(particle.x), int(particle.y), particle.radius, particle.color)

        for text in self.game.floating_texts:
            self.draw_text_simple(text.text, FONT_SMALL, text.color, int(text.x), int(text.y), center=True)

        self.draw_text_simple(f"Score: {self.game.score}", FONT_MEDIUM, PRIMARY_COLOR, 30, 30)
        time_color = (1, 0, 0) if self.game.time_left < 10 else SECONDARY_COLOR
        self.draw_text_simple(f"Time: {self.game.time_left}s", FONT_MEDIUM, time_color, SCREEN_WIDTH - 300, 30)

        if self.game.combo > 0:
            self.draw_text_simple(f"Combo x{self.game.combo}", FONT_SMALL, (1, 215 / 255, 0), SCREEN_WIDTH // 2, 30,
                                  center=True)

        self.draw_text_simple(f"Popped: {self.game.balloons_popped} | Missed: {self.game.balloons_missed}", FONT_TINY,
                              TEXT_COLOR, 30, SCREEN_HEIGHT - 40)
        mom_power_text = f"Mom's Power (M): {self.game.mom_privilege_count} used"
        self.draw_text_simple(mom_power_text, FONT_TINY, (1, 140 / 255, 0), SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT - 40)

    def draw_game_over(self):
        with self.canvas:
            Color(*BACKGROUND_COLOR)
            Rectangle(pos=(0, 0), size=Window.size)

        # 标题
        self.draw_text_simple("GAME OVER", FONT_LARGE, PRIMARY_COLOR, SCREEN_WIDTH // 2, 50, center=True)

        # 最终分数
        self.draw_text_simple(f"Final Score: {self.game.score}", FONT_MEDIUM, PRIMARY_COLOR, SCREEN_WIDTH // 2, 120,
                              center=True)

        # 统计信息 - 分布在屏幕上方到中间
        stats_y = 200
        self.draw_text_simple(f"Balloons Popped: {self.game.balloons_popped}", FONT_SMALL, TEXT_COLOR,
                              SCREEN_WIDTH // 2, stats_y, center=True)
        self.draw_text_simple(f"Balloons Missed: {self.game.balloons_missed}", FONT_SMALL, TEXT_COLOR,
                              SCREEN_WIDTH // 2, stats_y + 40, center=True)
        self.draw_text_simple(f"Max Combo: x{self.game.max_combo}", FONT_SMALL, TEXT_COLOR, SCREEN_WIDTH // 2,
                              stats_y + 80, center=True)
        power_text = f"Mom's Power Used: {self.game.mom_privilege_count} times"
        self.draw_text_simple(power_text, FONT_SMALL, (1, 140 / 255, 0), SCREEN_WIDTH // 2, stats_y + 120, center=True)

        # 高分显示
        if self.game.score == self.game.high_score and self.game.high_score > 0:
            self.draw_text_simple("NEW HIGH SCORE!", FONT_MEDIUM, (1, 215 / 255, 0), SCREEN_WIDTH // 2, stats_y + 170,
                                  center=True)
        else:
            self.draw_text_simple(f"High Score: {self.game.high_score}", FONT_SMALL, SECONDARY_COLOR, SCREEN_WIDTH // 2,
                                  stats_y + 170, center=True)

        # 评分
        if self.game.score >= 500:
            rating = "EXCELLENT!"
        elif self.game.score >= 300:
            rating = "GREAT!"
        elif self.game.score >= 100:
            rating = "GOOD!"
        else:
            rating = "Keep practicing!"

        self.draw_text_simple(rating, FONT_SMALL, PRIMARY_COLOR, SCREEN_WIDTH // 2, stats_y + 220, center=True)

        # 按钮 - 放在屏幕底部（y=620）
        self.draw_rectangle(150, 620, 280, 50, SECONDARY_COLOR, 3)
        self.draw_text_simple("PLAY AGAIN", FONT_SMALL, WHITE, 290, 645, center=True)

        self.draw_rectangle(570, 620, 280, 50, PRIMARY_COLOR, 3)
        self.draw_text_simple("MAIN MENU", FONT_SMALL, WHITE, 710, 645, center=True)


class MomBirthdayGameApp(App):
    def build(self):
        root = GameWidget()
        return root


if __name__ == '__main__':
    MomBirthdayGameApp().run()
