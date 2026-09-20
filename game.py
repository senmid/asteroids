import random
import pygame
from asteroid import Asteroid, score_for_radius
from asteroidfield import AsteroidField
from constants import (
    ASTEROID_MIN_RADIUS,
    PLAYER_LIVES,
    PLAYER_RESPAWN_CLEAR_RADIUS,
    POWERUP_DROP_CHANCE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from explosion import Explosion
from hud import Hud
from player import Player
from powerup import Powerup
from shot import Shot

SPAWN_X = SCREEN_WIDTH / 2
SPAWN_Y = SCREEN_HEIGHT / 2


def kill_all(group: pygame.sprite.Group) -> None:
    for sprite in list(group):
        sprite.kill()


class Game:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.hud = Hud(self.font)
        self.background = pygame.image.load("assets/background.jpg").convert()
        self.background = pygame.transform.scale(
            self.background, (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 128))
        self.updatable = pygame.sprite.Group()
        self.drawable = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        Asteroid.containers = (self.asteroids, self.updatable, self.drawable)
        AsteroidField.containers = (self.updatable,)
        Shot.containers = (self.drawable, self.updatable, self.shots)
        Explosion.containers = (self.drawable, self.updatable, self.explosions)
        Powerup.containers = (self.updatable, self.drawable, self.powerups)
        Player.containers = (self.updatable, self.drawable)
        self.field = AsteroidField()
        self.player = Player(SPAWN_X, SPAWN_Y)
        self.score = 0
        self.lives = PLAYER_LIVES
        self.is_game_over = False
        self.dt = 0.0

    def reset(self) -> None:
        self.lives = PLAYER_LIVES
        self.score = 0
        self.is_game_over = False
        kill_all(self.asteroids)
        kill_all(self.shots)
        kill_all(self.explosions)
        kill_all(self.powerups)
        self.field.spawn_timer = 0.0
        self.player.respawn(SPAWN_X, SPAWN_Y)

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 3
                and not self.is_game_over
            ):
                self.player.try_toggle_shield()
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_RETURN
                and self.is_game_over
            ):
                self.reset()
        return True

    def handle_shot_hits(self) -> None:
        for asteroid in self.asteroids:
            for shot in self.shots:
                if asteroid.collides_with(shot):
                    shot.kill()
                    self.score += score_for_radius(asteroid.radius)
                    x, y = asteroid.position.x, asteroid.position.y
                    radius = asteroid.radius
                    if radius > ASTEROID_MIN_RADIUS and random.random() < POWERUP_DROP_CHANCE:
                        kind = random.choices(
                            ("shield", "speed", "shot_wrap", "friction"),
                            weights=(30, 30, 20, 20),
                            k=1,
                        )[0]
                        Powerup(x, y, kind)
                    asteroid.split()
                    Explosion.spawn_explosions(x, y, radius)

    def handle_player_hits(self) -> None:
        if self.player.is_invulnerable:
            return
        for asteroid in self.asteroids:
            if not self.player.collides_with_asteroid(asteroid):
                continue
            if self.player.has_shield:
                continue
            x, y = self.player.position.x, self.player.position.y
            Explosion.spawn_player_explosion(x, y)
            self.lives -= 1
            if self.lives <= 0:
                self.is_game_over = True
                return
            self.player.respawn(SPAWN_X, SPAWN_Y)
            for rock in list(self.asteroids):
                if rock.position.distance_to(self.player.position) <= PLAYER_RESPAWN_CLEAR_RADIUS:
                    rock.kill()
            return

    def handle_powerup_pickups(self) -> None:
        for powerup in list(self.powerups):
            if powerup.collides_with(self.player):
                self.player.grant_powerup(powerup.kind)
                powerup.kill()

    def handle_shot_powerups(self) -> None:
        for powerup in list(self.powerups):
            for shot in list(self.shots):
                if not powerup.collides_with(shot):
                    continue
                self.player.grant_powerup(powerup.kind)
                powerup.kill()
                shot.kill()
                break

    def update(self) -> None:
        if self.is_game_over:
            self.explosions.update(self.dt)
            return
        self.updatable.update(self.dt)
        self.handle_shot_powerups()
        self.handle_shot_hits()
        self.handle_powerup_pickups()
        self.handle_player_hits()

    def draw(self) -> None:
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.overlay, (0, 0))
        for sprite in self.drawable:
            sprite.draw(self.screen)
        self.hud.draw(
            self.screen,
            self.score,
            self.lives,
            self.clock.get_fps(),
            self.is_game_over,
            self.player,
        )
        pygame.display.flip()

    def run(self) -> None:
        while self.handle_events():
            self.update()
            self.draw()
            self.dt = self.clock.tick(60) / 1000.0
