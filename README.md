#Dex Chess Engine#

Dex is an exploratory chess engine uniquely built in Python. The engine maintains its own gamestate and move generation, employing a minimax search complemented by several optimization techniques and a rudimentary evaluation heuristic move selection. Currenetly, Dex approximately plays at a 1400 level on Lichess in Blitz/Rapid. You can [watch Dex's games](https://lichess.org/@/dex_engine/tv) or [play against it](https://lichess.org/?user=dex_engine#friend) when it's online!

##Features##

Bitboard Representation: Encodes the board position as a series of 12 binary integers to enable efficient bitwise operations for faster decision making abilities.
Minimax Search with Alpha-Beta Pruning: The decision making process uses the minimax algorithm with Alpha-Beta pruning to prune unpromising move branches early.
Iterative Deepening: Searches for the best move one depth at a time, utilizing the previous depth's results to inform the next iteration about best pruning options.
Quiescence Search: The quiescence search combats the horizon effect to evaluate dynamic positions more deeply.
Zobrist Hashing & Transposition Table: Caches seen positions locally to minimize the amount of redundant calculations needed.
UCI Compatibility: Fully compatible with UCI (Universal Chess Interface) protocol, allowing it to be used with popular chess GUIs and play automatically with the Lichess API.
Cloud Computing: Can be configured to play using local resources or serverless compute with AWS Lambda.

###Notes###

If you have any questions or would like to contribute to Dex's development, feel free to fork the repo, create a pull request, log an issue, or start a discussion.
