from src.sprites import Player, Laser, Invader, Boss, Bomb, Explosion
from src.variables import N_INVADERS, GAME_WIDTH, GAME_HEIGHT
from threading import Timer


class SingleEngine:
    def __init__(self) -> None:
        """initialize the game"""
        self.gamew, self.gameh = GAME_WIDTH, GAME_HEIGHT

        # sprites
        self.player = Player()
        self.lasers = [Laser(self.player)]
        self.invaders = [Invader() for i in range(N_INVADERS)]
        self.boss = Boss()
        self.bombs = []  # type: list[Bomb]
        self.explosions = []  # type: list[Explosion]
        self.sounds = []

        # score goals
        self.invader_goal = 100
        self.boss_goal = 200

    def change_direction(self, direction: str) -> None:
        """change the direction of the player"""
        self.player.direction = direction

    def update(self, dt: int) -> None:
        """update game state"""
        self.player.move(dt)
        for laser in self.lasers:
            laser.move(dt)
        for invader in self.invaders:
            invader.move(dt)
        self.boss.move(dt)
        for bomb in self.bombs:
            bomb.move(dt)

        self.check_invader_collisions()
        self.check_laser_collisions()
        self.check_bomb_collisions()
        self.check_explosions()
        self.check_scores()

    def add_laser(self) -> None:
        """add a laser"""
        self.lasers.append(Laser(self.player))

    def add_explosion(self, x: int, y: int) -> None:
        """add an explosion to the explosions list"""
        self.explosions.append(Explosion(x, y, 0.3))

    def shoot_laser(self) -> None:
        """shoot a laser if possible"""
        if self.lasers != [] and not self.lasers[-1].shot:
            self.add_sound("shoot")
            self.lasers[-1].shoot()
            Timer(0.6, self.add_laser).start()

    def shoot_bomb(self) -> None:
        """shoot a bomb every 5 seconds when the boss is alive"""
        if self.boss.alive:
            self.add_sound("bomb")
            self.bombs.append(Bomb(self.boss))
            Timer(4, self.shoot_bomb).start()

    def check_invader_collisions(self) -> None:
        """check if an invader collides with the player, crashes, or dies"""
        for invader in self.invaders:
            if (
                invader.collide(self.player) or invader.crash()
            ) and self.player.life > 0:
                self.player.life -= 1
                self.add_explosion(invader.x, invader.y)
                self.add_sound("explosion")
                invader.die()

    def check_laser_collisions(self) -> None:
        """check if a laser collides with an invader or the top of the screen"""
        # check if a laser is out of screen
        for i in range(len(self.lasers) - 1, -1, -1):
            laser = self.lasers[i]
            if laser.y + laser.height <= 0:
                self.lasers.pop(i)

        # check if a laser collides with an invader
        for i in range(len(self.lasers) - 1, -1, -1):
            laser = self.lasers[i]
            if laser.shot:
                for invader in self.invaders:
                    if laser.collide(invader):
                        self.add_explosion(invader.x, invader.y)
                        self.add_sound("killed")
                        self.player.add_points(invader.type + 1)
                        invader.die()
                        self.lasers.pop(i)
                        break

        # check if a laser collides with a bomb
        for i in range(len(self.lasers) - 1, -1, -1):
            laser = self.lasers[i]
            if laser.shot:
                for j in range(len(self.bombs) - 1, -1, -1):
                    bomb = self.bombs[j]
                    if laser.collide(bomb):
                        self.bombs.pop(j)
                        self.add_explosion(bomb.x, bomb.y)
                        self.add_sound("killed")
                        self.lasers.pop(i)
                        self.player.add_points(1)
                        break

        # check if a laser collides with the boss
        for i in range(len(self.lasers) - 1, -1, -1):
            laser = self.lasers[i]
            if laser.shot and self.boss.alive and laser.collide(self.boss):
                self.boss.life -= 1
                self.add_explosion(laser.x - 32, laser.y - laser.height / 2)
                self.lasers.pop(i)
                self.add_sound("killed")
                if self.boss.life == 0:
                    self.add_sound("boss")
                    self.boss.die()
                    self.player.add_points(50)

    def check_bomb_collisions(self) -> None:
        """check if a bomb collides with the player"""
        for i in range(len(self.bombs) - 1, -1, -1):
            bomb = self.bombs[i]
            # check if bomb is out of screen
            if bomb.y > self.gameh:
                self.bombs.pop(i)
            elif bomb.collide(self.player):
                self.player.life -= 1
                self.add_sound("explosion")
                self.add_explosion(bomb.x, bomb.y)
                self.bombs.pop(i)

    def check_explosions(self) -> None:
        """check if an explosion is over"""
        for i in range(len(self.explosions) - 1, -1, -1):
            if self.explosions[i].over:
                self.explosions.pop(i)

    def check_scores(self) -> None:
        """check if the scores should pop an event"""
        if self.player.score >= self.invader_goal:
            self.invader_goal += 100
            for invader in self.invaders:
                invader.increase_speed()
        if self.player.score >= self.boss_goal:
            self.boss_goal += 200
            self.boss.appear()
            self.add_sound("boss")
            Timer(4, self.shoot_bomb).start()

    def add_sound(self, sound: str) -> None:
        """add a sound to the sounds list"""
        self.sounds.append(sound)

    def get_sounds(self) -> list:
        """return the sounds list"""
        sounds = self.sounds
        self.sounds = []
        return sounds


