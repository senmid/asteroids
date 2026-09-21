import audio
from circleshape import CircleShape
import pygame
from shot import Shot
from bomb import Bomb
from constants import (
    FRICTION_DEFECT_VALUE,
    LINE_WIDTH,
    PLAYER_BRAKE_FRICTION,
    PLAYER_FRICTION,
    PLAYER_INVULN_SECONDS,
    PLAYER_MAX_SPEED,
    PLAYER_RADIUS,
    PLAYER_THRUST,
    PLAYER_TURN_SPEED,
    SHIELD_MAX_SECONDS,
    SHIELD_PICKUP_SECONDS,
    SHIELD_REGEN_PER_SECOND,
    SHOT_WRAP_LIFE_SECONDS,
    SPEED_BOOST_SECONDS,
    SPEED_MULTIPLIER,
    FRICTION_DEFECT_SECONDS,
    SHOT_WRAP_SECONDS,
    WEAPON_BUFF_SECONDS,
    WEAPON_BUFFS,
    WEAPON_NORMAL,
    WEAPONS,
    BOMB_COOLDOWN,
    BOMB_INHERIT_VELOCITY,
    BOMB_MAX_AMMO,
    BOMB_PICKUP_AMOUNT,
    BOMBS_PER_LIFE,
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
        self.weapon = WEAPON_NORMAL
        self.weapon_timer = 0.0
        self.is_thrusting = False
        self.invulnerable_timer = 0.0
        self.shield_energy = 0.0
        self.is_shield_active = False
        self.speed_timer = 0.0
        self.shot_wrap_timer = 0.0
        self.friction_timer = 0.0
        self.bomb_ammo = BOMBS_PER_LIFE
        self.bomb_cooldown = 0.0

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
        hide_hull = self.is_invulnerable and int(
            self.invulnerable_timer * 8) % 2 == 0
        if not hide_hull:
            pygame.draw.polygon(screen, "white", self.ship(), LINE_WIDTH)
            if self.is_thrusting:
                pygame.draw.polygon(screen, "orange", self.flame())
        if self.has_shield:
            pygame.draw.circle(
                screen, "cyan", self.position, self.radius + 8, LINE_WIDTH
            )

    def rotate(self, dt: float) -> None:
        self.rotation += PLAYER_TURN_SPEED * dt

    def _speed_mult(self) -> float:
        return SPEED_MULTIPLIER if self.speed_timer > 0.0 else 1.0

    def thrust(self, dt: float) -> None:
        self.velocity += self.forward() * PLAYER_THRUST * self._speed_mult() * dt

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
        self.speed_timer = max(0.0, self.speed_timer - dt)
        self.shot_wrap_timer = max(0.0, self.shot_wrap_timer - dt)
        self.friction_timer = max(0.0, self.friction_timer - dt)
        self.weapon_timer = max(0.0, self.weapon_timer - dt)
        self.bomb_cooldown = max(0.0, self.bomb_cooldown - dt)
        self._tick_shield(dt)

    def _tick_shield(self, dt: float) -> None:
        if self.is_shield_active:
            self.shield_energy = max(0.0, self.shield_energy - dt)
            if self.shield_energy <= 0.0:
                self.is_shield_active = False
            return
        if self.shield_energy <= 0.0:
            return
        self.shield_energy = min(
            SHIELD_MAX_SECONDS,
            self.shield_energy + SHIELD_REGEN_PER_SECOND * dt,
        )

    def grant_powerup(self, kind: str) -> None:
        audio.play("pickup")
        if kind == "shield":
            self.grant_shield()
        elif kind == "speed":
            self.grant_speed()
        elif kind == "shot_wrap":
            self.grant_shot_wrap()
        elif kind == "friction":
            self.grant_friction()
        elif kind == "weapon":
            self.grant_weapon_buff()
        elif kind == "bomb":
            self.grant_bomb()

    def grant_bomb(self) -> None:
        self.bomb_ammo = min(BOMB_MAX_AMMO, self.bomb_ammo + BOMB_PICKUP_AMOUNT)

    def try_drop_bomb(self) -> bool:
        if self.bomb_cooldown > 0.0:
            return False
        if self.bomb_ammo <= 0:
            return False
        drop = self.position - self.forward() * (self.radius + 12)
        audio.play("bomb_drop")
        bomb = Bomb(drop.x, drop.y)
        bomb.velocity = self.velocity * BOMB_INHERIT_VELOCITY
        self.bomb_ammo -= 1
        self.bomb_cooldown = BOMB_COOLDOWN
        return True

    def grant_weapon_buff(self) -> None:
        self.weapon_timer = WEAPON_BUFF_SECONDS

    def _weapon_stats(self) -> dict:
        stats = dict(WEAPONS[self.weapon])
        if self.weapon_timer > 0.0:
            stats.update(WEAPON_BUFFS[self.weapon])
        return stats

    def grant_shield(self) -> None:
        self.shield_energy = min(
            SHIELD_MAX_SECONDS,
            self.shield_energy + SHIELD_PICKUP_SECONDS,
        )

    def grant_speed(self) -> None:
        self.speed_timer = SPEED_BOOST_SECONDS

    def try_toggle_shield(self) -> None:
        if self.is_shield_active:
            self.is_shield_active = False
            return
        if self.shield_energy <= 0.0:
            return
        audio.play("shield")
        self.is_shield_active = True

    def grant_shot_wrap(self) -> None:
        self.shot_wrap_timer = SHOT_WRAP_SECONDS

    def grant_friction(self) -> None:
        self.friction_timer = FRICTION_DEFECT_SECONDS

    @property
    def has_shield(self) -> bool:
        return self.is_shield_active and self.shield_energy > 0.0

    def _apply_friction(self, dt: float) -> None:
        friction = FRICTION_DEFECT_VALUE if self.friction_timer > 0.0 else PLAYER_FRICTION
        self.velocity *= friction ** (dt * 60)

    def _handle_thrust(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        self.is_thrusting = keys[pygame.K_w]
        if self.is_thrusting:
            self.thrust(dt)
        elif keys[pygame.K_s]:
            self.brake(dt)

    def _integrate(self, dt: float) -> None:
        max_speed = PLAYER_MAX_SPEED * self._speed_mult()
        if self.velocity.length() > max_speed:
            self.velocity = self.velocity.normalize() * max_speed
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
        audio.play("shoot")
        stats = self._weapon_stats()
        self.shot_cooldown = stats["cooldown"]
        for angle in stats["angles"]:
            self._spawn_shot(stats, angle)

    def _spawn_shot(self, stats: dict, angle: float) -> None:
        shot = Shot(
            self.position.x,
            self.position.y,
            radius=stats["radius"],
            color=stats["color"],
            pierce=stats["pierce"],
            blast_radius=stats["blast_radius"],
        )
        shot.velocity = self.forward().rotate(angle) * stats["speed"]
        if self.shot_wrap_timer > 0.0:
            shot.can_wrap = True
            shot.life = SHOT_WRAP_LIFE_SECONDS

    def set_weapon(self, weapon: str) -> None:
        if weapon not in WEAPONS:
            return
        self.weapon = weapon

    def respawn(self, x: float, y: float) -> None:
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.invulnerable_timer = PLAYER_INVULN_SECONDS
        self.is_shield_active = False
        self.speed_timer = 0.0
        self.shot_wrap_timer = 0.0
        self.friction_timer = 0.0
        self.weapon_timer = 0.0
        self.bomb_ammo = BOMBS_PER_LIFE
        self.bomb_cooldown = 0.0

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
        right_wing = self.position - forward * \
            (self.radius * 0.8) + right * 1.3
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
