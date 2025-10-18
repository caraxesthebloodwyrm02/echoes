import React, { useState, useEffect, useCallback, useRef } from 'react';
import { aiGameFeatures, Thought } from './src/ai/gameFeatures';
import { GameState, Direction, Position, Ghost, GhostState, Tile } from './types';
import {
  MAZE_LAYOUT,
  PACMAN_START_POS,
  GHOST_START_POS,
  INITIAL_LIVES,
  DOT_POINTS,
  POWER_PELLET_POINTS,
  GHOST_EAT_POINTS,
  POWER_PELLET_DURATION,
  GAME_SPEED,
  MAZE_WIDTH,
  MAZE_HEIGHT,
  TOTAL_DOTS
} from './constants';
import GameBoard from './components/GameBoard';

const deepCopyLayout = () => MAZE_LAYOUT.map(row => [...row]);
const deepCopyGhosts = () => GHOST_START_POS.map(g => ({ ...g, position: { ...g }, startPosition: { ...g }, state: GhostState.Chase, direction: Direction.None }));

const App: React.FC = () => {
  const [gameState, setGameState] = useState<GameState>(GameState.StartScreen);
  const [score, setScore] = useState(0);
  const [lives, setLives] = useState(INITIAL_LIVES);
  const [pacmanPos, setPacmanPos] = useState<Position>(PACMAN_START_POS);
  const [pacmanDirection, setPacmanDirection] = useState<Direction>(Direction.None);
  const [nextDirection, setNextDirection] = useState<Direction>(Direction.None);
  const [ghosts, setGhosts] = useState<Ghost[]>(deepCopyGhosts());
  const [boardData, setBoardData] = useState<Tile[][]>(deepCopyLayout());
  const [dotsEaten, setDotsEaten] = useState(0);

  const [cookMultiplier, setCookMultiplier] = useState(1);
  const [ghostsEatenInPowerUp, setGhostsEatenInPowerUp] = useState(0);
  const [cartmanPos, setCartmanPos] = useState<Position | null>(null);
  const [balance, setBalance] = useState(0);
  const [humbleScore, setHumbleScore] = useState(0);

  const gameLoopRef = useRef<number | null>(null);
  const powerUpTimeoutRef = useRef<number | null>(null);

  const resetPositions = useCallback(() => {
    setPacmanPos(PACMAN_START_POS);
    setGhosts(deepCopyGhosts());
    setPacmanDirection(Direction.None);
    setNextDirection(Direction.None);
    setCartmanPos(null); // Reset Cartman
    setHumbleScore(0); // Reset humble score on death

    if (powerUpTimeoutRef.current) {
        clearTimeout(powerUpTimeoutRef.current);
        powerUpTimeoutRef.current = null;
    }
    // If we die during powerup, revert state to Playing and disrupt balance
    if (gameState === GameState.PowerUp) {
        setGameState(GameState.Playing);
        setBalance(b => b + 1);
    }
  }, [gameState]);

  const resetLevel = useCallback(() => {
    setBoardData(deepCopyLayout());
    setDotsEaten(0);
    setBalance(0); // Restore order at the end of the day
    resetPositions();
  }, [resetPositions]);

  const initializeGame = useCallback(() => {
    setScore(0);
    setLives(INITIAL_LIVES);
    setBalance(0);
    setHumbleScore(0);
    resetLevel();
    setGameState(GameState.Playing);
  }, [resetLevel]);

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (gameState === GameState.StartScreen || gameState === GameState.GameOver) {
        if(e.key === 'Enter') initializeGame();
        return;
    }

    let newDirection: Direction | null = null;
    switch (e.key) {
      case 'ArrowUp':
      case 'w':
        newDirection = Direction.Up;
        break;
      case 'ArrowDown':
      case 's':
        newDirection = Direction.Down;
        break;
      case 'ArrowLeft':
      case 'a':
        newDirection = Direction.Left;
        break;
      case 'ArrowRight':
      case 'd':
        newDirection = Direction.Right;
        break;
    }
    if (newDirection) {
      setNextDirection(newDirection);
    }
  }, [initializeGame, gameState]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      if (gameLoopRef.current) cancelAnimationFrame(gameLoopRef.current);
      if (powerUpTimeoutRef.current) clearTimeout(powerUpTimeoutRef.current);
    };
  }, [handleKeyDown]);

  const canMove = (pos: Position, dir: Direction): boolean => {
    const { x, y } = getNextPosition(pos, dir);
    if (x < 0 || x >= MAZE_WIDTH || y < 0 || y >= MAZE_HEIGHT) return false;
    const tile = boardData[y][x];
    return tile !== Tile.Wall && tile !== Tile.GhostGate;
  };

  const getNextPosition = (pos: Position, dir: Direction): Position => {
    let { x, y } = pos;
    switch (dir) {
      case Direction.Up: y--; break;
      case Direction.Down: y++; break;
      case Direction.Left: x--; break;
      case Direction.Right: x++; break;
    }
    // Handle tunnel
    if (x < 0) x = MAZE_WIDTH - 1;
    if (x >= MAZE_WIDTH) x = 0;
    return { x, y };
  };

  const updateGame = useCallback(() => {
    // Pac-Man Movement
    let currentDirection = pacmanDirection;
    if (canMove(pacmanPos, nextDirection)) {
      currentDirection = nextDirection;
      setPacmanDirection(nextDirection);
    }

    let moved = false;
    if (canMove(pacmanPos, currentDirection)) {
      moved = true;
      const newPacmanPos = getNextPosition(pacmanPos, currentDirection);
      setPacmanPos(newPacmanPos);

      // Check for dot/pellet collision
      const tile = boardData[newPacmanPos.y][newPacmanPos.x];
      if (tile === Tile.Dot || tile === Tile.PowerPellet) {
        const newBoardData = [...boardData];
        newBoardData[newPacmanPos.y][newPacmanPos.x] = Tile.Empty;
        setBoardData(newBoardData);
        setDotsEaten(prev => prev + 1);

        if (tile === Tile.Dot) {
          setScore(s => s + DOT_POINTS);
        } else {
          setScore(s => s + POWER_PELLET_POINTS);
          setGameState(GameState.PowerUp);
          setBalance(b => b + 1); // Phase align +1
          setCartmanPos({ ...PACMAN_START_POS }); // Spawn Cartman
          setCookMultiplier(1);
          setGhostsEatenInPowerUp(0);
          setGhosts(g => g.map(ghost => ({ ...ghost, state: GhostState.Frightened })));
          if (powerUpTimeoutRef.current) clearTimeout(powerUpTimeoutRef.current);

          const humbleBonus = humbleScore * 50; // Bonus duration from being humble
          const currentPowerUpDuration = Math.max(2000, POWER_PELLET_DURATION - (balance * 500) + humbleBonus);

          powerUpTimeoutRef.current = window.setTimeout(() => {
            setGameState(GameState.Playing);
            setBalance(b => b + 1); // Phase align +1
            setCartmanPos(null); // Despawn Cartman
            setGhosts(g => g.map(ghost => ({ ...ghost, state: GhostState.Chase })));
          }, currentPowerUpDuration);
        }
      }
    }

    if (!moved) {
        // Acknowledge limitations, gain humble points
        setHumbleScore(h => h + (balance === 0 ? 2 : 1)); // Zen xDouble
    }

    // Cartman Movement
    if (gameState === GameState.PowerUp && cartmanPos) {
        let nearestGhost: Ghost | null = null;
        let minDistance = Infinity;
        ghosts.forEach(ghost => {
            if (ghost.state === GhostState.Frightened) {
                const distance = Math.abs(cartmanPos.x - ghost.position.x) + Math.abs(cartmanPos.y - ghost.position.y);
                if (distance < minDistance) {
                    minDistance = distance;
                    nearestGhost = ghost;
                }
            }
        });
        if (nearestGhost) {
            const dx = nearestGhost.position.x - cartmanPos.x;
            const dy = nearestGhost.position.y - cartmanPos.y;
            const moves: Direction[] = [];
            if (Math.abs(dx) > Math.abs(dy)) {
                if (dx > 0) moves.push(Direction.Right); else moves.push(Direction.Left);
                if (dy > 0) moves.push(Direction.Down); else moves.push(Direction.Up);
            } else {
                if (dy > 0) moves.push(Direction.Down); else moves.push(Direction.Up);
                if (dx > 0) moves.push(Direction.Right); else moves.push(Direction.Left);
            }
            for (const move of moves) {
                if (canMove(cartmanPos, move)) {
                    setCartmanPos(getNextPosition(cartmanPos, move));
                    break;
                }
            }
        }
    }

    // Ghost Movement
    setGhosts(prevGhosts => prevGhosts.map(ghost => {
        // Flee from Cartman during PowerUp
        if (gameState === GameState.PowerUp && cartmanPos && ghost.state === GhostState.Frightened) {
            const dx = ghost.position.x - cartmanPos.x;
            const dy = ghost.position.y - cartmanPos.y;
            const moves: Direction[] = [];
            if (Math.abs(dx) > Math.abs(dy)) {
                if (dx > 0) moves.push(Direction.Right); else moves.push(Direction.Left);
                if (dy > 0) moves.push(Direction.Down); else moves.push(Direction.Up);
            } else {
                if (dy > 0) moves.push(Direction.Down); else moves.push(Direction.Up);
                if (dx > 0) moves.push(Direction.Right); else moves.push(Direction.Left);
            }
            const allDirs = [Direction.Up, Direction.Down, Direction.Left, Direction.Right];
            allDirs.forEach(d => { if (!moves.includes(d)) moves.push(d); });
            for (const move of moves) {
                if (canMove(ghost.position, move)) {
                    return {...ghost, position: getNextPosition(ghost.position, move), direction: move};
                }
            }
            return ghost; // Stuck
        }
        // Default Ghost Logic
        const directions = [Direction.Up, Direction.Down, Direction.Left, Direction.Right];
        const opposite: {[key in Direction]?: Direction} = { [Direction.Up]: Direction.Down, [Direction.Down]: Direction.Up, [Direction.Left]: Direction.Right, [Direction.Right]: Direction.Left };
        let possibleMoves = directions.filter(dir => canMove(ghost.position, dir) && dir !== opposite[ghost.direction]);
        if (possibleMoves.length === 0) {
            possibleMoves = directions.filter(dir => canMove(ghost.position, dir));
        }
        if(possibleMoves.length > 0) {
            const newDirection = possibleMoves[Math.floor(Math.random() * possibleMoves.length)];
            const newPosition = getNextPosition(ghost.position, newDirection);
            return {...ghost, position: newPosition, direction: newDirection};
        }
        return ghost;
    }));

    // Ghost Collision
    ghosts.forEach((ghost) => {
      if (ghost.position.x === pacmanPos.x && ghost.position.y === pacmanPos.y) {
        if (gameState === GameState.PowerUp && ghost.state === GhostState.Frightened) {
          setScore(s => s + GHOST_EAT_POINTS * cookMultiplier);
          setCookMultiplier(m => m * 2);
          setGhostsEatenInPowerUp(g => g + 1);
          setBalance(b => Math.max(0, b - 2)); // Balance restores +2
          setGhosts(gs => gs.map(g => g.id === ghost.id ? { ...g, position: g.startPosition, state: GhostState.Chase } : g));
        } else if (ghost.state !== GhostState.Frightened) {
            if(lives - 1 <= 0) {
                setGameState(GameState.GameOver);
            } else {
                setLives(l => l - 1);
                resetPositions();
            }
        }
      }
    });

    // Check win condition
    if (dotsEaten + 1 >= TOTAL_DOTS) {
        setGameState(GameState.LevelComplete);
        setTimeout(() => {
            resetLevel();
            setGameState(GameState.Playing);
        }, 3000)
    }

  }, [pacmanPos, pacmanDirection, nextDirection, boardData, ghosts, lives, cookMultiplier, dotsEaten, gameState, resetLevel, resetPositions, cartmanPos, balance, humbleScore]);

  useEffect(() => {
    if (gameState === GameState.Playing || gameState === GameState.PowerUp) {
      const handle = setTimeout(updateGame, GAME_SPEED);
      return () => clearTimeout(handle);
    }
  }, [gameState, updateGame]);

  const Hud = () => (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 w-full text-base md:text-lg font-bold text-white px-2 py-2 uppercase tracking-widest" style={{fontFamily: "'Press Start 2P', cursive"}}>
        <div className="text-left">Score: <span className="text-yellow-400">{score}</span></div>
        <div className="text-left md:text-center">Balance: <span className={balance > 0 ? "text-red-400" : "text-cyan-400"}>{balance}</span></div>
        <div className="text-left md:text-center">Humble: <span className="text-green-400">{humbleScore}</span></div>
        <div className="text-left md:text-right">Lives: <span className="text-yellow-400">{'🟡 '.repeat(lives)}</span></div>
    </div>
  )

  const CookOverlay = () => {
    if (gameState !== GameState.PowerUp) return null;
    const size = Math.min(7, 3 + ghostsEatenInPowerUp * 0.75); // in rem
    const colorStops = ['#FF8C00', '#FF4500', '#FF0000', '#B22222', '#800000'];
    const color = colorStops[Math.min(colorStops.length-1, ghostsEatenInPowerUp)];

    return (
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none z-10 text-center">
            <h2 className="font-extrabold uppercase animate-pulse drop-shadow-[0_0_10px_rgba(255,255,255,0.8)]"
            style={{ fontSize: `${size}rem`, color: color, textShadow: `0 0 15px ${color}` }}>
                Let Bro Cook!
            </h2>
            {cookMultiplier > 1 && (
                <p className="text-white text-4xl font-bold mt-4 drop-shadow-[0_0_5px_rgba(0,0,0,1)] animate-bounce">
                    x{cookMultiplier} Multiplier!
                </p>
            )}
        </div>
    )
  }

  const ScreenOverlay: React.FC<{title: string; subtitle: string;}> = ({title, subtitle}) => (
     <div className="absolute inset-0 bg-black bg-opacity-70 flex flex-col items-center justify-center z-20 text-center p-4">
        <h1 className="text-5xl md:text-7xl font-extrabold text-yellow-400 uppercase tracking-wider mb-4" style={{textShadow: "3px 3px 0px #00008B"}}>{title}</h1>
        <p className="text-2xl text-white animate-pulse">{subtitle}</p>
    </div>
  )

  return (
    <main className="bg-gray-900 min-h-screen flex flex-col items-center justify-center p-4 font-mono select-none">
        <style>
            {`
            @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
            .animate-chomp { animation: chomp 0.4s infinite; }
            @keyframes chomp {
                0%, 100% { border-top-width: 12px; border-bottom-width: 12px; }
                50% { border-top-width: 0px; border-bottom-width: 0px; }
            }
            `}
        </style>
        <div className="w-full max-w-2xl mb-4">
            <Hud />
        </div>
        <div className="relative">
            {gameState === GameState.StartScreen && <ScreenOverlay title="Pac-Man" subtitle="Press Enter to Start" />}
            {gameState === GameState.GameOver && <ScreenOverlay title="Game Over" subtitle="Press Enter to Restart" />}
            {gameState === GameState.LevelComplete && <ScreenOverlay title="Level Clear!" subtitle="Get Ready..." />}
            <CookOverlay/>
            <GameBoard
                pacmanPos={pacmanPos}
                pacmanDirection={pacmanDirection}
                ghosts={ghosts}
                boardData={boardData}
                isFrightened={gameState === GameState.PowerUp}
                cartmanPos={cartmanPos}
            />
        </div>
    </main>
  );
};

export default App;
