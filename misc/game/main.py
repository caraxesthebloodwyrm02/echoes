import pygame
import sys
from enum import Enum
from dataclasses import dataclass
from typing import Tuple, List, Optional

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 32

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NONE = (0, 0)


class Tile(Enum):
    EMPTY = 0
    WALL = 1
    DOT = 2
    POWER_PELLET = 3
    GHOST_GATE = 4


@dataclass
class Position:
    x: int
    y: int


class GhostState(Enum):
    CHASE = 0
    FRIGHTENED = 1
    EATEN = 2


class GameState(Enum):
    START_SCREEN = 0
    PLAYING = 1
    GAME_OVER = 2
    LEVEL_COMPLETE = 3


class Ghost:
    def __init__(self, x: int, y: int, color: Tuple[int, int, int]):
        self.position = Position(x, y)
        self.start_position = Position(x, y)
        self.state = GhostState.CHASE
        self.color = color
        self.direction = Direction.LEFT
        self.speed = 2

    def update(self):
        # Basic movement logic (to be expanded)
        dx, dy = self.direction.value
        self.position.x += dx * self.speed
        self.position.y += dy * self.speed

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            (
                self.position.x * TILE_SIZE + TILE_SIZE // 2,
                self.position.y * TILE_SIZE + TILE_SIZE // 2,
            ),
            TILE_SIZE // 2 - 2,
        )


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Echoes Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.START_SCREEN

        # Initialize game objects
        self.ghosts = [
            Ghost(10, 10, (255, 0, 0)),  # Red ghost
            Ghost(12, 14, (255, 192, 203)),  # Pink ghost
            Ghost(14, 10, (0, 255, 255)),  # Cyan ghost
            Ghost(16, 14, (255, 165, 0)),  # Orange ghost
        ]

        # Simple level layout (0=empty, 1=wall, 2=dot, 3=power pellet, 4=ghost gate)
        self.level = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 2, 2, 1, 1, 2, 1],
            [1, 3, 1, 2, 2, 2, 2, 1, 2, 1],
            [1, 2, 2, 2, 1, 1, 2, 2, 2, 1],
            [1, 2, 1, 2, 2, 2, 2, 1, 2, 1],
            [1, 2, 1, 2, 1, 1, 2, 1, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 1, 1, 1, 1, 2, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif (
                    event.key == pygame.K_SPACE and self.state == GameState.START_SCREEN
                ):
                    self.state = GameState.PLAYING

    def update(self):
        if self.state == GameState.PLAYING:
            for ghost in self.ghosts:
                ghost.update()

    def draw(self):
        self.screen.fill(BLACK)

        if self.state == GameState.START_SCREEN:
            font = pygame.font.Font(None, 36)
            text = font.render("Press SPACE to Start", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)

        elif self.state == GameState.PLAYING:
            # Draw level
            for y, row in enumerate(self.level):
                for x, tile in enumerate(row):
                    rect = pygame.Rect(
                        x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE
                    )
                    if tile == 1:  # Wall
                        pygame.draw.rect(self.screen, BLUE, rect)
                    elif tile == 2:  # Dot
                        pygame.draw.circle(
                            self.screen,
                            WHITE,
                            (
                                x * TILE_SIZE + TILE_SIZE // 2,
                                y * TILE_SIZE + TILE_SIZE // 2,
                            ),
                            2,
                        )
                    elif tile == 3:  # Power pellet
                        pygame.draw.circle(
                            self.screen,
                            WHITE,
                            (
                                x * TILE_SIZE + TILE_SIZE // 2,
                                y * TILE_SIZE + TILE_SIZE // 2,
                            ),
                            5,
                        )

            # Draw ghosts
            for ghost in self.ghosts:
                ghost.draw(self.screen)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
