import random
import pygame
from asteroid import Asteroid, score_for_radius
from asteroidfield import AsteroidField
from bomb import BlastRing, Bomb
from constants import (
    ASTEROID_MIN_RADIUS,
    BOMB_RADIUS,
    PLAYER_LIVES,
    PLAYER_RESPAWN_CLEAR_RADIUS,
    POWERUP_DROP_CHANCE,
    POWERUP_KINDS,
    POWERUP_WEIGHTS,
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
        self.bombs = pygame.sprite.Group()
        Asteroid.containers = (self.asteroids, self.updatable, self.drawable)
        AsteroidField.containers = (self.updatable,)
        Shot.containers = (self.drawable, self.updatable, self.shots)
        Explosion.containers = (self.drawable, self.updatable, self.explosions)
        Powerup.containers = (self.updatable, self.drawable, self.powerups)
        Bomb.containers = (self.bombs, self.updatable, self.drawable)
        BlastRing.containers = (self.drawable, self.updatable, self.explosions)
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
        kill_all(self.bombs)
        self.field.spawn_timer = 0.0
        self.player.respawn(SPAWN_X, SPAWN_Y)
        self.player.set_weapon("normal")

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if self.is_game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.reset()
                continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self.player.try_toggle_shield()
                elif event.button == 2:
                    self._handle_bomb_key()
            elif event.type == pygame.KEYDOWN:
                weapon_map = {
                    pygame.K_1: "normal",
                    pygame.K_2: "spread",
                    pygame.K_3: "heavy",
                }
                if event.key in weapon_map:
                    self.player.set_weapon(weapon_map[event.key])
                elif event.key == pygame.K_b:
                    self._handle_bomb_key()
        return True

    def _handle_bomb_key(self) -> None:
        live = [
            bomb
            for bomb in self.bombs
            if bomb.alive() and not bomb.just_exploded
        ]
        if live:
            for bomb in live:
                bomb.detonate_now()
            return
        self.player.try_drop_bomb()

    def _obliterate_asteroid(self, asteroid: Asteroid) -> None:
        self.score += score_for_radius(asteroid.radius)
        x, y = asteroid.position.x, asteroid.position.y
        radius = asteroid.radius
        self._maybe_drop_powerup(x, y, radius)
        asteroid.kill()
        Explosion.spawn_explosions(x, y, radius)

    def handle_bomb_explosions(self) -> None:
        pending = [
            bomb for bomb in list(self.bombs) if bomb.just_exploded and bomb.alive()
        ]
        resolved: set[Bomb] = set()
        while pending:
            bomb = pending.pop()
            if bomb in resolved or not bomb.alive():
                continue
            resolved.add(bomb)
            center = pygame.Vector2(bomb.position)
            BlastRing(center.x, center.y)
            Explosion.spawn_bomb_explosion(center.x, center.y)
            for asteroid in list(self.asteroids):
                if not asteroid.alive():
                    continue
                if center.distance_to(asteroid.position) <= BOMB_RADIUS + asteroid.radius:
                    self._obliterate_asteroid(asteroid)
            for other in list(self.bombs):
                if other is bomb or other in resolved or not other.alive():
                    continue
                if center.distance_to(other.position) <= BOMB_RADIUS + other.radius:
                    other.detonate_now()
                    pending.append(other)
            self._try_bomb_hurt_player(center)
            bomb.kill()
            if self.is_game_over:
                return

    def _try_bomb_hurt_player(self, center: pygame.Vector2) -> None:
        if self.is_game_over:
            return
        if self.player.is_invulnerable:
            return
        if self.player.has_shield:
            return
        hit_range = BOMB_RADIUS + self.player.radius
        if center.distance_to(self.player.position) > hit_range:
            return
        x, y = self.player.position.x, self.player.position.y
        Explosion.spawn_player_explosion(x, y)
        self.lives -= 1
        if self.lives <= 0:
            self.is_game_over = True
            kill_all(self.bombs)
            return
        self.player.respawn(SPAWN_X, SPAWN_Y)
        for rock in list(self.asteroids):
            if rock.position.distance_to(self.player.position) <= PLAYER_RESPAWN_CLEAR_RADIUS:
                rock.kill()
        kill_all(self.bombs)

    def handle_shot_hits(self) -> None:
        for shot in list(self.shots):
            for asteroid in list(self.asteroids):
                if not asteroid.alive() or not asteroid.collides_with(shot):
                    continue
                blast_center = pygame.Vector2(asteroid.position)
                is_last_hit = shot.pierce_left <= 1
                if is_last_hit and shot.blast_radius > 0.0:
                    nearby = [
                        rock
                        for rock in list(self.asteroids)
                        if rock is not asteroid
                        and rock.alive()
                        and rock.position.distance_to(blast_center)
                        <= shot.blast_radius + rock.radius
                    ]
                    self._destroy_asteroid(asteroid)
                    Explosion.spawn_explosions(
                        blast_center.x, blast_center.y, shot.blast_radius
                    )
                    for rock in nearby:
                        if rock.alive():
                            self._destroy_asteroid(rock)
                    shot.kill()
                    break
                self._destroy_asteroid(asteroid)
                shot.pierce_left -= 1
                if shot.pierce_left <= 0:
                    shot.kill()
                    break

    def _destroy_asteroid(self, asteroid: Asteroid) -> None:
        self.score += score_for_radius(asteroid.radius)
        x, y = asteroid.position.x, asteroid.position.y
        radius = asteroid.radius
        self._maybe_drop_powerup(x, y, radius)
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

    def _maybe_drop_powerup(self, x: float, y: float, radius: float) -> None:
        if radius <= ASTEROID_MIN_RADIUS:
            return
        if random.random() >= POWERUP_DROP_CHANCE:
            return
        kind = random.choices(POWERUP_KINDS, weights=POWERUP_WEIGHTS, k=1)[0]
        Powerup(x, y, kind)

    def update(self) -> None:
        if self.is_game_over:
            self.explosions.update(self.dt)
            return
        self.updatable.update(self.dt)
        self.handle_bomb_explosions()
        if self.is_game_over:
            return
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
