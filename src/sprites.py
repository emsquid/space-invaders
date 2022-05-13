import random
from threading import Timer
from src.variables import *


class Sprite:
    def __init__(self) -> None:
        """initialize sprite"""
        self.gamew, self.gameh = GAME_WIDTH, GAME_HEIGHT

        self.image_name = ""
        self.width, self.height = 0, 0
        self.x, self.y = 0, 0

    def collide(self, other) -> bool:
        """check if two sprites collide"""
        if self.x + self.width > other.x and self.x < other.x + other.width:
            if self.y + self.height > other.y and self.y < other.y + other.height:
                return True
        return False


class Player(Sprite):
    def __init__(self) -> None:
        """initialize player"""
        super().__init__()
        # set sprite attributes
        self.image_name = f"spaceship0"
        self.width, self.height = 64, 64
        self.x, self.y = self.gamew // 2 - self.width // 2, self.gameh - 100
        # set player attributes
        self.direction = ""
        self.speed = self.gamew / (4000)  # ref 0.2
        self.life = 3
        self.score = 0

    def change_style(self, style: int) -> None:
        """change player style"""
        self.image_name = f"spaceship{style}"

    def move(self, dt: int) -> None:
        """move player"""
        if self.direction == "left" and self.x > 0:
            self.x -= self.speed * dt
        elif self.direction == "right" and self.x + self.width < self.gamew:
            self.x += self.speed * dt

    def add_points(self, points: int) -> None:
        """add points to the player score"""
        self.score += points


class Invader(Sprite):
    def __init__(self) -> None:
        """initialize invader"""
        super().__init__()
        self.type = random.randrange(4)
        # set sprite attributes
        self.image_name = f"invader{self.type}"
        self.width, self.height = (66, 54)
        self.x, self.y = (
            random.randrange(0, self.gamew - self.width),
            random.randrange(-4 * self.height, -self.height),
        )
        # set invader attributes
        # ref [0.05, 0.06, 0.07, 0.08]
        self.speed = self.gameh / [15000, 12500, 10715, 9375][self.type]
        self.dx = (random.random() * random.randrange(-1, 2, 2)) * self.speed / 2

    def increase_speed(self) -> None:
        """increase invader speed"""
        self.speed *= 1.1

    def die(self) -> None:
        """kill invader and make it repop"""
        self.__init__()

    def move(self, dt: int) -> None:
        """move invader"""
        self.y += self.speed * dt
        self.x = min(max(self.x + (self.dx * dt), 0), self.gamew - self.width)
        if self.x <= 0 or self.x + self.width >= self.gamew:
            self.dx = -self.dx

    def crash(self) -> bool:
        """check if invader crashed"""
        return self.y + self.height > self.gameh - 20


class Boss(Sprite):
    def __init__(self) -> None:
        """initialize boss"""
        super().__init__()
        # set sprite attributes
        self.image_name = "boss"
        self.width, self.height = 256, 101
        self.x, self.y = self.gamew // 2 - self.width // 2, -self.height
        # set boss attributes
        self.speed = self.gameh / 12500
        self.life = 10
        self.alive = False

    def appear(self) -> None:
        """make boss appear"""
        self.alive = True
        self.life = 10

    def die(self) -> None:
        """kill boss"""
        self.alive = False

    def move(self, dt: int) -> None:
        """move boss"""
        if self.alive:
            if self.y < 50:
                self.y += abs(self.speed) * dt
            else:
                self.x = min(
                    max(self.x + (self.speed * dt), 0), self.gamew - self.width
                )
                if self.x <= 0 or self.x + self.width >= self.gamew:
                    self.speed = -self.speed
        else:
            if self.y > -self.height:
                self.y -= abs(self.speed) * dt
            else:
                self.x = self.gamew // 2 - self.width // 2


class Laser(Sprite):
    def __init__(self, player: Player) -> None:
        """initialize laser"""
        super().__init__()
        self.player = player
        # set sprite attributes
        self.image_name = "laser"
        self.width, self.height = 8, 46
        self.x, self.y = (
            self.player.x + self.player.width // 2 - self.width // 2,
            self.player.y,
        )
        # set laser attributes
        self.shot = False
        self.speed = self.gameh / 2150  # ref 0.35

    def move(self, dt: int) -> None:
        """move laser"""
        if not self.shot:
            self.x = self.player.x + self.player.width // 2 - self.width // 2
        else:
            self.y -= self.speed * dt

    def shoot(self) -> None:
        """shoot laser"""
        self.shot = True


class Bomb(Sprite):
    def __init__(self, boss: Boss) -> None:
        """initialize bomb"""
        super().__init__()
        self.boss = boss
        # set sprite attributes
        self.image_name = "bomb"
        self.width, self.height = 32, 62
        self.x, self.y = (
            self.boss.x + self.boss.width // 2 - self.width // 2,
            self.boss.y,
        )
        # set bomb attributes
        self.speed = self.gameh / 6500

    def move(self, dt: int) -> None:
        """move bomb"""
        self.y += self.speed * dt


class Explosion(Sprite):
    def __init__(self, x: int, y: int, lifetime: int) -> None:
        """initialize explosion"""
        super().__init__()
        # set sprite attributes
        self.image_name = "explode"
        self.width, self.height = 64, 64
        self.x, self.y = x, y
        # set explosion attributes
        self.over = False
        Timer(lifetime, self.set_over).start()

    def set_over(self) -> None:
        """set explosion to over"""
        self.over = True
