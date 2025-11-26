#!/usr/bin/env python

import os
import nltk

def get_valid_words(word_length):
    nltk_data_dir = os.path.dirname(os.path.abspath(__file__)) + '/nltk_data'
    nltk.data.path.append(nltk_data_dir)

    try:
        from nltk.corpus import words
        english_words = words.words()
    except:
        print('Initializing NLTK data download. This may take a moment...\n')
        nltk.download('words', download_dir = nltk_data_dir, quiet = True)
        from nltk.corpus import words
        english_words = words.words()

    valid_words = [s.lower() for s in english_words if len(s) == word_length]

    return valid_words

def get_guess_colors(word, guess):
    colors = ['grey'] * len(word)
    appearances = {c : 0 for c in word}
    for i, (g, w) in enumerate(zip(guess, word)):
        if g == w:
            colors[i] = 'green'
        else:
            appearances[w] += 1

    for i, (g, w) in enumerate(zip(guess, word)):
        if g != w and g in appearances and appearances[g] > 0:
            colors[i] = 'yellow'
            appearances[g] -= 1

    return colors

def print_color(char, color):
    colors = {'green': '\033[92;1m',
              'yellow': '\033[93;1m',
              'grey': '\033[90;1m'}
    
    print(colors[color] + char.upper() + '\033[0m', end='')