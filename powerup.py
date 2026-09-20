import random
import pygame
from circleshape import CircleShape
from constants import (
    LINE_WIDTH,
    POWERUP_DRIFT_SPEED,
    POWERUP_LIFETIME_SECONDS,
    POWERUP_RADIUS
)


KIND_COLORS = {
    "shield": "cyan",
    "speed": "yellow",
    "shot_wrap": "magenta",
    "friction": "red",
    "weapon": "white",
}


class Powerup(CircleShape):
    def __init__(self, x: float, y: float, kind: str) -> None:
        super().__init__(x, y, POWERUP_RADIUS)
        self.kind = kind
        self.life = POWERUP_LIFETIME_SECONDS
        angle = random.uniform(0, 360)
        self.velocity = pygame.Vector2(0, 1).rotate(angle) * POWERUP_DRIFT_SPEED

    def draw(self, screen: pygame.Surface) -> None:
        color = KIND_COLORS.get(self.kind, "white")
        pygame.draw.circle(screen, color, self.position, self.radius, LINE_WIDTH)
        if self.kind == "shield":
            pygame.draw.circle(
                screen, color, self.position, self.radius * 0.45, LINE_WIDTH
            )
        elif self.kind == "speed":
            tip = self.position + pygame.Vector2(0, -self.radius * 0.7)
            pygame.draw.line(screen, color, self.position, tip, LINE_WIDTH)
        elif self.kind == "shot_wrap":
            pygame.draw.circle(
                screen, color, self.position, self.radius * 0.35, LINE_WIDTH
            )
        elif self.kind == "friction":
            left = self.position + pygame.Vector2(-self.radius * 0.4, 0)
            right = self.position + pygame.Vector2(self.radius * 0.4, 0)
            pygame.draw.line(screen, color, left, right, LINE_WIDTH)
        elif self.kind == "weapon":
            tip = self.position + pygame.Vector2(0, -self.radius * 0.6)
            pygame.draw.line(screen, color, self.position, tip, LINE_WIDTH)
    
    def update(self, dt: float) -> None:
        self.life -= dt
        if self.life <= 0:
            self.kill()
            return
        self.move(dt)
        self.wrap_position()
    

