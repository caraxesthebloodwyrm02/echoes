
export enum GameState {
  StartScreen = "START_SCREEN",
  Playing = "PLAYING",
  PowerUp = "POWER_UP",
  GameOver = "GAME_OVER",
  LevelComplete = "LEVEL_COMPLETE"
}

export enum Direction {
  Up = "UP",
  Down = "DOWN",
  Left = "LEFT",
  Right = "RIGHT",
  None = "NONE",
}

export enum Tile {
    Empty,
    Wall,
    Dot,
    PowerPellet,
    GhostGate,
}

export interface Position {
    x: number;
    y: number;
}

export enum GhostState {
    Chase,
    Frightened,
    Eaten,
}

export interface Ghost {
    id: string;
    position: Position;
    startPosition: Position;
    state: GhostState;
    color: string;
    direction: Direction;
}
