from circleshape import CircleShape
import pygame
from shot import Shot
from constants import (
    LINE_WIDTH,
    PLAYER_BRAKE_FRICTION,
    PLAYER_FRICTION,
    PLAYER_INVULN_SECONDS,
    PLAYER_MAX_SPEED,
    PLAYER_RADIUS,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    PLAYER_SHOOT_SPEED,
    PLAYER_THRUST,
    PLAYER_TURN_SPEED,
)


def point_in_triangle(
    p: pygame.Vector2,
    a: pygame.Vector2,
    b: pygame.Vector2,
    c: pygame.Vector2,
) -> bool:
    ab = b - a
    bc = c - b
    ca = a - c
    c1 = ab.cross(p - a)
    c2 = bc.cross(p - b)
    c3 = ca.cross(p - c)
    has_neg = (c1 < 0) or (c2 < 0) or (c3 < 0)
    has_pos = (c1 > 0) or (c2 > 0) or (c3 > 0)
    return not (has_neg and has_pos)


def distance_point_to_segment(
    p: pygame.Vector2,
    a: pygame.Vector2,
    b: pygame.Vector2,
) -> float:
    ab = b - a
    length_sq = ab.length_squared()
    if length_sq == 0:
        return p.distance_to(a)
    t = (p - a).dot(ab) / length_sq
    t = max(0.0, min(1.0, t))
    closest = a + ab * t
    return p.distance_to(closest)


class Player(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shot_cooldown = 0
        self.is_thrusting = False
        self.invulnerable_timer = 0.0

    def forward(self) -> pygame.Vector2:
        return pygame.Vector2(0, 1).rotate(self.rotation)

    def ship(self) -> list[pygame.Vector2]:
        forward = self.forward()
        right = forward.rotate(90) * self.radius / 1.5
        nose = self.position + forward * self.radius
        rear_center = self.position - forward * (self.radius * 0.4)
        left_wing = self.position - forward * (self.radius * 0.8) - right * 1.3
        right_wing = self.position - forward * \
            (self.radius * 0.8) + right * 1.3
        left_indent = self.position - forward * \
            (self.radius * 0.5) - right * 0.6
        right_indent = self.position - forward * \
            (self.radius * 0.5) + right * 0.6
        return [nose, right_indent, right_wing, rear_center, left_wing, left_indent]

    def flame(self) -> list[pygame.Vector2]:
        forward = self.forward()
        back = self.position - forward * self.radius
        tip = back - forward * (self.radius * 0.8)
        side = forward.rotate(90) * (self.radius * 0.4)
        return [back - side, back + side, tip]

    def draw(self, screen: pygame.Surface) -> None:
        if self.is_invulnerable and int(self.invulnerable_timer * 8) % 2 == 0:
            return
        pygame.draw.polygon(screen, "white", self.ship(), LINE_WIDTH)
        if self.is_thrusting:
            pygame.draw.polygon(screen, "orange", self.flame())

    def rotate(self, dt: float) -> None:
        self.rotation += PLAYER_TURN_SPEED * dt

    def thrust(self, dt: float) -> None:
        self.velocity += self.forward() * PLAYER_THRUST * dt

    def brake(self, dt: float) -> None:
        self.velocity *= max(0, 1 - PLAYER_BRAKE_FRICTION * dt)

    def update(self, dt: float) -> None:
        self._tick_timers(dt)
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        self._apply_friction(dt)
        self._handle_thrust(dt, keys)
        self._integrate(dt)
        self._handle_steering(dt, keys)
        self._handle_fire(keys, mouse)

    def _tick_timers(self, dt: float) -> None:
        self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)
        self.shot_cooldown -= dt

    def _apply_friction(self, dt: float) -> None:
        self.velocity *= PLAYER_FRICTION ** (dt * 60)

    def _handle_thrust(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        self.is_thrusting = keys[pygame.K_w]
        if self.is_thrusting:
            self.thrust(dt)
        elif keys[pygame.K_s]:
            self.brake(dt)

    def _integrate(self, dt: float) -> None:
        if self.velocity.length() > PLAYER_MAX_SPEED:
            self.velocity = self.velocity.normalize() * PLAYER_MAX_SPEED
        self.move(dt)
        self.wrap_position()

    def _handle_steering(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)

    def _handle_fire(
        self,
        keys: pygame.key.ScancodeWrapper,
        mouse: tuple[bool, bool, bool],
    ) -> None:
        if keys[pygame.K_SPACE] or mouse[0]:
            self.shoot()

    def shoot(self) -> None:
        if self.shot_cooldown > 0:
            return
        self.shot_cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS
        shot = Shot(self.position.x, self.position.y)
        shot.velocity = self.forward() * PLAYER_SHOOT_SPEED

    def respawn(self, x: float, y: float) -> None:
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.invulnerable_timer = PLAYER_INVULN_SECONDS

    @property
    def is_invulnerable(self) -> bool:
        return self.invulnerable_timer > 0.0

    @staticmethod
    def draw_life_icon(screen: pygame.Surface, x: float, y: float, radius: float = 10) -> None:
        width = radius * 1.2
        height = radius * 1.2
        top_center = pygame.Vector2(x, y - height * 0.2)
        bottom_tip = pygame.Vector2(x, y + height)
        left_shoulder = pygame.Vector2(x - width, y - height * 0.4)
        right_shoulder = pygame.Vector2(x + width, y - height * 0.4)
        left_lobe = pygame.Vector2(x - width * 0.5, y - height * 0.9)
        right_lobe = pygame.Vector2(x + width * 0.5, y - height * 0.9)
        heart_points = [
            top_center,
            left_lobe,
            left_shoulder,
            bottom_tip,
            right_shoulder,
            right_lobe
        ]
        pygame.draw.polygon(screen, "white", heart_points)

    def triangle(self) -> tuple[pygame.Vector2, pygame.Vector2, pygame.Vector2]:
        forward = self.forward()
        right = forward.rotate(90) * self.radius / 1.5
        nose = self.position + forward * self.radius
        left_wing = self.position - forward * (self.radius * 0.8) - right * 1.3
        right_wing = self.position - forward * (self.radius * 0.8) + right * 1.3
        return nose, right_wing, left_wing

    def collides_with_asteroid(self, asteroid: CircleShape) -> bool:
        a, b, c = self.triangle()
        center = asteroid.position
        radius = asteroid.radius
        if point_in_triangle(center, a, b, c):
            return True
        for p1, p2 in ((a, b), (b, c), (c, a)):
            if distance_point_to_segment(center, p1, p2) <= radius:
                return True
        return False
