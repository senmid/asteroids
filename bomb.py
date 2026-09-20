import pygame
from circleshape import CircleShape
from constants import (
    BOMB_DRAW_RADIUS,
    BOMB_FUSE_SECONDS,
    BOMB_RADIUS,
    BOMB_RING_LIFE,
    LINE_WIDTH,
)


class Bomb(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, BOMB_DRAW_RADIUS)
        self.fuse = BOMB_FUSE_SECONDS
        self.just_exploded = False

    def update(self, dt: float) -> None:
        if self.just_exploded:
            return
        self.move(dt)
        self.wrap_position()
        self.fuse -= dt
        if self.fuse <= 0.0:
            self.just_exploded = True

    def draw(self, screen: pygame.Surface) -> None:
        color = "red" if int(self.fuse * 8) % 2 == 0 else "orange"
        half = self.radius
        left = self.position.x - half
        top = self.position.y - half
        rect = pygame.Rect(left, top, half * 2, half * 2)
        pygame.draw.rect(screen, color, rect, LINE_WIDTH)
        top_left = pygame.Vector2(left, top)
        top_right = pygame.Vector2(left + half * 2, top)
        bottom_left = pygame.Vector2(left, top + half * 2)
        bottom_right = pygame.Vector2(left + half * 2, top + half * 2)
        pygame.draw.line(screen, color, top_left, bottom_right, LINE_WIDTH)
        pygame.draw.line(screen, color, top_right, bottom_left, LINE_WIDTH)

    def detonate_now(self) -> None:
        self.fuse = 0.0
        self.just_exploded = True


class BlastRing(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, 4)
        self.life = BOMB_RING_LIFE
        self.max_life = BOMB_RING_LIFE

    def update(self, dt: float) -> None:
        self.life -= dt
        if self.life <= 0.0:
            self.kill()
            return
        t = 1.0 - (self.life / self.max_life)
        self.radius = max(4.0, BOMB_RADIUS * t)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, "orange", self.position, self.radius, LINE_WIDTH)