# Dex Chess engine


0.0.3
- Move generation improvement with attack maps
- checkmate and stalemate evaluation
- check if a move is a capture, prioritize for move ordering in AB pruning
- Move ordering
- Various edge cases involving castling, pins, en passant

0.0.2
- Castling implemented
- Castling rights stored as bitboard
- Some optimizations
- Code cleanup
  
First bot win!
12.11.26am 11.29.2023
bernstein-2ply 1437 (0-1) dex_engine 1260
https://lichess.org/STazc9uN/black


0.0.1

Features:
Communicate with LiChess API using UCI
- Accept challenges
- Start new game
- Create position given move set from GUI
- Generate next move
- Send next move to GUI

Move Generation
- Checks all legal moves of all pieces for a color
- Does not handle castling or en passant yet
- Can check if a square is in scope of a piece or is occupied
