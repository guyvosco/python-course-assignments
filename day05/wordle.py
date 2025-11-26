#!/usr/bin/env python

import random
from utilities import get_valid_words, get_guess_colors, print_color

def main():
    word_length = 5
    attempts = 6

    print('\033[1;4mLet\'s play Wordle!\033[0m\n\n' + \
          'You have %i attempts to guess a %i-letter word.\n' % (attempts, word_length) + \
          'Each guess must be a valid %i-letter word.\n' % word_length + \
          'The color of the letters will change to show how close your guess was to the word.\n' + \
          '\033[92mGreen\033[0m means the letter is in the word and in the correct spot.\n' + \
          '\033[93mYellow\033[0m means the letter is in the word but in the wrong spot.\n' + \
          '\033[90mGrey\033[0m means the letter is not in the word in any spot.\n')
    
    valid_words = get_valid_words(word_length)

    word = random.choice(valid_words)

    for attempt in range(attempts):
        guess = input('Enter a %i-letter word: ' % word_length).lower()
        valid = guess in valid_words and len(guess) == word_length
        while not valid:
            guess = input('Invalid word. Please enter a valid %i-letter word: ' % word_length).lower()
            valid = guess in valid_words and len(guess) == word_length
        
        guess_colors = get_guess_colors(word, guess)
        
        print('\033[4mAttempt %i:\033[0m ' % (attempt + 1), end = '')
        for char, color in zip(guess, guess_colors):
            print_color(char, color)
        print('\n')
        
        if guess == word:
            print('\033[1;4mCongratulations!\033[0m You\'ve guessed the word.\n')
            break
        if attempt == attempts - 1:
            print('\033[1;4mGame Over\033[0m\n' + \
            'You\'ve used all attempts. The word was "%s".' % word)

if __name__ == '__main__':
    try:
        main()
    except ValueError as e:
        print(e)
