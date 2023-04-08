#!/usr/bin/python3
from spellchecker import SpellChecker

spell_en = SpellChecker(language='en')
spell_fr = SpellChecker(language='fr')

def is_word(word):
    return word in spell_en or word in spell_fr

def get_xp_from_title(title):
    
    # Creation of a dictionary of words
    words = title.split(' ')
    
    # Creation of the point counter
    points = 0
    
    # Verbatim word analysis
    for word in words:
        
        # If the word exists in the dictionary
        if is_word(word):
            
            # He wins a point
            points += 1
            
        else:
            
            # He loses a point
            points -= 1

    # Returns points
    return points
  