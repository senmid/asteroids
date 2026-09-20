import random
import pygame
from circleshape import CircleShape
from constants import ASTEROID_MIN_RADIUS


class Explosion(CircleShape):
    def __init__(
        self,
        x: float,
        y: float,
        velocity: pygame.Vector2,
        life: float,
        color: str,
    ) -> None:
        super().__init__(x, y, 2)
        self.velocity = velocity
        self.life = life
        self.color = color

    def update(self, dt: float) -> None:
        self.move(dt)
        self.life -= dt
        if self.life <= 0:
            self.kill()

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, self.color, self.position, self.radius)

    @staticmethod
    def _burst_for_radius(radius: float) -> tuple[int, float, float, str]:
        if radius <= ASTEROID_MIN_RADIUS:
            return 10, 50, 150, "white"
        if radius <= ASTEROID_MIN_RADIUS * 2:
            return 16, 80, 220, "orange"
        return 22, 100, 280, "yellow"

    @staticmethod
    def _spawn(
        x: float,
        y: float,
        count: int,
        speed_min: float,
        speed_max: float,
        color: str,
    ) -> None:
        for _ in range(count):
            angle = random.uniform(0, 360)
            speed = random.uniform(speed_min, speed_max)
            velocity = pygame.Vector2(0, 1).rotate(angle) * speed
            Explosion(x, y, velocity, life=random.uniform(0.2, 0.6), color=color)

    @staticmethod
    def spawn_explosions(x: float, y: float, radius: float) -> None:
        count, speed_min, speed_max, color = Explosion._burst_for_radius(radius)
        Explosion._spawn(x, y, count, speed_min, speed_max, color)

    @staticmethod
    def spawn_player_explosion(x: float, y: float) -> None:
        Explosion._spawn(x, y, count=20, speed_min=80, speed_max=260, color="orange")