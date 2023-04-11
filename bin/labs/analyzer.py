#!/usr/bin/python3
from spellchecker import SpellChecker
import textstat

spell_en = SpellChecker(language='en')


def is_word(word):
    if word.isalpha() is False:
        return False
    return word in spell_en


blacklist = ['task', 'tasks', 'point', 'points', 'hugo']
def get_xp_from_title(title):
    
    # Creation of a dictionary of words
    words = title.split(' ')
    
    # Creation of the point counter
    points = 0
    
    if len(words) < 2:
        points -= 2
    
    repeat = []
    
    # Verbatim word analysis
    for word in words:
        
        word = word.lower()
        
        
        if word in blacklist or word in repeat:
            
            points -= 3
            
        elif is_word(word):
            
            # He wins a point
            if len(word) > 2:
                
                points += 1
            
            
        else:
            
            # He loses a point
            if len(word) > 10:
                
                points -= len(word) / 10
                
            else:
            
                points -= 1
                
        repeat.append(word)


    # Returns points
    return points * 10
  