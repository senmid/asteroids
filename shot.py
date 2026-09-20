import pygame
from circleshape import CircleShape
from constants import (
    SHOT_RADIUS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


class Shot(CircleShape):
    def __init__(
        self,
        x: float,
        y: float,
        radius: float = SHOT_RADIUS,
        color: str = "white",
        pierce: int = 1,
        blast_radius: float = 0.0,
    ) -> None:
        super().__init__(x, y, radius)
        self.can_wrap = False
        self.life = 0.0
        self.color = color
        self.pierce_left = pierce
        self.blast_radius = blast_radius

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, self.color, self.position, self.radius)
    
    def update(self, dt: float) -> None:
        self.move(dt)
        if self.can_wrap:
            self.life -= dt
            if self.life <= 0:
                self.kill()
                return
            self.wrap_position()
            return
        if (
            self.position.x < -self.radius
            or self.position.x > SCREEN_WIDTH + self.radius
            or self.position.y < -self.radius
            or self.position.y > SCREEN_HEIGHT + self.radius
        ):
            self.kill()
            