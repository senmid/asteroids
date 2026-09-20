import pygame
from constants import (
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHIELD_MAX_SECONDS,
)
from player import Player

class Hud:
    def __init__(self, font: pygame.font.Font) -> None:
        self.font = font
    
    def draw(
        self,
        screen: pygame.Surface,
        score: int,
        lives: int,
        fps: float,
        is_game_over: bool,
        player: Player | None = None,
    ) -> None:
        fps_text = self.font.render(f"FPS: {round(fps)}", True, "white")
        fps_rect = fps_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
        screen.blit(fps_text, fps_rect)
        if is_game_over:
            self._draw_game_over(screen, score)
            return
        score_text = self.font.render(f"Score: {score}", True, "white")
        lives_label = self.font.render("Lives:", True, "white")
        screen.blit(score_text, (10, 10))
        screen.blit(lives_label, (10, 40))
        for i in range(lives):
            Player.draw_life_icon(screen, 90 + i * 28, 52)
        if player is not None:
            self._draw_buffs(screen, player)

    def _draw_buffs(self, screen: pygame.Surface, player: Player) -> None:
        labels: list[tuple[str, str]] = []
        labels.append((f"GUN {player.weapon.upper()}", "white"))
        if player.weapon_timer > 0.0:
            labels.append((f"GUN BUFF {player.weapon_timer:.1f}", "orange"))
        labels.append((
            f"{'SHIELD ON' if player.has_shield else 'SHIELD'} "
            f"{player.shield_energy:.1f}/{SHIELD_MAX_SECONDS:.0f}",
            "cyan" if player.has_shield else "white",
        ))
        if player.speed_timer > 0.0:
            labels.append((f"SPEED! {player.speed_timer:.1f}", "yellow"))
        if player.shot_wrap_timer > 0.0:
            labels.append((f"WRAP {player.shot_wrap_timer:.1f}", "magenta"))
        if player.friction_timer > 0.0:
            labels.append((f"SLOW {player.friction_timer:.1f}", "red"))
        y = 70
        for text, color in labels:
            surface = self.font.render(text, True, color)
            screen.blit(surface, (10, y))
            y += 28

    def _draw_game_over(self, screen: pygame.Surface, score: int) -> None:
        final_score_text = self.font.render(f"Final Score: {score}", True, "white")
        final_score_rect = final_score_text.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        )
        screen.blit(final_score_text, final_score_rect)
        restart_text = self.font.render("Press Enter to restart", True, "white")
        restart_rect = restart_text.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40)
        )
        screen.blit(restart_text, restart_rect)
