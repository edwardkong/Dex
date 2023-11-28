# Dex
Chess engine
0.0.2
- Castling implemented
- Castling rights stored as bitboard
- Some optimizations
- Code cleanup


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
