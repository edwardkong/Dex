// script.js
document.addEventListener("DOMContentLoaded", () => {
    const board = document.getElementById("chessboard");
    initBoard(board);
    placeInitialPieces(board);
    setupClickToMove();
  });
  
  function initBoard(board) {
    const rows = "87654321";
    const cols = "abcdefgh";
    let isDark = false;
    for (let row of rows) {
      for (let col of cols) {
        const square = document.createElement('div');
        square.className = `square ${isDark ? 'dark' : 'light'}`;
        square.id = `${col}${row}`;
        board.appendChild(square);
        isDark = !isDark;
      }
      isDark = !isDark;
    }
  }
  
  function placeInitialPieces(board) {
    const initialLayout = {
      a8: '♜', b8: '♞', c8: '♝', d8: '♛', e8: '♚', f8: '♝', g8: '♞', h8: '♜',
      a7: '♟', b7: '♟', c7: '♟', d7: '♟', e7: '♟', f7: '♟', g7: '♟', h7: '♟',
      a2: '♙', b2: '♙', c2: '♙', d2: '♙', e2: '♙', f2: '♙', g2: '♙', h2: '♙',
      a1: '♖', b1: '♘', c1: '♗', d1: '♕', e1: '♔', f1: '♗', g1: '♘', h1: '♖'
    };
  
    for (let position in initialLayout) {
      const piece = document.createElement('div');
      piece.className = 'piece';
      piece.textContent = initialLayout[position];
      piece.id = position;  // Assign ID based on position for easy tracking
      document.getElementById(position).appendChild(piece);
    }
  }
  
  function setupClickToMove() {
    const squares = document.querySelectorAll('.square');
    let selectedPiece = null;
  
    squares.forEach(square => {
      square.addEventListener('click', function() {
        if (selectedPiece && (square.hasChildNodes() || square === selectedPiece.parentNode)) {
          // Move the selected piece to the new square
          square.appendChild(selectedPiece);
          selectedPiece = null;
        } else if (square.firstChild && square.firstChild.classList.contains('piece')) {
          // Select the piece
          if (selectedPiece) {
            selectedPiece.classList.remove('selected');
          }
          selectedPiece = square.firstChild;
          selectedPiece.classList.add('selected');
        } else {
          // Deselect if clicking on an empty square
          if (selectedPiece) {
            selectedPiece.classList.remove('selected');
            selectedPiece = null;
          }
        }
      });
    });
  }
  