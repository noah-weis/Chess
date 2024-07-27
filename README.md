# Project Chessbot
##### Author: Noah Weis
##### Contact: njdweis@gmail.com
---

## v0.1_2PlayerChess

This is an early draft of my chess bot project. There are multiple known issues, and likely many unknown ones. Information on features, missing features, and known issues are all listed below.
**All such information are from the perspective of the end goal of a working chess engine, not from the perspective of a chess bot as that has a lot more missing features that are not in the current priorities of the project.**

### Why?

Building a chess bot has been a dream of mine since I began programming, as I always thought it would be an interesting project that others could appreciate. As I got into programming, I started to fall even more in love with the idea of building a chess bot as I started to realize the massive complications that would come with this endeavor, and the challenge that this would provide. Finally, I pulled the trigger after watching Sebastian Lague's video: [Coding Adventure: Chess](https://www.youtube.com/watch?v=U4ogK0MIzqk). If you would like an engaging account of what the process of building this is like, I promise you his video is more interesting than my glorified blog posts.

### Features
- Move validation
    - When selecting a piece, the board will highlight all valid pieces that the piece can make
    - This includes not highlighting/allowing moves that will put you in check<sup>1</sup>
- Checkmate/Check<sup>1</sup>
- Board setup using FEN
- Piece logic<sup>2</sup>
    - Pieces are limited to moving by the rules of the game

### Missing Features
- En passant
- Draw
    - Both via repeat moves and the halfmove rule.
- Pawn Promotion
- Sound
    - Chess is a lot more enjoyable when there's a satisfying *CLONK* sound when you move a piece. 

### Known Issues
 - Lots of redundant code that can be simplified
     - Especially in `board.handle_click()`
- <sup>1</sup> This is extremely unoptimized.
    - Right now, to find valid moves, it goes through every single possible move of the piece that you click, performs the move, decides if this is a check, and then resets the board back to the original state before trying the next move.
    - It does this every single time a piece is clicked, even if the piece has been clicked since the last update to the board.
    - For checkmate, it is constantly checking if any piece on a given side of the board has any valid moves. If no piece on X side has a valid move, it is checkmate. 
        - This is awful because there are a lot of repeat checks.
- <sup>2</sup> I think.

### Future plans (In no order)
- <sup>1</sup> Instead of the current method of move validation and checkmate validation, here's the new planned logic.
    - After every move, check for all valid moves for every piece on the board 1 time, and store this `piece.valid_moves` so that if the player clicks on that piece again, it can access `valid_moves` without having to do any actual work.
    - Once all valid moves for every piece have been found, make 1 checkmate check for each side. Repeat after each move.
- <sup>2</sup> Make the code more readable.
    - Factor out repeat code into helper functions
    - Access information in ways that are much more readable
        - Ex: before the decision to call v0.1 done here, there were 30+ calls to `board.get_square((x, y)).occupying_piece` that were all changed to `board.get_piece((x, y))`
- Add support for all missing features
- **Final step before calling the engine complete:**
    - Write a function that counts the number of possible board states after X moves.
    - Compare the data from this function with verified numbers, to ensure the chess engine is perfect.

