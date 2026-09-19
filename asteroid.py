import random
import pygame
from circleshape import CircleShape
from constants import ASTEROID_MIN_RADIUS, LINE_WIDTH, SCORE_LARGE, SCORE_MEDIUM, SCORE_SMALL, SCREEN_HEIGHT, SCREEN_WIDTH
from logger import log_event


class Asteroid(CircleShape):
    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)
    
    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)
    
    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.wrap_position()
    
    def split(self) -> int:
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return SCORE_SMALL
        log_event("asteroid_split")
        angle = random.uniform(20, 50)
        velocity1  = self.velocity.rotate(angle)
        velocity2 = self.velocity.rotate(-angle)
        radius = self.radius - ASTEROID_MIN_RADIUS
        Asteroid(self.position.x, self.position.y, radius).velocity = velocity1 * 1.2
        Asteroid(self.position.x, self.position.y, radius).velocity = velocity2 * 1.2
        if self.radius <= ASTEROID_MIN_RADIUS * 2:
            return SCORE_MEDIUM
        return SCORE_LARGE

    def wrap_position(self) -> None:
        if self.position.x > SCREEN_WIDTH:
            self.position.x = -self.radius
        if self.position.x < -self.radius:
            self.position.x = SCREEN_WIDTH + self.radius
        if self.position.y > SCREEN_HEIGHT:
            self.position.y = -self.radius
        if self.position.y < -self.radius:
            self.position.y = SCREEN_HEIGHT + self.radius