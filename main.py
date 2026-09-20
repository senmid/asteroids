import pygame
from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import PLAYER_LIVES, PLAYER_RESPAWN_CLEAR_RADIUS, SCREEN_HEIGHT, SCREEN_WIDTH
from logger import log_state, log_event
from player import Player
from shot import Shot

def main():
    pygame.init()
    clock = pygame.time.Clock()
    dt = 0.0
    score = 0
    lives = PLAYER_LIVES
    is_game_over = False
    font = pygame.font.SysFont("Arial", 24)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    background = pygame.image.load("assets/background.jpg").convert_alpha()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable)
    AsteroidField()
    Shot.containers = (drawable, updatable, shots)
    Player.containers = (updatable, drawable)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if (
                event.type == pygame.KEYDOWN 
                and event.key == pygame.K_RETURN
                and is_game_over
            ):
                lives = PLAYER_LIVES
                score = 0
                is_game_over = False
                for asteroid in asteroids:
                    asteroid.kill()
                for shot in shots:
                    shot.kill()
                player.respawn(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        if not is_game_over:
            updatable.update(dt)
            for asteroid in asteroids:
                for shot in shots:
                    if asteroid.collides_with(shot):
                        log_event("asteroid_shot")
                        shot.kill()
                        score += asteroid.split()
                if asteroid.collides_with(player):
                    if player.is_invulnerable():
                        continue
                    lives -= 1
                    log_event("player_hit")
                    if lives <= 0:
                        is_game_over = True
                        print(f"Final Score: {score}")
                        print("Game Over! Press Enter to restart")
                    else:
                        player.respawn(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                        for asteroid in list(asteroids):
                            if asteroid.position.distance_to(player.position) <= PLAYER_RESPAWN_CLEAR_RADIUS:
                                asteroid.kill()
                    break
        screen.blit(background, (0, 0))
        screen.blit(overlay, (0, 0))
        score_text = font.render(f"Score: {score}", True, "white")
        fps_text = font.render(f"FPS: {round(clock.get_fps())}", True, "white")
        fps_rect = fps_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
        screen.blit(fps_text, fps_rect)
        lives_label = font.render("Lives:", True, "white")
        if is_game_over:
            final_score_text = font.render(f"Final Score: {score}", True, "white")
            final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            screen.blit(final_score_text, final_score_rect)
            restart_text = font.render("Press Enter to restart", True, "white")
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40))
            screen.blit(restart_text, restart_rect)
        else:
            screen.blit(score_text, (10, 10))
            screen.blit(lives_label, (10, 40))
            for i in range(lives):
                Player.draw_life_icon(screen, 90 + i * 28, 52)
        for sprite in drawable:
            sprite.draw(screen)
        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()
