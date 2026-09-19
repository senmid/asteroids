import pygame
from circleshape import CircleShape
from constants import LINE_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH, SHOT_RADIUS


class Shot(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, SHOT_RADIUS)
    
    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)
    
    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        if (
            self.position.x < -self.radius 
            or self.position.x > SCREEN_WIDTH + self.radius 
            or self.position.y < -self.radius 
            or self.position.y > SCREEN_HEIGHT + self.radius
        ):
            self.kill()
            