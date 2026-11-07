# title: Coin Dash - Skybound Run
# author: OpenAI
# desc: A pastel pixel-art scrolling platformer with jump, coins, and PWA touch controls
# license: MIT
# version: 2.0.1

"""A real horizontal-scrolling Pyxel platform game.

Desktop: LEFT/RIGHT or A/D to move, SPACE/UP/W to jump, P to pause.
Mobile: virtual D-pad LEFT/RIGHT, A to jump/start, B to pause.
"""

import math
import pyxel

WIDTH = 320
HEIGHT = 200
FPS = 30
GROUND_Y = 172
LEVEL_END = 4320
PLAYER_W = 15
PLAYER_H = 22
MOVE_SPEED = 2.75
GRAVITY = 0.34
JUMP_SPEED = -6.35
START_TIME = 100

# All artwork is original and uses Pyxel's built-in 16-color palette.
# 12 = blue sky; 6 = pale blue; 15 = peach; 10 = gold; 11 = mint.


class CoinDash:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Coin Dash - Skybound Run", fps=FPS)
        self.high_score = 0
        self.frames = 0
        self.state = "title"
        self.generate_level()
        self.start_session()
        self.state = "title"
        self.setup_sounds()
        pyxel.run(self.update, self.draw)

    def setup_sounds(self):
        pyxel.sounds[0].set("c3 e3 g3 c4", "p", "7755", "nnnn", 10)  # coin
        pyxel.sounds[1].set("c3 g3 c4", "t", "765", "nnn", 10)      # jump
        pyxel.sounds[2].set("e3 c3 g2", "n", "765", "nnf", 16)      # hit
        pyxel.sounds[3].set("c3 e3 g3 c4 e4 g4", "t", "777777", "nnnnnn", 10)
        pyxel.sounds[4].set("g3 e3 c3", "t", "765", "nnn", 16)

    def generate_level(self):
        # Short gaps can all be cleared with one jump. Platforms form
        # optional routes over the continuous low ground.
        self.gaps = [(705, 750), (1500, 1550), (2300, 2350), (3100, 3150), (3840, 3890)]
        self.platforms = []
        self.coin_spots = []
        for i in range(1, 55):
            x = 105 + i * 77
            top = (137, 148, 127, 142, 155, 133)[i % 6]
            width = (55, 66, 49, 61)[i % 4]
            # All platforms have a reachable top (< 50px above ground).
            self.platforms.append((x, top, width))
            self.coin_spots.append((x + width // 2, top - 16))
            if i % 3 == 0:
                self.coin_spots.append((x + width // 2 + 16, top - 31))
            if i % 2 == 0:
                self.coin_spots.append((x - 17, GROUND_Y - 16))
        self.coin_spots += [(x, GROUND_Y - 17) for x in range(75, LEVEL_END, 169)
                            if self.solid_ground(x)]
        # Friendly-looking dark creatures moving along the ground.
        self.enemy_origins = [450, 1040, 1840, 2630, 3480, 4050]
        self.clouds = [(i * 165 + (i % 3) * 43, 19 + (i * 29) % 94,
                        38 + (i % 4) * 13) for i in range(36)]

    def start_session(self):
        self.x = 35.0
        self.y = float(GROUND_Y - PLAYER_H)
        self.vy = 0.0
        self.grounded = True
        self.facing = 1
        self.camera_x = 0.0
        self.score = 0
        self.taken = set()
        self.lives = 3
        self.clock = START_TIME * FPS
        self.invincible = 0
        self.checkpoint = 35.0
        self.enemies = [{"x": float(x), "home": float(x), "d": 1 if i % 2 else -1}
                        for i, x in enumerate(self.enemy_origins)]
        self.particles = []
        self.state = "playing"

    def solid_ground(self, x):
        return not any(a <= x < b for a, b in self.gaps)

    @staticmethod
    def pressed(key):
        return pyxel.btn(key)

    @staticmethod
    def tapped(key):
        return pyxel.btnp(key)

    def any_pressed(self, *keys):
        return any(self.pressed(k) for k in keys)

    def any_tapped(self, *keys):
        return any(self.tapped(k) for k in keys)

    def jump_key(self):
        return self.any_tapped(pyxel.KEY_SPACE, pyxel.KEY_UP, pyxel.KEY_W,
                               pyxel.GAMEPAD1_BUTTON_A,
                               pyxel.GAMEPAD1_BUTTON_DPAD_UP)

    def start_key(self):
        return self.jump_key() or self.any_tapped(pyxel.KEY_RETURN)

    def pause_key(self):
        return self.any_tapped(pyxel.KEY_P, pyxel.GAMEPAD1_BUTTON_B)

    def sparkle(self, x, y, color=10, count=8):
        for i in range(count):
            angle = i * 6.28318 / count
            speed = 0.8 + (i % 3) * 0.35
            self.particles.append([float(x), float(y),
                                   math.cos(angle) * speed,
                                   math.sin(angle) * speed - 0.4,
                                   15 + (i % 5), color])

    def advance_particles(self):
        for particle in self.particles:
            particle[0] += particle[2]
            particle[1] += particle[3]
            particle[4] -= 1
        self.particles = [p for p in self.particles if p[4] > 0]

    def hit_player(self):
        if self.invincible > 0 or self.state != "playing":
            return
        self.lives -= 1
        self.invincible = 55
        self.sparkle(self.x + PLAYER_W / 2, self.y + 9, 8, 14)
        pyxel.play(1, 2)
        if self.lives <= 0:
            self.finish(False)
            return
        self.x = max(35.0, self.checkpoint)
        self.y = float(GROUND_Y - PLAYER_H)
        self.vy = 0
        self.grounded = True
        self.camera_x = max(0, self.x - WIDTH * 0.36)

    def finish(self, won):
        self.state = "win" if won else "gameover"
        self.high_score = max(self.high_score, self.score)
        pyxel.play(2, 3 if won else 4)

    def update(self):
        self.frames += 1
        self.advance_particles()
        if self.state in ("title", "gameover", "win"):
            if self.start_key():
                self.start_session()
                pyxel.play(0, 1)
            return
        if self.pause_key():
            self.state = "playing" if self.state == "paused" else "paused"
            return
        if self.state != "playing":
            return

        direction = int(self.any_pressed(pyxel.KEY_RIGHT, pyxel.KEY_D,
                                         pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)) - int(
                    self.any_pressed(pyxel.KEY_LEFT, pyxel.KEY_A,
                                     pyxel.GAMEPAD1_BUTTON_DPAD_LEFT))
        if direction:
            self.facing = 1 if direction > 0 else -1
        self.x = max(0.0, min(LEVEL_END - PLAYER_W, self.x + direction * MOVE_SPEED))
        if self.jump_key() and self.grounded:
            self.vy = JUMP_SPEED
            self.grounded = False
            pyxel.play(1, 1)
        previous_feet = self.y + PLAYER_H
        self.vy = min(7.0, self.vy + GRAVITY)
        self.y += self.vy
        self.grounded = False
        current_feet = self.y + PLAYER_H
        center = self.x + PLAYER_W / 2

        # One-way platforms: land only while falling through the upper surface.
        if self.vy >= 0:
            best = None
            for px, py, pw in self.platforms:
                if (px - PLAYER_W < self.x < px + pw and
                        previous_feet <= py + 3 and current_feet >= py):
                    if best is None or py < best:
                        best = py
            if (self.solid_ground(center) and
                    previous_feet <= GROUND_Y + 3 and current_feet >= GROUND_Y and
                    (best is None or GROUND_Y < best)):
                best = GROUND_Y
            if best is not None:
                self.y = float(best - PLAYER_H)
                self.vy = 0.0
                self.grounded = True

        if self.y > HEIGHT + 24:
            self.hit_player()
            if self.state != "playing":
                return
        if self.invincible > 0:
            self.invincible -= 1

        for idx, (cx, cy) in enumerate(self.coin_spots):
            if idx not in self.taken and abs(center - cx) < 12 and abs(
                    self.y + PLAYER_H / 2 - cy) < 14:
                self.taken.add(idx)
                self.score += 10
                self.sparkle(cx, cy, 10)
                pyxel.play(0, 0)
                if len(self.taken) % 10 == 0:
                    self.clock += 5 * FPS
                    self.sparkle(cx, cy, 7, 14)

        for enemy in self.enemies:
            enemy["x"] += enemy["d"] * 0.8
            if abs(enemy["x"] - enemy["home"]) > 26 or not self.solid_ground(enemy["x"]):
                enemy["d"] *= -1
            if self.invincible == 0 and abs(center - enemy["x"]) < 12 and abs(
                    self.y + PLAYER_H - (GROUND_Y - 4)) < 17:
                self.hit_player()
                if self.state != "playing":
                    return

        # Frequent checkpoints limit the punishment for mistakes on mobile.
        if self.grounded and self.x > self.checkpoint + 370:
            self.checkpoint = self.x
        if self.x >= LEVEL_END - 40:
            self.score += int(self.clock / FPS) * 2
            self.finish(True)
            return
        self.clock -= 1
        if self.clock <= 0:
            self.finish(False)
        target = max(0.0, min(LEVEL_END - WIDTH, self.x - WIDTH * 0.30))
        self.camera_x += (target - self.camera_x) * 0.17

    def cloud(self, x, y, width):
        # Crisp layered pastel clouds like the supplied reference image.
        x, y, width = int(x), int(y), int(width)
        if x > WIDTH + width or x + width < -width:
            return
        pyxel.rect(x + 2, y + 5, width + 5, 9, 6)
        pyxel.rect(x + 8, y + 2, width - 6, 11, 6)
        pyxel.rect(x + 16, y, width - 23, 6, 6)
        pyxel.rect(x + 5, y + 7, width + 1, 6, 15)
        pyxel.rect(x + 12, y + 4, width - 7, 7, 15)
        pyxel.rect(x + 22, y + 2, max(4, width - 28), 4, 15)

    def sky(self):
        pyxel.cls(12)
        # Far-off drifting clouds: different speeds create parallax.
        for cx, cy, cw in self.clouds:
            sx = cx - self.camera_x * 0.20
            if -cw - 15 < sx < WIDTH + 15:
                self.cloud(sx, cy, cw)
        # Distant mountain peaks and soft snowcaps.
        mountain_shift = int(self.camera_x * 0.32)
        for i in range(-1, 17):
            x = i * 85 - mountain_shift % 85
            top = 147 + (i % 3) * 5
            pyxel.tri(x - 39, GROUND_Y, x + 21, top, x + 85, GROUND_Y, 5)
            pyxel.tri(x + 4, top + 7, x + 21, top, x + 38, top + 9, 7)
            pyxel.rect(x + 15, top + 6, 11, 3, 6)
        # Checker / snow stripe across the horizon.
        horizon_scroll = int(self.camera_x * 0.47)
        for x in range(-10, WIDTH + 12, 12):
            px = x - (horizon_scroll % 12)
            pyxel.rect(px, 159, 7, 3, 6)
            pyxel.rect(px + 6, 162, 6, 3, 7)
            pyxel.rect(px + 2, 166, 6, 2, 15)

    def draw_ground(self):
        cam = int(self.camera_x)
        left_cell = max(0, cam // 12 - 2)
        right_cell = min(LEVEL_END // 12 + 2, (cam + WIDTH) // 12 + 3)
        for cell in range(left_cell, right_cell + 1):
            wx = cell * 12
            sx = wx - cam
            if not self.solid_ground(wx + 6):
                continue
            pyxel.rect(sx, GROUND_Y, 12, HEIGHT - GROUND_Y, 3)
            pyxel.rect(sx, GROUND_Y, 12, 3, 11)
            pyxel.rect(sx, GROUND_Y + 3, 12, 5, 15)
            pyxel.rect(sx, GROUND_Y + 8, 12, 3, 6)
            pyxel.rect(sx, GROUND_Y + 11, 12, 2, 15)
            if cell % 3 == 0:
                pyxel.rect(sx, GROUND_Y + 16, 5, 3, 11)
            elif cell % 3 == 1:
                pyxel.rect(sx + 6, GROUND_Y + 20, 5, 3, 11)
            else:
                pyxel.rect(sx + 1, GROUND_Y + 24, 4, 2, 5)
            pyxel.rect(sx + 2, GROUND_Y + 1, 4, 1, 7)
        # Grass tips silhouette along each solid portion.
        for wx in range(cam // 8 * 8 - 8, cam + WIDTH + 8, 8):
            if self.solid_ground(wx + 4):
                sx = wx - cam
                pyxel.rect(sx + 1, GROUND_Y - 2 - (wx // 8 % 2), 4, 4, 11)
                pyxel.rect(sx + 3, GROUND_Y - 4 - (wx // 8 % 3), 2, 3, 11)

    def draw_platform(self, wx, wy, width):
        sx = int(wx - self.camera_x)
        if sx > WIDTH or sx + width < 0:
            return
        pyxel.rect(sx, wy + 1, width, 15, 2)
        pyxel.rect(sx, wy + 1, width, 4, 9)
        pyxel.rect(sx, wy + 4, width, 3, 15)
        pyxel.rect(sx, wy + 7, width, 9, 4)
        for segment in range(0, width, 16):
            px = sx + segment
            size = min(15, width - segment)
            pyxel.rect(px, wy + 8, size, 6, 4)
            pyxel.rect(px + 2, wy + 10, min(3, max(0, size - 3)), 3, 14)
            if segment:
                pyxel.rect(px - 1, wy + 7, 2, 9, 2)
                pyxel.rect(px, wy + 1, 2, 5, 10)
        pyxel.rect(sx, wy, width, 2, 15)

    def draw_coin(self, wx, wy, tick):
        x = int(wx - self.camera_x)
        y = int(wy + math.sin(tick * 0.10) * 2)
        if x < -12 or x > WIDTH + 12:
            return
        pyxel.circ(x, y, 9, 1)
        pyxel.circ(x, y, 7, 9)
        pyxel.circ(x - 1, y - 1, 6, 10)
        pyxel.rect(x - 5, y - 4, 3, 4, 7)
        pyxel.rect(x + 4, y + 2, 2, 3, 9)
        pyxel.line(x - 5, y + 5, x + 3, y + 6, 9)
        if (tick // 9) % 2 == 0:
            pyxel.pset(x - 7, y - 8, 7)
            pyxel.pset(x - 7, y - 6, 7)
            pyxel.pset(x - 9, y - 7, 7)

    def draw_enemy(self, enemy):
        x = int(enemy["x"] - self.camera_x)
        if x < -15 or x > WIDTH + 15:
            return
        y = GROUND_Y - 11
        pyxel.rect(x - 7, y, 14, 9, 1)
        pyxel.rect(x - 5, y - 3, 10, 5, 2)
        pyxel.rect(x - 4, y + 2, 3, 3, 7)
        pyxel.rect(x + 2, y + 2, 3, 3, 7)
        pyxel.rect(x - 6, y + 8, 3, 3, 2)
        pyxel.rect(x + 3, y + 8, 3, 3, 2)

    def draw_player(self):
        if self.invincible and self.frames % 6 < 3:
            return
        sx = int(self.x - self.camera_x)
        sy = int(self.y)
        running = self.grounded and self.any_pressed(pyxel.KEY_LEFT, pyxel.KEY_RIGHT,
                pyxel.KEY_A, pyxel.KEY_D, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT,
                pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
        step = (self.frames // 5) % 2 if running else 0
        # Crisp 15x22 sprite, teal jacket, short hair, bright boots.
        if self.grounded:
            pyxel.elli(sx + 2, sy + 20, 12, 3, 5)
        # Brown hair with dark border and peach face.
        pyxel.rect(sx + 4, sy + 1, 9, 3, 1)
        pyxel.rect(sx + 3, sy + 4, 11, 6, 1)
        pyxel.rect(sx + 5, sy + 4, 8, 6, 15)
        pyxel.rect(sx + 4, sy + 2, 8, 3, 9)
        pyxel.rect(sx + 3, sy + 4, 2, 5, 9)
        eye_x = sx + (11 if self.facing == 1 else 6)
        pyxel.pset(eye_x, sy + 7, 1)
        # Teal jacket, red scarf, navy outlines.
        pyxel.rect(sx + 3, sy + 10, 11, 8, 1)
        pyxel.rect(sx + 4, sy + 11, 9, 6, 3)
        pyxel.rect(sx + 7, sy + 11, 2, 7, 14)
        pyxel.rect(sx + 1, sy + (10 if not self.grounded else 13), 3, 5, 1)
        pyxel.rect(sx + 1, sy + (11 if not self.grounded else 14), 2, 3, 3)
        pyxel.rect(sx + 13, sy + (10 if not self.grounded else 13), 3, 5, 1)
        pyxel.rect(sx + 14, sy + (11 if not self.grounded else 14), 2, 3, 3)
        # Animated running legs.
        if not self.grounded:
            pyxel.rect(sx + 5, sy + 17, 4, 3, 5)
            pyxel.rect(sx + 9, sy + 17, 4, 4, 5)
            pyxel.rect(sx + 3, sy + 19, 6, 3, 8)
            pyxel.rect(sx + 10, sy + 20, 5, 2, 8)
        else:
            pyxel.rect(sx + 5, sy + 17, 4, 4, 5)
            pyxel.rect(sx + 10, sy + 17, 4, 4, 5)
            pyxel.rect(sx + 3 - 2 * step, sy + 20, 7, 2, 8)
            pyxel.rect(sx + 9 + 2 * step, sy + 20, 7, 2, 8)

    def draw_flag(self):
        sx = int(LEVEL_END - 35 - self.camera_x)
        if sx < -20 or sx > WIDTH + 30:
            return
        pyxel.rect(sx, GROUND_Y - 76, 3, 75, 7)
        pyxel.rect(sx - 3, GROUND_Y - 2, 9, 3, 1)
        pyxel.tri(sx + 3, GROUND_Y - 75,
                  sx + 34, GROUND_Y - 65, sx + 3, GROUND_Y - 55, 8)
        pyxel.rect(sx + 5, GROUND_Y - 70, 11, 3, 14)

    def hud(self):
        pyxel.text(8, 7, "SCORE", 1)
        pyxel.text(7, 6, "SCORE", 7)
        pyxel.text(38, 7, str(self.score).zfill(5), 1)
        pyxel.text(37, 6, str(self.score).zfill(5), 7)
        pyxel.text(108, 6, "COINS " + str(len(self.taken)), 7)
        pyxel.text(196, 6, "TIME " + str(max(0, math.ceil(self.clock / FPS))), 7)
        for i in range(3):
            x = 282 + i * 12
            pyxel.rect(x, 6, 3, 3, 8 if i < self.lives else 5)
            pyxel.rect(x + 4, 6, 3, 3, 8 if i < self.lives else 5)
            pyxel.rect(x - 1, 9, 9, 3, 8 if i < self.lives else 5)
            pyxel.rect(x + 1, 12, 5, 2, 8 if i < self.lives else 5)
        # Level progression along bottom edge.
        pyxel.rect(0, HEIGHT - 2, WIDTH, 2, 1)
        pyxel.rect(0, HEIGHT - 2, int(WIDTH * self.x / LEVEL_END), 2, 10)

    def center(self, text, y, color=7):
        pyxel.text((WIDTH - len(text) * 4) // 2, y, text, color)

    def popup(self, title, subtitle, prompt):
        x, y, w, h = 63, 51, WIDTH - 126, 96
        pyxel.rect(x + 4, y + 5, w, h, 1)
        pyxel.rect(x, y, w, h, 5)
        pyxel.rect(x + 3, y + 3, w - 6, h - 6, 1)
        pyxel.rectb(x, y, w, h, 7)
        self.center(title, y + 15, 10)
        self.center(subtitle, y + 38, 7)
        self.center(prompt, y + 66, 15 if self.frames % 34 < 22 else 7)

    def draw(self):
        self.sky()
        self.draw_ground()
        for x, y, width in self.platforms:
            if -80 < x - self.camera_x < WIDTH + 25:
                self.draw_platform(x, y, width)
        for i, (x, y) in enumerate(self.coin_spots):
            if i not in self.taken and -20 < x - self.camera_x < WIDTH + 20:
                self.draw_coin(x, y, self.frames + i * 3)
        for enemy in self.enemies:
            self.draw_enemy(enemy)
        self.draw_flag()
        self.draw_player()
        for x, y, _, _, _, color in self.particles:
            sx = int(x - self.camera_x)
            if -3 < sx < WIDTH + 3:
                pyxel.rect(sx, int(y), 2, 2, color)
        self.hud()
        if self.state == "title":
            self.popup("COIN DASH", "SKYBOUND PIXEL ADVENTURE", "PRESS SPACE / A TO START")
            self.center("MOVE: LEFT RIGHT   JUMP: SPACE / A", 160, 1)
        elif self.state == "paused":
            self.popup("PAUSED", "TAKE A BREAK", "PRESS P / B TO CONTINUE")
        elif self.state == "gameover":
            self.popup("GAME OVER", "SCORE " + str(self.score) + "   BEST " + str(self.high_score),
                       "PRESS SPACE / A TO RETRY")
        elif self.state == "win":
            self.popup("LEVEL CLEAR!", "SCORE " + str(self.score) + "   BEST " + str(self.high_score),
                       "PRESS SPACE / A TO REPLAY")


CoinDash()
