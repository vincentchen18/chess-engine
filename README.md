## Vinniebot Chess Engine

My Chess Engine is a project where you can play a game of chess against another person, or my amateur chess engine Vinniebot, or watch it play itself!

My bot is built with a minimax algorithm using alpha-beta search for speed optimisation, with piece-square tables and material counting to evaluate positions, allowing it to calculate up to 3 moves ahead in a reasonable timeframe.

I also finally learned pygame GUI so yeah you don't have to play in the terminal anymore! Have fun :)))

![Chess image](readme%20image.png)

me getting destroyed by my bot.

## Usage instructions

### Windows:

Download the exe from https://github.com/vincentchen18/chess-engine/releases/tag/v1 and run it to start playing!

### Mac:

I don't have a Mac to compile with PyInstaller, so just clone the repository and run the project with the following commands:

`git clone https://github.com/vincentchen18/chess-engine/`

`pip install pygame` to install dependency

`python3 chess.py`

### Linux:

I actually published this game to the snap store, so you can just open terminal and run this command:

`sudo snap install vinniebot-chess`

or from this link here: https://snapcraft.io/vinniebot-chess

Alternatively, download the linux binary from https://github.com/vincentchen18/chess-engine/releases/tag/v1 and run it with ./VinniebotChessLinux to play! :)

### Controls:

To move the pieces, it's just drag and drop, but it won't let you move if you try to make an illegal move. If you're moving a piece, right click to put the piece back where it was, and you can use the keys f or x to flip the board.

### AI Disclaimer:

AI was used throughout the project for assistance in asset crediting, fixing file packaging problems (for )

## Asset Credits

Chess piece images by Colin M.L. Burnett, licensed under GPL/CC-BY-SA. Sourced via [Lichess](https://lichess.org).

Crown icon by feen from Flaticon

½ icon by Freepik from Flaticon  

Hashtag icon by Freepik from Flaticon