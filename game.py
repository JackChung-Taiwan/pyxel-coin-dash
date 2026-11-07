# title: Coin Dash - Pixel Coin Collector
# author: OpenAI
# desc: A Pyxel arcade coin-collecting game for desktop and mobile browsers
# license: MIT
# version: 1.0.0

"""Collect coins, avoid bombs, and beat your high score.

Desktop: arrow keys / WASD move, Space/Enter start/pause.
Mobile (Pyxel Web): virtual D-pad moves, A starts/pauses.
"""

import math
import pyxel

WIDTH = 256
HEIGHT = 192
FPS = 30
GAME_SECONDS = 60
PLAYER_SPEED = 2.0
COINS_ON_FIELD = 7
BOMBS_ON_FIELD = 3
PLAY_TOP = 34
PLAY_BOTTOM = 181
PLAY_LEFT = 9
PLAY_RIGHT = WIDTH - 10


class CoinDash:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Coin Dash", fps=FPS)
        self.best = 0
        self.state = "title"
        self.frame = 0
        self.player_x = WIDTH / 2
        self.player_y = 110
        self.coins = []
        self.bombs = []
        self.particles = []
        self.score = 0
        self.collected = 0
        self.lives = 3
        self.frames_left = GAME_SECONDS * FPS
        self.invulnerable = 0
        self.combo = 0
        self.combo_timeout = 0
        self.setup_sounds()
        pyxel.run(self.update, self.draw)

    def setup_sounds(self):
        pyxel.sounds[0].set("c3 e3 g3 c4", "p", "7765", "nnnn", 9)
        pyxel.sounds[1].set("g3 d3 c3", "n", "765", "nnf", 12)
        pyxel.sounds[2].set("c3 e3 g3 c4", "t", "7777", "nnnn", 13)
        pyxel.sounds[3].set("g3 e3 c3", "t", "765", "nnn", 18)

    def action(self):
        return (
            pyxel.btnp(pyxel.KEY_SPACE)
            or pyxel.btnp(pyxel.KEY_RETURN)
            or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
        )

    def direction(self, keyboard, gamepad):
        return pyxel.btn(keyboard) or pyxel.btn(gamepad)

    def reset(self):
        self.state = "playing"
        self.frame = 0
        self.player_x = WIDTH / 2
        self.player_y = (PLAY_TOP + PLAY_BOTTOM) / 2
        self.score = 0
        self.collected = 0
        self.lives = 3
        self.frames_left = GAME_SECONDS * FPS
        self.invulnerable = 0
        self.combo = 0
        self.combo_timeout = 0
        self.particles = []
        self.bombs = []
        self.coins = []
        for _ in range(BOMBS_ON_FIELD):
            x, y = self.random_position(31)
            self.bombs.append({
                "x": float(x), "y": float(y),
                "vx": float(pyxel.rndi(0, 1) * 2 - 1) * pyxel.rndi(4, 9) / 12,
                "vy": float(pyxel.rndi(0, 1) * 2 - 1) * pyxel.rndi(4, 9) / 12,
            })
        for _ in range(COINS_ON_FIELD):
            self.coins.append(self.random_position(17))
        pyxel.play(0, 2)

    def random_position(self, min_from_player=20):
        for _ in range(100):
            x = pyxel.rndi(PLAY_LEFT + 14, PLAY_RIGHT - 14)
            y = pyxel.rndi(PLAY_TOP + 14, PLAY_BOTTOM - 14)
            if self.distance(x, y, self.player_x, self.player_y) < min_from_player:
                continue
            if any(self.distance(x, y, b["x"], b["y"]) < 16 for b in self.bombs):
                continue
            if any(self.distance(x, y, c[0], c[1]) < 14 for c in self.coins):
                continue
            return (x, y)
        return (pyxel.rndi(20, WIDTH - 20), pyxel.rndi(50, HEIGHT - 20))

    @staticmethod
    def distance(ax, ay, bx, by):
        return math.hypot(ax - bx, ay - by)

    def burst(self, x, y, color, amount=10):
        for _ in range(amount):
            self.particles.append([
                float(x), float(y),
                pyxel.rndi(-13, 13) / 8,
                pyxel.rndi(-13, 13) / 8,
                pyxel.rndi(8, 17), color,
            ])

    def update_particles(self):
        for p in self.particles:
            p[0] += p[2]
            p[1] += p[3]
            p[4] -= 1
        self.particles = [p for p in self.particles if p[4] > 0]

    def update(self):
        self.frame += 1
        self.update_particles()

        if self.state == "title":
            if self.action():
                self.reset()
            return
        if self.state == "gameover":
            if self.action():
                self.reset()
            return
        if self.action():
            self.state = "paused" if self.state == "playing" else "playing"
        if self.state != "playing":
            return

        dx = int(self.direction(pyxel.KEY_RIGHT, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)) - int(
            self.direction(pyxel.KEY_LEFT, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
        )
        dy = int(self.direction(pyxel.KEY_DOWN, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)) - int(
            self.direction(pyxel.KEY_UP, pyxel.GAMEPAD1_BUTTON_DPAD_UP)
        )
        dx += int(pyxel.btn(pyxel.KEY_D)) - int(pyxel.btn(pyxel.KEY_A))
        dy += int(pyxel.btn(pyxel.KEY_S)) - int(pyxel.btn(pyxel.KEY_W))
        if dx or dy:
            magnitude = math.hypot(dx, dy)
            self.player_x += PLAYER_SPEED * dx / magnitude
            self.player_y += PLAYER_SPEED * dy / magnitude
        self.player_x = max(PLAY_LEFT + 9, min(PLAY_RIGHT - 9, self.player_x))
        self.player_y = max(PLAY_TOP + 9, min(PLAY_BOTTOM - 9, self.player_y))

        if self.invulnerable > 0:
            self.invulnerable -= 1
        if self.combo_timeout > 0:
            self.combo_timeout -= 1
        else:
            self.combo = 0

        for i, coin in enumerate(self.coins):
            if self.distance(self.player_x, self.player_y, coin[0], coin[1]) < 11:
                self.combo = min(5, self.combo + 1) if self.combo_timeout > 0 else 1
                self.combo_timeout = 75
                points = 10 * self.combo
                self.score += points
                self.collected += 1
                self.burst(coin[0], coin[1], 10, 13)
                self.coins[i] = self.random_position(20)
                pyxel.play(0, 0)
                if self.collected % 10 == 0:
                    self.frames_left += 5 * FPS
                    self.burst(self.player_x, self.player_y, 11, 17)
                    pyxel.play(1, 2)

        for bomb in self.bombs:
            bomb["x"] += bomb["vx"]
            bomb["y"] += bomb["vy"]
            if bomb["x"] < PLAY_LEFT + 8 or bomb["x"] > PLAY_RIGHT - 8:
                bomb["vx"] *= -1
                bomb["x"] = max(PLAY_LEFT + 8, min(PLAY_RIGHT - 8, bomb["x"]))
            if bomb["y"] < PLAY_TOP + 8 or bomb["y"] > PLAY_BOTTOM - 8:
                bomb["vy"] *= -1
                bomb["y"] = max(PLAY_TOP + 8, min(PLAY_BOTTOM - 8, bomb["y"]))
            if self.invulnerable == 0 and self.distance(
                self.player_x, self.player_y, bomb["x"], bomb["y"]
            ) < 11:
                self.lives -= 1
                self.invulnerable = 45
                self.combo = 0
                self.combo_timeout = 0
                self.burst(self.player_x, self.player_y, 8, 22)
                pyxel.play(0, 1)
                if self.lives == 0:
                    self.end_game()
                    return

        self.frames_left -= 1
        if self.frames_left <= 0:
            self.end_game()

    def end_game(self):
        self.state = "gameover"
        self.best = max(self.best, self.score)
        pyxel.play(0, 3)

    def draw_ground(self):
        pyxel.cls(1)
        pyxel.rect(0, PLAY_TOP - 1, WIDTH, HEIGHT - PLAY_TOP + 1, 3)
        for y in range(PLAY_TOP + 3, HEIGHT, 16):
            for x in range(1, WIDTH, 16):
                pyxel.pset(x + ((y // 16) % 2) * 5, y, 11)
        pyxel.rectb(PLAY_LEFT, PLAY_TOP, PLAY_RIGHT - PLAY_LEFT, PLAY_BOTTOM - PLAY_TOP, 7)
        pyxel.line(PLAY_LEFT + 1, PLAY_TOP + 1, PLAY_RIGHT - 1, PLAY_TOP + 1, 11)
        for x in range(20, WIDTH - 10, 40):
            pyxel.rect(x, HEIGHT - 9, 12, 3, 11)
            pyxel.rect(x + 5, HEIGHT - 12, 2, 3, 11)

    def draw_coin(self, x, y, tick):
        xi = int(x)
        yi = int(y)
        shimmer = 1 if (tick // 9) % 2 else 0
        pyxel.circ(xi, yi, 6, 4)
        pyxel.circ(xi, yi, 5, 10)
        pyxel.circb(xi, yi, 5, 9)
        pyxel.rect(xi - 1, yi - 3, 2, 6, 9)
        pyxel.pset(xi - 3, yi - 3, 7)
        if shimmer:
            pyxel.pset(xi + 7, yi - 6, 7)
            pyxel.pset(xi + 8, yi - 6, 7)
            pyxel.pset(xi + 7, yi - 5, 7)

    def draw_bomb(self, x, y):
        xi, yi = int(x), int(y)
        pyxel.circ(xi, yi, 6, 0)
        pyxel.circ(xi - 2, yi - 2, 3, 5)
        pyxel.circb(xi, yi, 6, 8)
        pyxel.line(xi + 2, yi - 5, xi + 4, yi - 9, 4)
        pyxel.pset(xi + 5, yi - 10, 10 if (self.frame // 5) % 2 else 8)
        pyxel.pset(xi - 2, yi - 2, 7)

    def draw_player(self):
        x, y = int(self.player_x), int(self.player_y)
        if self.invulnerable and self.frame % 5 < 3:
            return
        # shadow, boots, body and smiling face
        pyxel.ellib(x - 8, y + 5, 16, 5, 1)
        pyxel.rect(x - 6, y + 2, 5, 5, 2)
        pyxel.rect(x + 1, y + 2, 5, 5, 2)
        pyxel.rect(x - 7, y - 7, 14, 11, 12)
        pyxel.rect(x - 6, y - 10, 12, 4, 7)
        pyxel.rect(x - 4, y - 10, 3, 2, 10)
        pyxel.rect(x + 1, y - 10, 3, 2, 10)
        pyxel.pset(x - 3, y - 4, 0)
        pyxel.pset(x + 3, y - 4, 0)
        pyxel.line(x - 2, y, x + 2, y, 8)
        pyxel.pset(x - 2, y - 1, 8)
        pyxel.pset(x + 2, y - 1, 8)

    def draw_heart(self, x, y, filled):
        color = 8 if filled else 5
        pyxel.rect(x + 1, y + 1, 3, 3, color)
        pyxel.rect(x + 6, y + 1, 3, 3, color)
        pyxel.rect(x, y + 3, 10, 4, color)
        pyxel.rect(x + 2, y + 7, 6, 2, color)
        pyxel.rect(x + 4, y + 9, 2, 2, color)
        if filled:
            pyxel.pset(x + 2, y + 2, 14)

    def draw_hud(self):
        pyxel.rect(0, 0, WIDTH, PLAY_TOP - 1, 1)
        pyxel.rect(0, PLAY_TOP - 3, WIDTH, 2, 12)
        pyxel.text(8, 5, "COIN DASH", 10)
        pyxel.text(83, 5, "SCORE", 7)
        pyxel.text(83, 15, str(self.score), 10)
        pyxel.text(145, 5, "TIME", 7)
        remaining = max(0, math.ceil(self.frames_left / FPS))
        pyxel.text(145, 15, f"{remaining:02d}s", 10 if remaining > 10 else 8)
        for i in range(3):
            self.draw_heart(204 + i * 15, 11, i < self.lives)
        if self.combo > 1:
            pyxel.text(180, 24, f"x{self.combo} COMBO", 10)
        else:
            pyxel.text(8, 24, "+5 SEC / 10 COINS", 6)

    def center_text(self, text, y, color):
        pyxel.text((WIDTH - len(text) * 4) // 2, y, text, color)

    def panel(self, top, height):
        left, width = 39, WIDTH - 78
        pyxel.rect(left + 3, top + 4, width, height, 0)
        pyxel.rect(left, top, width, height, 1)
        pyxel.rectb(left, top, width, height, 7)
        pyxel.line(left + 1, top + 1, left + width - 2, top + 1, 12)

    def draw(self):
        self.draw_ground()
        if self.state != "title":
            for i, coin in enumerate(self.coins):
                self.draw_coin(coin[0], coin[1], self.frame + i * 4)
            for bomb in self.bombs:
                self.draw_bomb(bomb["x"], bomb["y"])
            self.draw_player()
            for p in self.particles:
                pyxel.rect(int(p[0]), int(p[1]), 2, 2, p[5])
            self.draw_hud()

        if self.state == "title":
            self.panel(35, 116)
            self.center_text("* COIN DASH *", 49, 10)
            self.center_text("COLLECT THE GOLD!", 68, 7)
            self.center_text("AVOID MOVING BOMBS", 79, 8)
            self.center_text("60 SEC  /  3 HEARTS", 94, 11)
            self.draw_coin(87, 115, self.frame)
            self.draw_coin(168, 115, self.frame)
            if (self.frame // 15) % 2 == 0:
                self.center_text("PRESS SPACE / A", 127, 10)
            self.center_text("MOVE: ARROWS / D-PAD", 161, 7)
        elif self.state == "paused":
            self.panel(72, 46)
            self.center_text("PAUSED", 86, 10)
            self.center_text("PRESS SPACE / A", 102, 7)
        elif self.state == "gameover":
            self.panel(56, 88)
            self.center_text("GAME OVER", 68, 8)
            self.center_text(f"SCORE: {self.score}", 88, 10)
            self.center_text(f"BEST: {self.best}", 102, 11)
            if (self.frame // 15) % 2 == 0:
                self.center_text("PRESS SPACE / A", 126, 7)


CoinDash()
