import random
import pygame
from circleshape import CircleShape
from constants import (
    ASTEROID_MIN_RADIUS,
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
    
    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)
    
    def update(self, dt: float) -> None:
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