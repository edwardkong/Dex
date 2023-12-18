# Dex Chess Engine

Dex is an exploratory chess engine uniquely built in Python. The engine maintains its own gamestate and move generation, employing a minimax search complemented by several optimization techniques and a rudimentary evaluation heuristic move selection. Currenetly, Dex approximately plays at a 1400 level on Lichess in Blitz/Rapid. You can [watch Dex's games](https://lichess.org/@/dex_engine/tv) or [play against it](https://lichess.org/?user=dex_engine#friend) when it's online!

## Features

| Feature                           | Benefits                                                                                   |
|-----------------------------------|--------------------------------------------------------------------------------------------|
| Bitboard Representation           | Encodes positions as 12 64-bit ints to enable efficient bitwise operations for faster computations. |
| Minimax Search w/ Alpha-Beta Pruning | Prunes unpromising move branches early in search tree, enhancing decision-making efficiency.              |
| Iterative Deepening               | Searches for the best move at increasing depths, leveraging previous results for optimization. |
| Quiescence Search                 | Addresses the horizon effect by evaluating dynamic positions more deeply.                  |
| Zobrist Hashing & Transposition Table | Reduces redundant calculations by caching previously evaluated positions.              |
| UCI Compatibility                 | Allows seamless use with popular chess GUIs and automatic play via the Lichess API.        |
| Cloud Computing                   | Offers flexibility to use local resources or serverless compute on AWS Lambda.  |


### Notes

If you have any questions or would like to contribute to Dex's development, feel free to fork the repo, create a pull request, log an issue, or start a discussion.
