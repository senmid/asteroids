from circleshape import CircleShape
from constants import LINE_WIDTH, PLAYER_BRAKE_FRICTION, PLAYER_FRICTION, PLAYER_MAX_SPEED, PLAYER_RADIUS, PLAYER_SHOOT_COOLDOWN_SECONDS, PLAYER_SHOOT_SPEED, PLAYER_THRUST, PLAYER_TURN_SPEED
import pygame
from shot import Shot


class Player(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shot_cooldown = 0
        self.is_thrusting = False
    
    def forward(self) -> pygame.Vector2:
        return pygame.Vector2(0, 1).rotate(self.rotation)

    def triangle(self) -> list[pygame.Vector2]:
        forward = self.forward()
        right = forward.rotate(90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]
    
    def flame(self) -> list[pygame.Vector2]:
        forward = self.forward()
        back = self.position - forward * self.radius
        tip = back - forward * (self.radius * 0.8)
        side = forward.rotate(90) * (self.radius * 0.4)
        return [back - side, back + side, tip]

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.polygon(screen, "white", self.triangle(), LINE_WIDTH)
        if self.is_thrusting:
            pygame.draw.polygon(screen, "orange", self.flame())

    def rotate(self, dt: float) -> None:
        self.rotation += PLAYER_TURN_SPEED * dt

    def thrust(self, dt: float) -> None:
        self.velocity += self.forward() * PLAYER_THRUST * dt
    
    def brake(self, dt: float) -> None:
        self.velocity *= max(0, 1 - PLAYER_BRAKE_FRICTION * dt)

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        self.velocity *= PLAYER_FRICTION
        self.is_thrusting = keys[pygame.K_w]
        if keys[pygame.K_w]:
            self.thrust(dt)
        elif keys[pygame.K_s]:
            self.brake(dt)
        if self.velocity.length() > PLAYER_MAX_SPEED:
            self.velocity = self.velocity.normalize() * PLAYER_MAX_SPEED
        self.position += self.velocity * dt
        self.shot_cooldown -= dt
        self.wrap_position()
        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_SPACE] or mouse[0]:
            self.shoot()
    
    def shoot(self) -> None:
        if self.shot_cooldown > 0:
            return
        self.shot_cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS
        shot = Shot(self.position.x, self.position.y)
        shot.velocity = self.forward() * PLAYER_SHOOT_SPEED
