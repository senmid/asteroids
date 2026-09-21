from pathlib import Path
import pygame
from constants import (
    MUSIC_DUCKED,
    MUSIC_VOLUME,
    PICKUP_CHANNEL,
    SFX_VOLUMES,
    VOICE_CHANNEL,
    VOICE_VOLUME,
)

ASSETS = Path("assets")

_sfx: dict[str, pygame.mixer.Sound] = {}
_voice: dict[str, pygame.mixer.Sound] = {}
_is_muted = False


def load() -> None:
    sfx_dir = ASSETS / "sfx"
    if sfx_dir.is_dir():
        for path in sfx_dir.glob("*.ogg"):
            sound = pygame.mixer.Sound(path)
            sound.set_volume(SFX_VOLUMES.get(path.stem, 0.25))
            _sfx[path.stem] = sound
    voice_dir = ASSETS / "voice"
    if voice_dir.is_dir():
        for path in voice_dir.glob("*.ogg"):
            sound = pygame.mixer.Sound(path)
            sound.set_volume(VOICE_VOLUME)
            _voice[path.stem] = sound


def play(name: str) -> None:
    if _is_muted:
        return
    sound = _sfx.get(name)
    if sound is None:
        return
    if name == "pickup":
        channel = pygame.mixer.Channel(PICKUP_CHANNEL)
        if channel.get_busy():
            return
        channel.play(sound)
        return
    sound.play()


def play_voice(name: str) -> None:
    if _is_muted:
        return
    sound = _voice.get(name)
    if sound is None:
        return

    channel = pygame.mixer.Channel(VOICE_CHANNEL)
    if channel.get_busy():
        return

    pygame.mixer.music.set_volume(MUSIC_DUCKED)
    channel.play(sound)


def play_music() -> None:
    path = ASSETS / "music" / "bgm.ogg"
    if not path.is_file():
        return

    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(MUSIC_VOLUME)
    pygame.mixer.music.play(loops=-1)


def tick() -> None:
    if _is_muted:
        return
    busy = pygame.mixer.Channel(VOICE_CHANNEL).get_busy()
    pygame.mixer.music.set_volume(MUSIC_DUCKED if busy else MUSIC_VOLUME)


def is_muted() -> bool:
    return _is_muted


def toggle_muted() -> None:
    global _is_muted
    _is_muted = not _is_muted
    if _is_muted:
        pygame.mixer.music.pause()
        pygame.mixer.stop()
        return
    pygame.mixer.unpause()
    pygame.mixer.music.unpause()
    pygame.mixer.music.set_volume(MUSIC_VOLUME)
