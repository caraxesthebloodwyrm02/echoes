import React from 'react';
import { Ghost, Position, Tile } from '../types';
import { TILE_SIZE, MAZE_LAYOUT } from '../constants';

interface GameBoardProps {
  pacmanPos: Position;
  pacmanDirection: string;
  ghosts: Ghost[];
  boardData: Tile[][];
  isFrightened: boolean;
  cartmanPos: Position | null;
}

const Pacman: React.FC<{ position: Position, direction: string }> = ({ position, direction }) => {
  const rotationClasses: { [key: string]: string } = {
    RIGHT: 'rotate-0',
    DOWN: 'rotate-90',
    LEFT: 'rotate-180',
    UP: '-rotate-90',
    NONE: 'rotate-0'
  };

  return (
    <div
      className="absolute transition-all duration-100 ease-linear"
      style={{ left: position.x * TILE_SIZE, top: position.y * TILE_SIZE, width: TILE_SIZE, height: TILE_SIZE }}
    >
      <div className={`w-full h-full ${rotationClasses[direction]}`}>
          <div className="w-0 h-0
              border-t-[12px] border-t-transparent
              border-l-[24px] border-l-yellow-400
              border-b-[12px] border-b-transparent
              rounded-full animate-chomp"
          ></div>
      </div>
    </div>
  );
};

const GhostComponent: React.FC<{ ghost: Ghost; isFrightened: boolean }> = ({ ghost, isFrightened }) => {
  const bgColor = isFrightened ? 'bg-blue-600 animate-pulse' : ghost.color;
  return (
    <div
      className={`absolute transition-all duration-150 ease-linear rounded-t-full ${bgColor}`}
      style={{ left: ghost.position.x * TILE_SIZE, top: ghost.position.y * TILE_SIZE, width: TILE_SIZE, height: TILE_SIZE }}
    >
        <div className="absolute bottom-1 w-full flex justify-center space-x-1">
            <div className="w-2 h-2 bg-white rounded-full">
                <div className="w-1 h-1 bg-black rounded-full relative top-0.5 left-0.5"></div>
            </div>
            <div className="w-2 h-2 bg-white rounded-full">
                <div className="w-1 h-1 bg-black rounded-full relative top-0.5 left-0.5"></div>
            </div>
        </div>
    </div>
  );
};

const Cartman: React.FC<{ position: Position }> = ({ position }) => {
  return (
    <div
      className="absolute transition-all duration-150 ease-linear flex flex-col items-center"
      style={{ left: position.x * TILE_SIZE, top: position.y * TILE_SIZE, width: TILE_SIZE, height: TILE_SIZE }}
      aria-label="Eric Cartman"
    >
      {/* Hat */}
      <div className="w-[80%] h-[25%] bg-cyan-400 rounded-t-sm relative flex justify-center">
        <div className="absolute bottom-0 w-full h-[30%] bg-yellow-400"></div>
        <div className="absolute -top-1 w-2 h-2 bg-yellow-400 rounded-full"></div>
      </div>
      {/* Face */}
      <div className="w-[70%] h-[20%] bg-orange-200"></div>
       {/* Body */}
      <div className="w-full h-[55%] bg-red-600 rounded-b-sm relative">
        {/* Buttons */}
        <div className="absolute top-1 left-1/2 -translate-x-1/2 w-0.5 h-0.5 bg-black rounded-full"></div>
        <div className="absolute top-2 left-1/2 -translate-x-1/2 w-0.5 h-0.5 bg-black rounded-full"></div>
        <div className="absolute top-3 left-1/2 -translate-x-1/2 w-0.5 h-0.5 bg-black rounded-full"></div>
      </div>
    </div>
  );
};


const GameBoard: React.FC<GameBoardProps> = ({ pacmanPos, pacmanDirection, ghosts, boardData, isFrightened, cartmanPos }) => {
  return (
    <div
      className="relative bg-black border-4 border-blue-800 shadow-lg shadow-cyan-400/30"
      style={{
        width: MAZE_LAYOUT[0].length * TILE_SIZE,
        height: MAZE_LAYOUT.length * TILE_SIZE,
      }}
    >
      {boardData.map((row, y) =>
        row.map((tile, x) => {
          if (tile === Tile.Wall) {
            return (
              <div
                key={`${x}-${y}`}
                className="absolute bg-blue-900"
                style={{ left: x * TILE_SIZE, top: y * TILE_SIZE, width: TILE_SIZE, height: TILE_SIZE }}
              ></div>
            );
          }
          if (tile === Tile.Dot) {
            return (
              <div
                key={`${x}-${y}`}
                className="absolute flex items-center justify-center"
                style={{ left: x * TILE_SIZE, top: y * TILE_SIZE, width: TILE_SIZE, height: TILE_SIZE }}
              >
                <div className="w-1.5 h-1.5 bg-yellow-200 rounded-full"></div>
              </div>
            );
          }
          if (tile === Tile.PowerPellet) {
            return (
              <div
                key={`${x}-${y}`}
                className="absolute flex items-center justify-center"
                style={{ left: x * TILE_SIZE, top: y * TILE_SIZE, width: TILE_SIZE, height: TILE_SIZE }}
              >
                <div className="w-4 h-4 bg-yellow-300 rounded-full animate-pulse"></div>
              </div>
            );
          }
          return null;
        })
      )}
      <Pacman position={pacmanPos} direction={pacmanDirection} />
      {ghosts.map((ghost) => (
        <GhostComponent key={ghost.id} ghost={ghost} isFrightened={isFrightened} />
      ))}
      {cartmanPos && <Cartman position={cartmanPos} />}
    </div>
  );
};

export default GameBoard;
