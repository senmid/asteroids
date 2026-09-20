import random
import pygame
from circleshape import CircleShape
from constants import (
    ASTEROID_MIN_RADIUS,
    ASTEROID_SPIN_MAX,
    ASTEROID_SPIN_MIN,
    LINE_WIDTH,
    SCORE_LARGE,
    SCORE_MEDIUM,
    SCORE_SMALL,
)


def score_for_radius(radius: float) -> int:
    if radius <= ASTEROID_MIN_RADIUS:
        return SCORE_SMALL
    if radius <= ASTEROID_MIN_RADIUS * 2:
        return SCORE_MEDIUM
    return SCORE_LARGE


class Asteroid(CircleShape):
    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)
        self.points: list[pygame.Vector2] = []
        num = random.randint(8, 12)
        for i in range(num):
            angle = (360 / num) * i
            r = self.radius * random.uniform(0.75, 1.0)
            self.points.append(pygame.Vector2(0, 1).rotate(angle) * r)
        direction = random.choice((-1.0, 1.0))
        self.spin_speed = direction * random.uniform(
            ASTEROID_SPIN_MIN, ASTEROID_SPIN_MAX
        )

    def draw(self, screen: pygame.Surface) -> None:
        world = [self.position + p for p in self.points]
        pygame.draw.polygon(screen, "white", world, LINE_WIDTH)

    def update(self, dt: float) -> None:
        for point in self.points:
            point.rotate_ip(self.spin_speed * dt)
        self.move(dt)
        self.wrap_position()

    def split(self) -> None:
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        angle = random.uniform(20, 50)
        radius = self.radius - ASTEROID_MIN_RADIUS
        Asteroid(self.position.x, self.position.y, radius).velocity = (
            self.velocity.rotate(angle) * 1.2
        )
        Asteroid(self.position.x, self.position.y, radius).velocity = (
            self.velocity.rotate(-angle) * 1.2
        )