class MultiEngine:
    def __init__(self) -> None:
        """initialize the game"""
        self.gamew, self.gameh = GAME_WIDTH, GAME_HEIGHT

        # sprites
        self.players = [Player(), Player()]
        self.lasers = [[Laser(self.players[0])], [Laser(self.players[1])]]
        self.invaders = [Invader() for i in range(int(N_INVADERS * 2.5))]
        self.boss = Boss()
        self.bombs = []  # type: list[Bomb]
        self.explosions = []  # type: list[Explosion]
        self.sounds = [[], []]

        # score goals
        self.invader_goal = 100
        self.boss_goal = 300

        # online attributes
        self.ready = False
        self.player_count = 1
        self.player_names = ["PLAYER-1", "PLAYER-2"]

    def change_direction(self, playerId: int, direction: str) -> None:
        """change the direction of the player"""
        self.players[playerId].direction = direction

    def update(self, dt: int) -> None:
        """update game state"""
        for player in self.players:
            player.move(dt)
        for laser in self.lasers[0] + self.lasers[1]:
            laser.move(dt)
        for invader in self.invaders:
            invader.move(dt)
        self.boss.move(dt)
        for bomb in self.bombs:
            bomb.move(dt)

        self.check_invader_collisions()
        self.check_laser_collisions(0)
        self.check_laser_collisions(1)
        self.check_bomb_collisions()
        self.check_explosions()
        self.check_scores()

    def add_laser(self, playerId: int) -> None:
        """add a laser to the player lasers"""
        self.lasers[playerId].append(Laser(self.players[playerId]))

    def add_explosion(self, x: int, y: int) -> None:
        """add an explosion to the explosions list"""
        self.explosions.append(Explosion(x, y, 0.3))

    def shoot_laser(self, playerId: int) -> None:
        """shoot a laser if possible"""
        if self.lasers[playerId] != [] and not self.lasers[playerId][-1].shot:
            self.add_sound("shoot")
            self.lasers[playerId][-1].shoot()
            Timer(0.6, self.add_laser, [playerId]).start()

    def shoot_bomb(self) -> None:
        """shoot a bomb every 5 seconds when the boss is alive"""
        if self.boss.alive:
            self.add_sound("bomb")
            self.bombs.append(Bomb(self.boss))
            Timer(4, self.shoot_bomb).start()

    def check_invader_collisions(self) -> None:
        """check if an invader collides with the players or crashes"""
        for invader in self.invaders:
            if (
                invader.collide(self.players[0])
                or invader.collide(self.players[1])
                or invader.crash()
            ) and self.players[0].life > 0:
                self.players[0].life -= 1
                self.add_explosion(invader.x, invader.y)
                self.add_sound("explosion")
                invader.die()

    def check_laser_collisions(self, playerId: int) -> None:
        """check if a laser collides with something"""
        # check if laser is out of screen
        for i in range(len(self.lasers[playerId]) - 1, -1, -1):
            laser = self.lasers[playerId][i]
            if laser.y + laser.height < 0:
                self.lasers[playerId].pop(i)

        # check if laser collides with invader
        for i in range(len(self.lasers[playerId]) - 1, -1, -1):
            laser = self.lasers[playerId][i]
            if laser.shot:
                for invader in self.invaders:
                    if laser.collide(invader):
                        self.add_explosion(invader.x, invader.y)
                        self.add_sound("killed")
                        self.lasers[playerId].pop(i)
                        self.players[playerId].add_points(invader.type + 1)
                        invader.die()
                        break

        # check if laser collides with a bomb
        for i in range(len(self.lasers[playerId]) - 1, -1, -1):
            laser = self.lasers[playerId][i]
            if laser.shot:
                for j in range(len(self.bombs) - 1, -1, -1):
                    bomb = self.bombs[j]
                    if laser.collide(bomb):
                        self.add_explosion(bomb.x, bomb.y)
                        self.add_sound("explosion")
                        self.bombs.pop(j)
                        self.lasers[playerId].pop(i)
                        self.players[playerId].add_points(1)
                        break

        # check if laser collides with boss
        for i in range(len(self.lasers[playerId]) - 1, -1, -1):
            laser = self.lasers[playerId][i]
            if laser.shot and self.boss.alive and laser.collide(self.boss):
                self.boss.life -= 1
                self.add_explosion(laser.x - 32, laser.y - laser.height / 2)
                self.add_sound("killed")
                self.lasers[playerId].pop(i)
                if self.boss.life == 0:
                    self.add_sound("boss")
                    self.boss.die()
                    self.players[playerId].add_points(50)

    def check_bomb_collisions(self) -> None:
        """check if a bomb collides with the players"""
        for i in range(len(self.bombs) - 1, -1, -1):
            bomb = self.bombs[i]
            # check if bomb is out of screen
            if bomb.y > self.gameh:
                self.bombs.pop(i)
            elif (
                bomb.collide(self.players[0]) or bomb.collide(self.players[1])
            ) and self.players[0].life > 0:
                self.add_explosion(bomb.x, bomb.y)
                self.add_sound("explosion")
                self.players[0].life -= 1
                self.bombs.pop(i)

    def check_explosions(self) -> None:
        """check if an explosion is over"""
        for i in range(len(self.explosions) - 1, -1, -1):
            explosion = self.explosions[i]
            if explosion.over:
                self.explosions.pop(i)

    def check_scores(self) -> None:
        """check if the scores should pop an event"""
        if self.players[0].score + self.players[1].score >= self.invader_goal:
            self.invader_goal += 100
            for invader in self.invaders:
                invader.increase_speed()
        if self.players[0].score + self.players[1].score >= self.boss_goal:
            self.boss_goal += 300
            self.boss.appear()
            self.add_sound("boss")
            Timer(4, self.shoot_bomb).start()

    def add_sound(self, sound: str) -> None:
        """add a sound to the sounds list"""
        self.sounds[0].append(sound)
        self.sounds[1].append(sound)

    # online mode methods to get needed datas
    def get_players_data(self) -> dict:
        """return the players needed data"""
        return [
            {
                "image_name": player.image_name,
                "x": player.x,
                "y": player.y,
                "direction": player.direction,
                "score": player.score,
                "life": player.life,
            }
            for player in self.players
        ]

    def get_lasers_data(self) -> dict:
        """return the lasers needed data"""
        return [
            [
                {"image_name": laser.image_name, "x": laser.x, "y": laser.y}
                for laser in lasers
            ]
            for lasers in self.lasers
        ]

    def get_invaders_data(self) -> dict:
        """return the invaders needed data"""
        return [
            {
                "image_name": invader.image_name,
                "x": invader.x,
                "y": invader.y,
            }
            for invader in self.invaders
        ]

    def get_boss_data(self) -> dict:
        """return the needed boss data"""
        boss = self.boss
        return {
            "image_name": boss.image_name,
            "x": boss.x,
            "y": boss.y,
            "life": boss.life,
        }

    def get_bombs_data(self) -> dict:
        """return the needed bombs data"""
        return [
            {"image_name": bomb.image_name, "x": bomb.x, "y": bomb.y}
            for bomb in self.bombs
        ]

    def get_explosions_data(self) -> dict:
        """return the needed explosions data"""
        return [
            {"image_name": explosion.image_name, "x": explosion.x, "y": explosion.y}
            for explosion in self.explosions
        ]

    def get_sounds(self, playerId: int) -> list:
        """get the sounds data of the player"""
        sounds = self.sounds[playerId]
        self.sounds[playerId] = []
        return sounds

    def get_data(self, playerId: int) -> dict:
        """return all the needed game data"""
        return {
            "ready": self.ready,
            "names": self.player_names,
            "players": self.get_players_data(),
            "lasers": self.get_lasers_data(),
            "invaders": self.get_invaders_data(),
            "boss": self.get_boss_data(),
            "bombs": self.get_bombs_data(),
            "explosions": self.get_explosions_data(),
            "sounds": self.get_sounds(playerId),
        }
