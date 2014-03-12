__author__ = 'Autio'

### A stab at a spell system ###

# The idea is that you need at least 3 letters to form a workable spell
# one vowel must be included, this designates something about the spell
# perhaps its type (create rock, summon ally, etc)
# or its form (line, area, self, spot, nearest, everywhere)

# a, e, i, o, u, y

# The player starts with a full alphabet but each consonant, once used, is gone forever


# read in the allowed combinations here


# try if a spell is legitimate and return its effects

# (look at how items / spells are built anyway modularly to figure out the best way)
# should be shape 'consonant/vowel/consonant' but can chain them?
# 'rixbetfyz'

# runes the player can choose from
alphabetString = 'abcdefghijklmnopqrstuvwxyz'
alphabet = []
for l in alphabetString: alphabet.append(l)

vowels = "aeiouyAEIOUY"
consonants = "bcdfghjklmnpqrstvwxzBCDFGHJKLMNPQRSTVWXZ"

# Read in the runebook
def readSpellsToDict(filePath):
    outputDict = {}

    with open(filePath, 'rb') as source:
        for line in source:
            sides = line.split(',')

            outputDict[sides[0]] = sides[1][:-2]
    return outputDict

valtaKirja = readSpellsToDict("vallat\\valtakirja.csv")
print valtaKirja
spell = alphabet[1] + alphabet[0] + alphabet[2]

def mapSpells():
    consonantMap =  {'1' : "dark", '2' : "light", '3' : "ice", '4' : "fire", '5' : "air", '6' : "rock"}

    print consonantMap

mapSpells()

def castRune(runes):

    vowelCount = 0
    consonantCount = 0
    for letter in runes:
        if letter in vowels:
            vowelCount += 1
        elif letter in consonants:
            consonantCount += 1

    if vowelCount == 0:
         # Error - power takes no form
        return "noVowel"

    if consonantCount < 2:
        # Error - power has no substance
        return "noConsonants"

    # find all consonant-vowel-consonant combinations
    combinations = []
    l = 0
    while l < len(runes)-2:
        if runes[l] in consonants and runes[l+1] in vowels and runes[l+2] in consonants:
            combinations.append(runes[l]+runes[l+1] + runes[l+2])
        l += 1

    return "success"

def removeLetters(spell):
    # prune the used up consonants from the alphabet
    for l in spell:
        if l not in vowels:
            i = 0
            while i < len(alphabet):
                if l == alphabet[i]:
                    alphabet[i] = ""
                i += 1

# no errors in casting
if castRune(spell) == "success":
    #print 'removing letters'
    removeLetters(spell)

