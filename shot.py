import pygame
from circleshape import CircleShape
from constants import (
    SHOT_RADIUS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


class Shot(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, SHOT_RADIUS)
    
    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, "white", self.position, self.radius)
    
    def update(self, dt: float) -> None:
        self.move(dt)
        if (
            self.position.x < -self.radius 
            or self.position.x > SCREEN_WIDTH + self.radius 
            or self.position.y < -self.radius 
            or self.position.y > SCREEN_HEIGHT + self.radius
        ):
            self.kill()
            