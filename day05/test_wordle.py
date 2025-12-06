#!/usr/bin/env python

'''
pytest test suite for the exchange_rates function in utilities module.
The rates dictionary is hardcoded for testing purposes to allow consistent results.
'''

import pytest
from utilities import get_guess_colors

@pytest.mark.parametrize("word, guess, expected", [
    ("apple", "apric", ["green", "green", "grey", "grey", "grey"]),
    ("hello", "hullo", ["green", "grey", "green", "green", "green"]),
    ("world", "words", ["green", "green", "green", "yellow", "grey"]),
    ("python", "typhon", ["yellow", "green", "yellow", "green", "green", "green"]),
    ("banana", "bandan", ["green", "green", "green", "grey", "yellow", "yellow"]),
])
def test_parametrized(word, guess, expected):
    assert get_guess_colors(word, guess) == expected

if __name__ == "__main__":
    pytest.main([__file__, '-v'])
