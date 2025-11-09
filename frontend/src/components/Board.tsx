import type { MoveResponse } from "../types";

interface BoardProps {
  board: string[];
  onCellClick: (position: number) => void;
  disabled: boolean;
  lastMove: MoveResponse | null;
}

export default function Board({ board, onCellClick, disabled, lastMove }: BoardProps) {
  console.log("Board rendered:", board);

  const getClassName = (position: number) => {
    const isLastMove = lastMove?.position === position || lastMove?.ai_move === position;

    const baseClass =
      "w-28 h-28 text-5xl font-bold flex items-center justify-center cursor-pointer transition-all duration-200 rounded-xl disabled:cursor-not-allowed";

    if (isLastMove) {
      return `${baseClass} bg-yellow-400/30 backdrop-blur border-2 border-yellow-300 shadow-lg transform scale-105`;
    }

    return `${baseClass} bg-white/20 backdrop-blur border-2 border-white/30 hover:bg-white/30 hover:scale-105 hover:shadow-xl disabled:hover:scale-100 disabled:hover:bg-white/20`;
  };

  const getCellContent = (cell: string) => {
    if (cell === "X") return "X";
    if (cell === "O") return "O";
    return "";
  };

  return (
    <div className="grid grid-cols-3 gap-3 p-6 bg-white/5 backdrop-blur rounded-2xl shadow-2xl border border-white/20">
      {board.map((cell, index) => (
        <button
          key={index}
          onClick={() => onCellClick(index)}
          disabled={disabled || cell !== " "}
          className={getClassName(index)}
          style={{
            color: cell === "X" ? "#60a5fa" : cell === "O" ? "#f87171" : "transparent",
            textShadow: cell !== " " ? "0 0 10px rgba(255,255,255,0.5)" : "none",
          }}
        >
          {getCellContent(cell)}
        </button>
      ))}
    </div>
  );
}
