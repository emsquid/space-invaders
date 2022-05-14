import os
import contextlib
from time import time
from _thread import start_new_thread

# import pygame silently
with contextlib.redirect_stdout(None):
    import pygame


# personal modules
from src.config import *
from src.objects import *
from src.engines import *
from src.data import *
from src.online import *
from src.variables import *


class Game:
    def __init__(self) -> None:
        pygame.init()

        self.running = True
        self.width, self.height = WIDTH, HEIGHT

        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.RESIZABLE
        )
        pygame.display.set_icon(Image("icon").image)
        pygame.display.set_caption("Space Invaders")

        self.background = Background()
        self.sidebar = SideBar()
        self.bosshealthbar = BossHealthBar()
        self.sound = Sound()
        self.clock = pygame.time.Clock()

        self.server = Server()
        self.client = Client()
        self.data = Data()
        self.config = Config()

        self.online = False
        start_new_thread(self.check_connection, ())

        self.last_ip = ""

    # connection methods
    def check_connection(self) -> None:
        """check if app can connect to internet, loop every second"""
        Timer(1, self.check_connection).start()

        # variable to compare after
        online_before = self.online
        # check if online
        self.online = check_connection()
        # if online and not before
        if self.online and not online_before:
            if not self.data.connected:
                self.data.connect_to_db()
            if self.server.running:
                self.server.close()
            if self.client.connected:
                self.client.disconnect()
        # if not online and before
        elif not self.online and online_before:
            if self.data.connected:
                self.data.disconnect_from_db()

        # updates
        self.data.fetch_scores()

    # run and exit methods
    def run(self) -> None:
        """run the game"""
        if self.config.get():
            self.menu()
        else:
            self.welcome_screen()

    def exit(self) -> None:
        """exit"""
        self.config.save()
        self.running = False
        pygame.quit()
        os._exit(0)

    # draw and play_sounds methods
    def draw_game(self, *objects) -> None:
        """draw the game screen"""
        for obj in objects:
            if (
                isinstance(obj, Image)
                or isinstance(obj, Text)
                or isinstance(obj, SideBar)
                or isinstance(obj, BossHealthBar)
                or isinstance(obj, Notification)
            ):
                self.background.image.blit(obj.image, (obj.x, obj.y))
            elif isinstance(obj, dict):
                image = Image(obj["image_name"])
                self.background.image.blit(image.image, (obj["x"], obj["y"]))
            elif obj is not None:
                image = Image(obj.image_name)
                self.background.image.blit(image.image, (obj.x, obj.y))

        game = pygame.transform.scale(self.background.image, self.screen.get_size())
        self.screen.blit(game, (0, 0))

    def play_sounds(self, *sounds) -> None:
        """play sounds"""
        for sound in sounds:
            self.sound.play(sound)

    # welcome, menu, and game over screens
    def welcome_screen(self) -> None:
        """welcome screen, ask player to enter their name"""
        title_obj = Image("title")
        title_obj.x = self.width / 2 - title_obj.width / 2
        title_obj.y = self.height / 4 - title_obj.height / 2.5

        text_obj = Text("ENTER YOUR NAME:", WHITE)
        text_obj.x = self.width / 2 - text_obj.width / 2
        text_obj.y = self.height * 0.75 - text_obj.height * 2

        input_obj = Text("", GREEN)

        credits_obj = Text("©EMANUEL", WHITE)
        credits_obj.x = self.width / 2 - credits_obj.width / 2
        credits_obj.y = self.height - credits_obj.height - 10

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if self.config.name == "":
                            self.error_screen("PLEASE ENTER A NAME", "welcome")
                        else:
                            self.menu()

                    elif event.key == pygame.K_BACKSPACE:
                        self.config.name = self.config.name[:-1]

                    elif event.unicode.isalnum() and len(self.config.name) < 16:
                        self.config.name += event.unicode.upper()

            # updates
            dt = self.clock.tick(60)

            self.background.update(dt, playing=False)
            input_obj.change_text(self.config.name + ("_" if time() % 1 > 0.5 else ""))
            input_obj.x = self.width / 2 - input_obj.width / 2
            input_obj.y = self.height * 0.75

            # display
            self.draw_game(title_obj, text_obj, input_obj, credits_obj)

            pygame.display.update()

    def menu(self) -> None:
        """menu screen of the game"""
        title_obj = Image("title")
        title_obj.x = self.width / 2 - title_obj.width / 2
        title_obj.y = self.height / 4 - title_obj.height / 2.5

        single_obj = Text("SINGLE PLAYER", WHITE)
        single_obj.x = self.width / 2 - single_obj.width / 2
        single_obj.y = self.height * 0.75 - single_obj.height * 4

        local_obj = Text("LOCAL MULTI", WHITE)
        local_obj.x = self.width / 2 - local_obj.width / 2
        local_obj.y = self.height * 0.75 - local_obj.height * 2.5

        online_obj = Text("ONLINE MULTI", WHITE)
        online_obj.x = self.width / 2 - online_obj.width / 2
        online_obj.y = self.height * 0.75 - online_obj.height

        leaderboard_obj = Text("LEADERBOARD", WHITE)
        leaderboard_obj.x = self.width / 2 - leaderboard_obj.width / 2
        leaderboard_obj.y = self.height * 0.75 + leaderboard_obj.height / 2

        settings_obj = Text("SETTINGS", WHITE)
        settings_obj.x = self.width / 2 - settings_obj.width / 2
        settings_obj.y = self.height * 0.75 + settings_obj.height * 2

        connection_obj = Text("CONNECTED:", WHITE)
        connection_obj.x = 10
        connection_obj.y = self.height - connection_obj.height - 10

        credits_obj = Text("©EMANUEL", WHITE)
        credits_obj.x = self.width - credits_obj.width - 10
        credits_obj.y = self.height - credits_obj.height - 10

        arrow = Image("arrow")

        # show fps at the top right corner

        selected = 0

        while self.running:
            # events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == self.config.controls["up"] and selected > 0:
                        if not self.online and selected == 4:
                            selected = 1
                        else:
                            selected -= 1
                    elif event.key == self.config.controls["down"] and selected < 4:
                        if selected < 1 or self.online:
                            selected += 1
                        elif selected == 1 and not self.online:
                            selected = 4

                    elif event.key == self.config.controls["enter"]:
                        if selected == 0:
                            self.single_player()
                        elif selected == 1:
                            self.local_multi_player()
                        elif selected == 2:
                            self.host_or_join()
                        elif selected == 3:
                            self.leaderboard()
                        elif selected == 4:
                            self.settings()

            # check
            if not self.online and 1 < selected < 4:
                selected = 0

            # updates
            dt = self.clock.tick(60)

            self.background.update(dt)

            single_obj.change_color(RED if selected == 0 else WHITE)
            local_obj.change_color(RED if selected == 1 else WHITE)
            online_obj.change_color(
                INACTIVE_GREY if not self.online else RED if selected == 2 else WHITE
            )
            leaderboard_obj.change_color(
                INACTIVE_GREY if not self.online else RED if selected == 3 else WHITE
            )
            settings_obj.change_color(RED if selected == 4 else WHITE)

            if selected == 0:
                arrow.x = single_obj.x - arrow.width - 15
                arrow.y = single_obj.y + 4
            elif selected == 1:
                arrow.x = local_obj.x - arrow.width - 15
                arrow.y = local_obj.y + 4
            elif selected == 2 and self.online:
                arrow.x = online_obj.x - arrow.width - 15
                arrow.y = online_obj.y + 4
            elif selected == 3 and self.online:
                arrow.x = leaderboard_obj.x - arrow.width - 15
                arrow.y = leaderboard_obj.y + 4
            elif selected == 4:
                arrow.x = settings_obj.x - arrow.width - 15
                arrow.y = settings_obj.y + 4

            connection_v_obj = Text("YES", GREEN) if self.online else Text("NO", RED)
            connection_v_obj.x = connection_obj.x + connection_obj.width + 5
            connection_v_obj.y = self.height - connection_v_obj.height - 10

            # display
            self.draw_game(
                title_obj,
                single_obj,
                local_obj,
                online_obj,
                leaderboard_obj,
                settings_obj,
                arrow,
                connection_obj,
                connection_v_obj,
                credits_obj,
            )

            pygame.display.update()

    def game_over(
        self, score1: int, score2: int, original_mode: str, name1=None, name2=None
    ) -> None:
        """game over screen"""
        # save score
        if original_mode == "single":
            name = self.config.name
            score = score1
            mode = "single"
        elif original_mode in ("local_multi", "online_multi"):
            if name1 == name2 == None:
                name = self.config.name
            else:
                f"{name1[:4]}. & {name2[:4]}."
            score = score1 + score2
            mode = "multi"
        self.data.save_score(name, score, mode)

        over_obj = Text("GAME OVER !!!", RED)
        over_obj.x = self.width / 2 - over_obj.width / 2
        over_obj.y = self.height / 4 - over_obj.height * 3

        score1_obj = Text(
            f"{name1 if not name1 is None else 'SCORE' if original_mode=='single'  else 'SCORE-1'}: {score1}",
            WHITE,
        )
        score1_obj.x = self.width / 2 - score1_obj.width / 2
        score1_obj.y = self.height / 4 - score1_obj.height

        score2_obj = Text(
            f"{name2 if not name2 is None else 'HI-SCORE' if original_mode=='single'  else 'SCORE-2'}: {score2}",
            WHITE,
        )
        score2_obj.x = self.width / 2 - score2_obj.width / 2
        score2_obj.y = self.height / 4 + score2_obj.height

        spaceship = Image(f"spaceship{self.config.style}")
        spaceship.x = self.width / 2 - spaceship.width / 2
        spaceship.y = self.height / 2 - spaceship.height / 2 - 20

        retry_obj = Text("RETRY", WHITE)
        retry_obj.x = self.width / 2 - retry_obj.width / 2
        retry_obj.y = self.height * 0.75 - retry_obj.height * 3

        menu_obj = Text("MENU", WHITE)
        menu_obj.x = self.width / 2 - menu_obj.width / 2
        menu_obj.y = self.height * 0.75 - menu_obj.height

        quit_obj = Text("QUIT", WHITE)
        quit_obj.x = self.width / 2 - quit_obj.width / 2
        quit_obj.y = self.height * 0.75 + quit_obj.height

        credits_obj = Text("©EMANUEL", WHITE)
        credits_obj.x = self.width / 2 - credits_obj.width / 2
        credits_obj.y = self.height - credits_obj.height - 10

        arrow = Image("arrow")

        selected = 0

        while self.running:
            # events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == self.config.controls["up"] and selected > 0:
                        selected -= 1
                    if event.key == self.config.controls["down"] and selected < 2:
                        selected += 1
                    if event.key == self.config.controls["enter"]:
                        if selected == 0:
                            if original_mode == "single":
                                self.single_player()
                            elif original_mode == "local_multi":
                                self.local_multi_player()
                            elif original_mode == "online_multi":
                                if self.server.running:
                                    self.host()
                                else:
                                    self.join()
                        elif selected == 1:
                            self.menu()
                        elif selected == 2:
                            self.exit()

            # updates
            dt = self.clock.tick(60)

            self.background.update(dt)

            retry_obj.change_color(RED if selected == 0 else WHITE)
            menu_obj.change_color(RED if selected == 1 else WHITE)
            quit_obj.change_color(RED if selected == 2 else WHITE)

            if selected == 0:
                arrow.x = retry_obj.x - arrow.width - 15
                arrow.y = retry_obj.y + 4
            elif selected == 1:
                arrow.x = menu_obj.x - arrow.width - 15
                arrow.y = menu_obj.y + 4
            elif selected == 2:
                arrow.x = quit_obj.x - arrow.width - 15
                arrow.y = quit_obj.y + 4

            # display
            self.draw_game(
                over_obj,
                score1_obj,
                score2_obj,
                spaceship,
                retry_obj,
                menu_obj,
                quit_obj,
                arrow,
                credits_obj,
            )

            pygame.display.update()

    # game modes and leaderboard screens
    def single_player(self) -> None:
        """single player game mode"""
        engine = SingleEngine()
        engine.player.change_style(self.config.style)

        highscore = self.data.get_high_score("single")

        while self.running:
            # get sprites
            player = engine.player
            lasers = engine.lasers
            invaders = engine.invaders
            boss = engine.boss
            bombs = engine.bombs
            explosions = engine.explosions
            sounds = engine.get_sounds()

            highscore = max(highscore, player.score)

            # events
            if player.life == 0:
                self.play_sounds("explosion")
                self.game_over(
                    score1=player.score,
                    score2=highscore,
                    original_mode="single",
                )
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.menu()
                    elif event.key == self.config.controls["left"]:
                        engine.change_direction("left")
                    elif event.key == self.config.controls["right"]:
                        engine.change_direction("right")
                    elif event.key == self.config.controls["shoot"]:
                        engine.shoot_laser()

                elif event.type == pygame.KEYUP:
                    if (
                        event.key == self.config.controls["left"]
                        and player.direction == "left"
                    ):
                        engine.change_direction("")
                    elif (
                        event.key == self.config.controls["right"]
                        and player.direction == "right"
                    ):
                        engine.change_direction("")

            # updates
            dt = self.clock.tick(60)

            self.background.update(dt, playing=True)
            self.sidebar.update(
                life=player.life,
                score1=player.score,
                highscore=highscore,
            )
            self.bosshealthbar.update(boss)
            engine.update(dt)

            # display and sounds
            self.draw_game(
                *explosions,
                *invaders,
                *bombs,
                boss,
                *lasers,
                player,
                self.sidebar,
                self.bosshealthbar,
            )
            self.play_sounds(*sounds)

            pygame.display.update()

    def local_multi_player(self) -> None:
        """local multiplayer game mode, the two players play on the same window"""
        engine = MultiEngine()
        engine.players[1].change_style(1)

        highscore = self.data.get_high_score("multi")

        while self.running:
            # get sprites
            player1 = engine.players[0]
            player2 = engine.players[1]
            lasers1 = engine.lasers[0]
            lasers2 = engine.lasers[1]
            invaders = engine.invaders
            boss = engine.boss
            bombs = engine.bombs
            explosions = engine.explosions
            sounds = engine.get_sounds(0)

            highscore = max(highscore, player1.score + player2.score)

            # events
            if player1.life == 0:
                self.play_sounds("explosion")
                self.game_over(
                    score1=player1.score,
                    score2=player2.score,
                    original_mode="local_multi",
                )
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.menu()
                    # player1 checks
                    elif event.key == pygame.K_LEFT:
                        engine.change_direction(0, "left")
                    elif event.key == pygame.K_RIGHT:
                        engine.change_direction(0, "right")
                    elif event.key == pygame.K_UP:
                        engine.shoot_laser(0)

                    # player2 checks
                    elif event.key == pygame.K_q:
                        engine.change_direction(1, "left")
                    elif event.key == pygame.K_d:
                        engine.change_direction(1, "right")
                    elif event.key == pygame.K_z:
                        engine.shoot_laser(1)

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT and player1.direction == "left":
                        engine.change_direction(0, "")
                    elif event.key == pygame.K_RIGHT and player1.direction == "right":
                        engine.change_direction(0, "")
                    elif event.key == pygame.K_q and player2.direction == "left":
                        engine.change_direction(1, "")
                    elif event.key == pygame.K_d and player2.direction == "right":
                        engine.change_direction(1, "")

            # updates
            dt = self.clock.tick(60)

            self.background.update(dt, playing=True)
            self.sidebar.update(
                life=player1.life,
                score1=player1.score,
                highscore=highscore,
                score2=player2.score,
            )
            self.bosshealthbar.update(boss)
            engine.update(dt)

            # display and sounds
            self.draw_game(
                *explosions,
                *invaders,
                *bombs,
                boss,
                *lasers2,
                player2,
                *lasers1,
                player1,
                self.sidebar,
                self.bosshealthbar,
            )
            self.play_sounds(*sounds)

            pygame.display.update()

    def online_multi_player(self) -> None:
        """online multiplayer game mode, the two players can play on different screens/windows"""
        if not self.client.connected:
            self.error_screen("YOU ARE NOT CONNECTED", "menu")
        else:
            self.waiting_screen()

        playerId = self.client.playerId
        otherId = 1 if playerId == 0 else 0

        highscore = self.data.get_high_score("multi")

        request = "get|"

        while self.running:
            # sending and receiving datas
            try:
                data = self.client.send(request)

                player = data["players"][playerId]
                other = data["players"][otherId]
                lasers_p = data["lasers"][playerId]
                lasers_o = data["lasers"][otherId]
                invaders = data["invaders"]
                boss = data["boss"]
                bombs = data["bombs"]
                explosions = data["explosions"]
                sounds = data["sounds"]
                name1, name2 = data["names"]
            except:
                self.client.disconnect()
                self.error_screen("CONNECTION LOST", "menu")

            highscore = max(highscore, player["score"] + other["score"])

            # re-initialize request
            request = "get|"

            # events
            if player["life"] == 0 or other["life"] == 0:
                self.play_sounds("explosion")
                self.client.disconnect()
                self.game_over(
                    score1=player["score"] if playerId == 0 else other["score"],
                    score2=other["score"] if playerId == 0 else player["score"],
                    original_mode="online_multi",
                    name1=name1,
                    name2=name2,
                )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.client.disconnect()
                    self.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.server.running:
                            self.server.close()
                        self.client.disconnect()
                        self.menu()
                    elif event.key == self.config.controls["left"]:
                        request += "direction:left|"
                    elif event.key == self.config.controls["right"]:
                        request += "direction:right|"
                    elif event.key == self.config.controls["shoot"]:
                        request += "shoot|"

                elif event.type == pygame.KEYUP:
                    if (
                        event.key == self.config.controls["left"]
                        and player["direction"] == "left"
                    ):
                        request += "direction:|"
                    elif (
                        event.key == self.config.controls["right"]
                        and player["direction"] == "right"
                    ):
                        request += "direction:|"

            # updates
            dt = self.clock.tick(60)

            self.background.update(dt, playing=True)
            self.sidebar.update(
                player["life"] if playerId == 0 else other["life"],
                score1=player["score"] if playerId == 0 else other["score"],
                highscore=highscore,
                score2=other["score"] if playerId == 0 else player["score"],
                name1=name1,
                name2=name2,
            )
            self.bosshealthbar.update(boss)
            request += f"update:{dt}|"

            # display and sounds
            self.draw_game(
                *explosions,
                *invaders,
                *bombs,
                boss,
                *lasers_o,
                other,
                *lasers_p,
                player,
                self.sidebar,
                self.bosshealthbar,
            )
            self.play_sounds(*sounds)

            pygame.display.update()

    def leaderboard(self) -> None:
        """leaderboard screen, show off the 10 best scores"""
        single_obj = Text("SINGLE", BLUE)
        single_obj.x = self.width / 4 - single_obj.width / 2
        single_obj.y = self.height / 10

        multi_obj = Text("MULTI", BLUE)
        multi_obj.x = self.width * 0.75 - multi_obj.width / 2
        multi_obj.y = self.height / 10

        ok_obj = Text("PRESS ANY KEY TO RETURN", WHITE)
        ok_obj.x = self.width / 2 - ok_obj.width / 2
        ok_obj.y = self.height / 10 * 8

        credits_obj = Text("©EMANUEL", WHITE)
        credits_obj.x = self.width / 2 - credits_obj.width / 2
        credits_obj.y = self.height - credits_obj.height - 10

        while self.running:
            # events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                elif event.type == pygame.KEYDOWN:
                    self.menu()

            # updates
            dt = self.clock.tick(60)

            self.background.update(dt)

            # get single scores
            single_score_objs = []
            for i in range(10):
                if i < len(self.data.scores["single"]):
                    obj = Text(
                        f"{i + 1}. {self.data.scores['single'][i]['name']} - {self.data.scores['single'][i]['score']}",
                        WHITE,
                    )
                else:
                    obj = Text(f"{i + 1}. -----", INACTIVE_GREY)
                obj.x = self.width / 4 - obj.width / 2
                obj.y = self.height / 2 - obj.height / 2 + ((i - 5) * obj.height)

                single_score_objs.append(obj)

            # get multi scores
            multi_score_objs = []
            for i in range(10):
                if i < len(self.data.scores["multi"]):
                    obj = Text(
                        f"{i + 1}. {self.data.scores['multi'][i]['name']} - {self.data.scores['multi'][i]['score']}",
                        WHITE,
                    )
                else:
                    obj = Text(f"{i + 1}. -----", INACTIVE_GREY)
                obj.x = self.width * 0.75 - obj.width / 2
                obj.y = self.height / 2 - obj.height / 2 + ((i - 5) * obj.height)

                multi_score_objs.append(obj)

            # display
            self.draw_game(
                single_obj,
                multi_obj,
                *single_score_objs,
                *multi_score_objs,
                ok_obj,
                credits_obj,
            )

            pygame.display.update()

    def settings(self) -> None:
        """add the possibility to change name, style and config.controls"""
        # align objects from the right
        settings_obj = Text("SETTINGS", BLUE)
        settings_obj.x = self.width / 2 - settings_obj.width / 2
        settings_obj.y = self.height / 10

        name_obj = Text("NAME:", WHITE)
        name_obj.x = self.width / 2 - name_obj.width
        name_obj.y = self.height / 10 * 2.25

        name_input = Text(self.config.name, WHITE)
        name_input.x = self.width / 2 + 25
        name_input.y = self.height / 10 * 2.25

        style_obj = Text("STYLE:", WHITE)
        style_obj.x = self.width / 2 - style_obj.width
        style_obj.y = self.height / 10 * 3.10

        shoot_obj = Text("SHOOT:", WHITE)
        shoot_obj.x = self.width / 2 - shoot_obj.width
        shoot_obj.y = self.height / 10 * 3.95

        shoot_key = Text("", WHITE)
        shoot_key.x = self.width / 2 + 25
        shoot_key.y = self.height / 10 * 3.95

        left_obj = Text("LEFT:", WHITE)
        left_obj.x = self.width / 2 - left_obj.width
        left_obj.y = self.height / 10 * 4.80

        left_key = Text("", WHITE)
        left_key.x = self.width / 2 + 25
        left_key.y = self.height / 10 * 4.80

        right_obj = Text("RIGHT:", WHITE)
        right_obj.x = self.width / 2 - right_obj.width
        right_obj.y = self.height / 10 * 5.65

        right_key = Text("", WHITE)
        right_key.x = self.width / 2 + 25
        right_key.y = self.height / 10 * 5.65

        up_obj = Text("UP:", WHITE)
        up_obj.x = self.width / 2 - up_obj.width
        up_obj.y = self.height / 10 * 6.50

        up_key = Text("", WHITE)
        up_key.x = self.width / 2 + 25
        up_key.y = self.height / 10 * 6.50

        down_obj = Text("DOWN:", WHITE)
        down_obj.x = self.width / 2 - down_obj.width
        down_obj.y = self.height / 10 * 7.35

        down_key = Text("", WHITE)
        down_key.x = self.width / 2 + 25
        down_key.y = self.height / 10 * 7.35

        escape_obj = Text("PRESS ENTER TO CHANGE AND ESCAPE TO RETURN", WHITE)
        escape_obj.x = self.width / 2 - escape_obj.width / 2
        escape_obj.y = self.height / 10 * 8.5

        notification_obj = Notification("PRESS A KEY!")

        arrow = Image("arrow")

        selected = 0
        changing = False

        while self.running:
            # events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.menu()

                    elif not changing:
                        if event.key == self.config.controls["enter"] and selected != 1:
                            changing = True
                        elif event.key == self.config.controls["up"] and selected > 0:
                            selected -= 1
                        elif event.key == self.config.controls["down"] and selected < 6:
                            selected += 1
                        elif selected == 1:
                            if event.key == self.config.controls["left"]:
                                self.config.style = (self.config.style - 1) % 6
                            elif event.key == self.config.controls["right"]:
                                self.config.style = (self.config.style + 1) % 6

                    elif changing:
                        if selected == 0:
                            if (
                                event.key == self.config.controls["enter"]
                                and self.config.name != ""
                            ):
                                changing = False
                            elif event.key == pygame.K_BACKSPACE:
                                self.config.name = self.config.name[:-1]
                            elif event.unicode.isalnum() and len(self.config.name) < 16:
                                self.config.name += event.unicode.upper()

                        elif event.key not in self.config.controls.values():
                            if selected == 2:
                                self.config.controls["shoot"] = event.key
                            elif selected == 3:
                                self.config.controls["left"] = event.key
                            elif selected == 4:
                                self.config.controls["right"] = event.key
                            elif selected == 5:
                                self.config.controls["up"] = event.key
                            elif selected == 6:
                                self.config.controls["down"] = event.key
                            changing = False

            # updates
            dt = self.clock.tick(60)

            self.background.update(dt)

            style_example = Image(f"spaceship{self.config.style}")
            style_example.x = self.width / 2 + 25
            style_example.y = self.height / 10 * 3.10 - 13

            name_input.change_text(
                self.config.name
                + ("_" if changing and selected == 0 and time() % 1 > 0.5 else "")
            )
            name_input.change_color(GREEN if changing and selected == 0 else WHITE)
            shoot_key.change_text(
                pygame.key.name(self.config.controls["shoot"]).upper()
            )
            left_key.change_text(pygame.key.name(self.config.controls["left"]).upper())
            right_key.change_text(
                pygame.key.name(self.config.controls["right"]).upper()
            )
            up_key.change_text(pygame.key.name(self.config.controls["up"]).upper())
            down_key.change_text(pygame.key.name(self.config.controls["down"]).upper())

            name_obj.change_color(RED if selected == 0 else WHITE)
            style_obj.change_color(RED if selected == 1 else WHITE)
            shoot_obj.change_color(RED if selected == 2 else WHITE)
            left_obj.change_color(RED if selected == 3 else WHITE)
            right_obj.change_color(RED if selected == 4 else WHITE)
            up_obj.change_color(RED if selected == 5 else WHITE)
            down_obj.change_color(RED if selected == 6 else WHITE)

            if selected == 0:
                arrow.x = name_obj.x - arrow.width - 15
                arrow.y = name_obj.y + 4
            elif selected == 1:
                arrow.x = style_obj.x - arrow.width - 15
                arrow.y = style_obj.y + 4
            elif selected == 2:
                arrow.x = shoot_obj.x - arrow.width - 15
                arrow.y = shoot_obj.y + 4
            elif selected == 3:
                arrow.x = left_obj.x - arrow.width - 15
                arrow.y = left_obj.y + 4
            elif selected == 4:
                arrow.x = right_obj.x - arrow.width - 15
                arrow.y = right_obj.y + 4
            elif selected == 5:
                arrow.x = up_obj.x - arrow.width - 15
                arrow.y = up_obj.y + 4
            elif selected == 6:
                arrow.x = down_obj.x - arrow.width - 15
                arrow.y = down_obj.y + 4

            # display
            self.draw_game(
                settings_obj,
                name_obj,
                name_input,
                style_obj,
                style_example,
                shoot_obj,
                shoot_key,
                left_obj,
                left_key,
                right_obj,
                right_key,
                up_obj,
                up_key,
                down_obj,
                down_key,
                escape_obj,
                arrow,
                notification_obj if changing and selected > 1 else None,
            )

            pygame.display.update()

    # online mode methods/screens
    def host_or_join(self) -> None:
        """choose between hosting or joining an online game"""
        host_obj = Text("HOST GAME", WHITE)
        host_obj.x = self.width / 2 - host_obj.width / 2
        host_obj.y = self.height / 2 - host_obj.height

        join_obj = Text("JOIN GAME", WHITE)
        join_obj.x = self.width / 2 - join_obj.width / 2
        join_obj.y = self.height / 2 + join_obj.height / 2

        arrow = Image("arrow")

        selected = 0

        while self.running:
            if not self.online:
                self.error_screen("CONNECTION UNAVAILABLE", "menu")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.menu()
                    elif event.key == pygame.K_UP and selected > 0:
                        selected -= 1
                    elif event.key == pygame.K_DOWN and selected < 1:
                        selected += 1
                    elif event.key == pygame.K_RETURN:
                        if selected == 0:
                            self.host()
                        elif selected == 1:
                            self.join()

            # updates
            dt = self.clock.tick(60)

            self.background.update(dt)

            host_obj.change_color(RED if selected == 0 else WHITE)
            join_obj.change_color(RED if selected == 1 else WHITE)

            if selected == 0:
                arrow.x = host_obj.x - arrow.width - 10
                arrow.y = host_obj.y + 4
            else:
                arrow.x = join_obj.x - arrow.width - 10
                arrow.y = join_obj.y + 4

            # display
            self.draw_game(host_obj, join_obj, arrow)

            pygame.display.update()

    def host(self) -> None:
        """host game and connect to it"""
        # start server if not already started
        if not self.server.running:
            # if the server start fails go to error screen
            if self.server.start():
                start_new_thread(self.server.run, ())
            else:
                self.error_screen("CONNECTION UNAVAILABLE", "menu")

        # connect client
        self.client.connect(self.server.ip, self.config.name, self.config.style)
        # load game
        self.online_multi_player()

    def join(self) -> None:
        """connection screen for online multiplayer mode"""
        # variables
        input_ip = self.last_ip
        connecting = False
        connecting_since = 0

        # objects
        connection_obj = Text("ENTER THE SERVER IP ADDRESS:", WHITE)
        connection_obj.x = self.width / 2 - connection_obj.width / 2
        connection_obj.y = self.height / 2 - connection_obj.height * 2

        input_obj = Text(f"{input_ip}", RED)

        cursor_obj = Text("_", WHITE)

        valid_obj = Text("INVALID IP ADDRESS", WHITE)
        valid_obj.x = self.width / 2 - valid_obj.width / 2
        valid_obj.y = self.height / 2 + valid_obj.height

        def valid(ip: str):
            """check if ip is valid"""
            if len(ip.split(".")) == 4:
                for i in ip.split("."):
                    if not i.isdigit():
                        return False
                    if int(i) < 0 or int(i) > 255:
                        return False
                return True
            return False

        while not self.client.connected and self.running:
            # check
            if not self.online:
                self.error_screen("CONNECTION UNAVAILABLE", "menu")

            if connecting and time() - connecting_since > 5:
                connecting = False
                connecting_since = 0
                input_ip = ""
            # events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.host_or_join()
                    elif not connecting and event.key == pygame.K_BACKSPACE:
                        input_ip = input_ip[:-1]
                    elif not connecting and event.key != pygame.K_RETURN:
                        input_ip += event.unicode
                    elif (
                        not connecting
                        and event.key == pygame.K_RETURN
                        and valid(input_ip)
                    ):
                        connecting = True
                        connecting_since = time()
                        start_new_thread(
                            self.client.connect,
                            (input_ip, self.config.name, self.config.style),
                        )

            # updates
            dt = self.clock.tick(60)

            self.background.update(dt, playing=False)

            input_obj.change_text(input_ip)
            input_obj.change_color(
                RED if not valid(input_ip) else BLUE if connecting else GREEN
            )
            input_obj.x = self.width / 2 - input_obj.width / 2
            input_obj.y = self.height / 2 - input_obj.height / 2

            cursor_obj.change_text("_" if time() % 1 > 0.5 and not connecting else "")
            cursor_obj.x = self.width / 2 - input_obj.width / 2 + input_obj.width
            cursor_obj.y = input_obj.y

            valid_obj.change_text(
                "INVALID IP ADDRESS"
                if not valid(input_ip)
                else "TRYING TO CONNECT" + "." * int(time() % 4)
                if connecting
                else "VALID IP ADDRESS"
            )
            valid_obj.x = self.width / 2 - valid_obj.width / 2
            valid_obj.y = self.height / 2 + valid_obj.height

            # display
            self.draw_game(connection_obj, input_obj, cursor_obj, valid_obj)

            pygame.display.update()

        # save ip
        self.last_ip = input_ip
        # load game
        self.online_multi_player()

    def waiting_screen(self) -> None:
        """waiting screen for online multiplayer mode"""
        if self.server.running:
            message_obj = Text("SERVER RUNNING ON:", WHITE)
            ip_obj = Text(self.server.ip, GREEN)
            quit_obj = Text("PRESS ESCAPE TO CLOSE SERVER", RED)
        else:
            message_obj = Text("CONNECTED TO SERVER", WHITE)
            ip_obj = Text(self.client.ip, GREEN)
            quit_obj = Text("PRESS ESCAPE TO QUIT", RED)

        message_obj.x = self.width / 2 - message_obj.width / 2
        message_obj.y = self.height / 2 - message_obj.height * 2

        ip_obj.x = self.width / 2 - ip_obj.width / 2
        ip_obj.y = self.height / 2 - ip_obj.height / 2

        quit_obj.x = self.width / 2 - quit_obj.width / 2
        quit_obj.y = self.height * 3 / 4 - quit_obj.height / 2

        waiting_obj = Text("WAITING FOR OTHER PLAYERS", WHITE)
        waiting_obj.x = self.width / 2 - waiting_obj.width / 2
        waiting_obj.y = self.height / 2 + waiting_obj.height

        ready = False
        ready_since = time()

        while not ready or time() - ready_since < 4:
            # get data from server
            try:
                ready = self.client.send("get|")["ready"]
            except:
                self.client.disconnect()
                self.error_screen("CONNECTION LOST", "menu")

            # events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.server.running:
                        self.server.close()
                    self.client.disconnect()
                    self.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.server.running:
                            self.server.close()
                        self.client.disconnect()
                        self.host_or_join()

            # updates
            dt = self.clock.tick(60)

            self.background.update(dt, playing=False)

            if ready:
                waiting_obj.change_text(
                    f"STARTING GAME IN {int(4 - time() + ready_since)}"
                )
                waiting_obj.x = self.width / 2 - waiting_obj.width / 2
            else:
                waiting_obj.change_text(
                    f"WAITING FOR OTHER PLAYERS{'.' * int(time() % 4)}"
                )
                waiting_obj.x = self.width / 2 - waiting_obj.width / 2
                ready_since = time()

            # display
            self.draw_game(message_obj, ip_obj, quit_obj, waiting_obj)

            pygame.display.update()

    # error method
    def error_screen(self, error: str, redirect: str) -> None:
        """error screen"""
        error_obj = Text(error.upper(), RED)
        error_obj.x = self.width / 2 - error_obj.width / 2
        error_obj.y = self.height / 2 - error_obj.height

        ok_obj = Text("PRESS ANY KEY TO RETURN", WHITE)
        ok_obj.x = self.width / 2 - ok_obj.width / 2
        ok_obj.y = self.height / 2 + ok_obj.height

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                elif event.type == pygame.KEYDOWN:
                    if redirect == "welcome":
                        self.welcome_screen()
                    elif redirect == "menu":
                        self.menu()
                    elif redirect == "single":
                        self.single_player()
                    elif redirect == "local_multi":
                        self.local_multi_player()
                    elif redirect == "online_multi":
                        self.host_or_join()
                    elif redirect == "settings":
                        self.settings()

            # updates
            dt = self.clock.tick(60)

            self.background.update(dt, playing=False)

            # display
            self.draw_game(error_obj, ok_obj)

            pygame.display.update()


Game().run()
