# day05 - Assignment

## wordle.py
Dependencies: 
- [`NLTK`](https://pypi.org/project/nltk/) (install using: `uv add nltk` or `pip install nltk`)

I wrote a Wordle-style guessing game. 
The game **randomly** selects a word, and you must guess it within a limited number of attempts. After each attempt, you receive feedback using *ASCII*-colored letters indicating how accurate your guess was.

You can change the word length or the number of attempts by modifying `word_length` and `attempts` in the code.  
The default settings are **6 attempts** to guess a **5-letter word**.

The **business logic** of the game is implemented in the `utilities` module through the following functions:

- `get_valid_words`: Loads English words from `nltk_data` and returns all words matching the chosen `word_length`.  
  If necessary, it downloads the required corpus using [`NLTK`](https://www.nltk.org/) and saves it in the assignment directory.

- `get_guess_colors`: Implements the core game logic. It compares your guess to the target word in two passes:  
  first counting direct hits and occurrences of remaining letters, and then marking non-direct hits.  
  The two-pass approach ensures letters are not counted more than once.

- `print_color`: Prints colored strings using *ASCII colors*.

Enjoy!