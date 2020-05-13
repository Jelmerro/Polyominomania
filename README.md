# Polyominomania

A simple Tetris clone with a frightening amount of customization options.

Ever wondered what it would be like if the scoring system was totally different?
Always wanted to have a different grid size?
Ever wanted to find out what it would be like if you could use larger or smaller polyomino sets?
Always wanted to modify the level system?
Trying to play with a different number of next pieces shown?
Or simply in search of a free and open source version?
Meet Polyominomania, the answer to all the questions above.
A Tetris clone made in Python 3 with pyglet.

# License

I think it's necessary to make it very clear that this isn't an official Tetris,
but a fan-made variation of the game which allows the user to customize core features.
Polyominomania doesn't share any assets (be it art or music) with any Tetris game,
as there is no music and the art consists of simple squares only.
Aside from that, Polyominomania has a completely different way to play the game,
by allowing the user to come up with new ways to play.
Polyominomania itself is released into the public domain, you can check the UNLICENSE for details.
Please check the [pyglet library](https://github.com/pyglet/pyglet) and [Fixedsys Excelsior font](https://github.com/kika/fixedsys) as well!

# Features

- Play with a custom set of polyominoes (ranging from the monomino all the way up to 30-ominoes)
- Combine multiple sets with customizable color scheme
- Modify the scoring system per level
- Increase or decrease the amount of lines needed per level
- Modify the randomization of the next piece (can be picked from a bag, generated when it's needed or system random)
- Start at a custom speed and increase it per level with a custom amount
- Set the size of the level grid to any size (minimum being the size of the largest set of polyominoes)
- Full keyboard input, no mouse required (Keyboard inputs are explained further below)
- Play with or without ghost pieces visible
- Show a custom amount of next pieces (0-4)
- Customize all that and more using simple JSON (Config files are explained further below)
- Highscores are saved separately for each config

# Keyboard

The entire game works using a keyboard.
Most of the actions are configured at two keys,
to give the user a bit more options without the need for full key customization.
The ones that are the same through the entire game are:

- F11 - Toggle fullscreen. This will scale the game to a maximum, but it won't stretch it.

Key | Key | Menu | Highscores | Game
--- | --- | --- | --- | ---
Arrow up | W | Move up | Scroll up in the list of characters (Hold to repeat) | Rotate clockwise
Arrow down | S | Move down | Scroll down in the list of characters (Hold to repeat) | Softdrop (Hold to repeat)
Arrow left | A | - | Move to the previous character | Move the piece left (Hold to repeat)
Arrow right | D | - | Move to the next character | Move the piece right (Hold to repeat)
Right ctrl | E | - | - | Rotate counter-clockwise
Enter | Space | Select mode | Go to OK, and go to menu from OK | Harddrop
Backspace | Esc | - | - | Toggle pause

If you want to use a joystick or gamepad, simply map the desired buttons to the ones above.

# Config

All the modifications and settings are saved in a config JSON file.
For each different way to play, a separate file is saved in the "modes" folder.
You can create your own by copying any of the existing modes.
A fair amount of example configurations can be found in the modes folder.
Most configurations fields are explained below and will result in a different highscore table being used.

## Basic fields

- description (str) - The explanation text that will be shown in the game. (This is only to explain the config to the user and will not cause a different highscore list to be used)
- lines_per_level (int) - The amount of lines needed to progress to the next level.
- first_level (int) - The level at which the game starts.
- speed (int) - The initial speed of the game (calculation: 10 / speed = time in seconds per line).
- speed_per_level (int) - The amount of speed by which the game increases when the player reaches the next level.
- width (int) - The width of the level in blocks.
- height (int) - The height of the level in blocks.
- next_pieces (int) - The amount of next pieces shown as a preview on the right (maximum of 4, set to 0 to display none).
- ghost (bool) - Enable this, to show a ghost of where the current piece will land.
- extra_spacing (bool) - Enable this to increase the space between the squares (This is only cosmetic and will not cause a different highscore list to be used)

Aside from these bools and ints, two dictionaries named "polyominoes" and "scoring" should be added.
These will be explained in detail in the next two paragraphs.

## Polyominoes

In the root of the config a dictionary field of polyominoes should be present.
In this dictionary, the keys determine the size of the polyomino.
This value should be at least 0 and at most 30.
In there, the following fields should be configured:

- next_piece (str) - Configure the randomization type to use for this set of polyominoes.
  Choose between: "jit", "random" or "bag".  
  jit - A new piece will be generated when it is needed in the game. This option is especially useful for large sets, as it's the only type of randomization which does not need to generate all the pieces before the game starts.  
  random - Generates a list of all pieces and picks a random one out of the list each time a new piece is needed.  
  bag - The bag randomization will start with a list of all generated pieces, but will remove the piece from the list if it is picked. When the list is empty, the list with all possibilities is restored. This means you will get all pieces at least once, before the getting the same piece again. The order by which the individual pieces are picked from the list is still random. (As the name suggests, it's as if you are blind picking a piece from a bag, where the bag is refilled once it's empty)
- colors (str) - Choose a colors scheme for this set of polyominoes.
  Currently the following schemes are supported: "original", "retro", "bootstrap", "gray".
  If you know a bit of Python, it should be easy enough to add some more.
  If the polyomino set is a set of tetrominoes (4), the pieces will get the same color each time.
  For all other sizes a random color is picked each time.
  This is only cosmetic and will not cause a different highscore list to be used
- chance (int) - Configure the chance between different sets.
  This can be represented as any value above 0.
  Items with a chance higher than 1, are simply added more than once to the list of possible sizes.
  For example, if we have hexominoes with a chance of 2 and tetrominoes with a change of 1,
  the list of possible sizes for the next piece will look like this: [6, 6, 3].
  From this list a random size is picked for each new piece.

## Scoring

In the root of the config a scoring dictionary should be present.
In this dictionary all fields are int's and can be 0.

- polyomino - The amount of points the player receives when a piece is placed.
- softdrop - The amount of points the player receives for soft-dropping a piece.
  The amount of points is awarded per block, so if the player soft-drops for 5 blocks with a softdrop setting of 1, the player will receive 5 points.
- harddrop - The amount of points the player receives for soft-dropping a piece.
  The amount of points is awarded per block, so if the player hard-drops for 5 blocks with a harddrop setting of 2, the player will receive 10 points.

Aside from that, two dictionaries of scores are also found here.
Both of them should contain a key for each number of lines the player could possibly clear with one piece.
For example, if the largest set of polyominoes is 6, we should define a score for clearing up to 6 lines.
There are two dictionaries, to allow the user to increase the score per line per level.
This works the same way as the speed and speed_per_level.

Hopefully this has answered all the questions about the config file,
if there is anything you are unsure of just try it.
The game should detect invalid configs and tell you what is wrong.
