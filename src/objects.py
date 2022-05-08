import os
import sys
import random
import pygame
from src.sprites import Boss
from src.variables import *


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class Background:
    def __init__(self) -> None:
        """initialize background"""
        self.width, self.height = WIDTH, HEIGHT
        self.gamew, self.gameh = GAME_WIDTH, GAME_HEIGHT
        self.image = pygame.Surface((self.width, self.height))
        self.stars = [
            [
                random.randrange(self.width),
                random.randrange(self.height),
                random.random() / 20,
            ]
            for i in range(N_STARS)
        ]

    def update(self, dt: int, playing=False) -> None:
        """update the background and move the stars"""
        self.image.fill(BLACK)
        for star in self.stars:
            pygame.draw.line(self.image, WHITE, (star[0], star[1]), (star[0], star[1]))
            star[1] += star[2] * dt
            if star[1] > self.height:
                star[0] = random.randrange(self.width)
                star[1] = 0
        if playing:
            pygame.draw.line(
                self.image,
                RED,
                (20, self.gameh - 20),
                (self.gamew - 20, self.gameh - 20),
                3,
            )


class SideBar:
    def __init__(self) -> None:
        """initialize the side bar"""
        self.width, self.height = SIDE_WIDTH, HEIGHT
        self.image = pygame.Surface((self.width, self.height))
        self.x, self.y = GAME_WIDTH, 0

    def update(
        self,
        life: int,
        score1: int,
        highscore="-----",
        score2="-----",
        name1=None,
        name2=None,
    ) -> None:
        """update the side bar"""
        self.image.fill(BLACK)
        pygame.draw.line(self.image, WHITE, (3, 0), (3, self.height), 3)

        # create objects for the side bar
        score1_obj = Text("SCORE-1:" if name1 is None else name1, WHITE)
        score1_obj.x = self.width / 2 - score1_obj.width / 2
        score1_obj.y = 10

        score1_v_obj = Text(str(score1).zfill(5), WHITE)
        score1_v_obj.x = self.width / 2 - score1_v_obj.width / 2
        score1_v_obj.y = 10 + score1_obj.height

        hscore_obj = Text("HI-SCORE:", WHITE)
        hscore_obj.x = self.width / 2 - hscore_obj.width / 2
        hscore_obj.y = 10 + score1_obj.height * 3

        hscore_v_obj = Text(str(highscore).zfill(5), WHITE)
        hscore_v_obj.x = self.width / 2 - hscore_v_obj.width / 2
        hscore_v_obj.y = 10 + score1_obj.height * 4

        score2_obj = Text("SCORE-2:" if name2 is None else name2, WHITE)
        score2_obj.x = self.width / 2 - score2_obj.width / 2
        score2_obj.y = 10 + score1_obj.height * 6

        score2_v_obj = Text(str(score2).zfill(5), WHITE)
        score2_v_obj.x = self.width / 2 - score2_v_obj.width / 2
        score2_v_obj.y = 10 + score1_obj.height * 7

        life_obj = Text("LIFE:", WHITE)
        life_obj.x = self.width / 2 - life_obj.width / 2
        life_obj.y = self.height - life_obj.height * 2 - 20

        life_v_obj = Image(f"life{life}")
        life_v_obj.x = self.width / 2 - life_v_obj.width / 2
        life_v_obj.y = self.height - life_v_obj.height - 20

        # blit objects
        self.image.blit(score1_obj.image, (score1_obj.x, score1_obj.y))
        self.image.blit(score1_v_obj.image, (score1_v_obj.x, score1_v_obj.y))
        self.image.blit(hscore_obj.image, (hscore_obj.x, hscore_obj.y))
        self.image.blit(hscore_v_obj.image, (hscore_v_obj.x, hscore_v_obj.y))
        self.image.blit(score2_obj.image, (score2_obj.x, score2_obj.y))
        self.image.blit(score2_v_obj.image, (score2_v_obj.x, score2_v_obj.y))
        self.image.blit(life_obj.image, (life_obj.x, life_obj.y))
        self.image.blit(life_v_obj.image, (life_v_obj.x, life_v_obj.y))


class BossHealthBar:
    def __init__(self) -> None:
        """initialize the boss health bar"""
        self.width, self.height = GAME_WIDTH - 20, 30
        self.image = pygame.Surface((self.width, self.height))
        self.x, self.y = 10, 0

    def update(self, boss) -> None:
        """update the boss health bar"""
        self.image.fill(WHITE)
        pygame.draw.line(
            self.image,
            BLACK,
            (3, self.height / 2 - 1),
            (self.width - 3 - 1, self.height / 2 - 1),
            24,
        )
        pygame.draw.line(
            self.image,
            PURPLE,
            (3, self.height / 2 - 1),
            (
                (self.width - 3)
                / 10
                * (boss.life if isinstance(boss, Boss) else boss["life"])
                - 1,
                self.height / 2 - 1,
            ),
            24,
        )
        # set the y position of the health bar depending on the boss
        self.y = (boss.y if isinstance(boss, Boss) else boss["y"]) - self.height - 10


class Text:
    def __init__(self, text: str, color: tuple) -> None:
        """initialize the text"""
        self.text = text
        self.color = color
        self.font = pygame.font.Font(resource_path("src/assets/fonts/retro.ttf"), 30)

        self.image = self.render()
        self.width, self.height = self.image.get_size()
        self.x, self.y = 0, 0

    def change_text(self, text: str) -> None:
        """change the text of the text object"""
        self.text = text
        self.image = self.render()
        self.width, self.height = self.image.get_size()

    def change_color(self, color: tuple) -> None:
        """change the color of the text object"""
        self.color = color
        self.image = self.render()

    def render(self) -> pygame.Surface:
        """render the text object"""
        image = self.font.render(self.text, True, self.color)
        if len(self.color) == 4:
            image.set_alpha(self.color[3])
        return image


class Image:
    def __init__(self, image_name: str) -> None:
        """initialize the image"""
        self.image = self.find_image(image_name)
        self.width, self.height = self.image.get_size()
        self.x, self.y = 0, 0

    def find_image(self, image_name: str) -> None:
        """find the image"""
        image_path = resource_path(f"src/assets/images/{image_name}.png")
        return pygame.image.load(image_path).convert_alpha()


class Sound:
    def __init__(self) -> None:
        """initialize the sound"""
        self.mixer = pygame.mixer
        self.mixer.music.set_volume(1)

        self.play_soundtrack()

    def play_soundtrack(self) -> None:
        """play the soundtrack"""
        sound_path = resource_path("src/assets/sounds/soundtrack.wav")
        self.mixer.music.load(sound_path)
        self.mixer.music.play(-1)

    def play(self, sound: str) -> None:
        """play a sound"""
        sound_path = resource_path(f"src/assets/sounds/{sound}.wav")
        channel = self.mixer.find_channel()
        channel.set_volume(0.2)
        channel.play(self.mixer.Sound(sound_path))
