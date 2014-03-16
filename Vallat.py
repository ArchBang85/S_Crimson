__author__ = 'ArchBang'
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


# 13/03/2014 reworking
# following on from conversing with Darren I think it's best to take his idea that
# the distance between two consonants establishes the strength

# further to that the polarity establishes something further

# retain the vowel in the middle, actually have two
# one sets the form
# one sets the content

#e.g. 'BAUM' -> medium strong enemy targeting damage spell
#     'VIIT' -> weak etc

# What do the vowels stand for?

# consonant, form, content, consonant

# Forms:
# a     = area
# e     = line
# i     = self
# o     = adjacent
# u     = another
# y     = nearest

# Contents:
# a     = access / blocking
# e     =
# i     =
# o     = healing / damage
# u     =
# y     = knowledge / confusion


# How should the spellcasting be structured?
# 1. see if it's a valid spell, respond appropriately if not
#       2. establish the form, content and power of the spell
#           3. remove the used consonants from the alphabet
#               4. play out the effects of the successfully cast spell

# runes the player can choose from
alphabetString = 'abcdefghijklmnopqrstuvwxyz'
alphabet = []
for l in alphabetString: alphabet.append(l)

vowels = "aeiouyAEIOUY"
consonants = "bcdfghjklmnpqrstvwxzBCDFGHJKLMNPQRSTVWXZ"

runeForms =     \
                {
                    'a' : 1,
                    'e' : 2,
                    'i' : 3,
                    'o' : 4,
                    'u' : 5,
                    'y' : 6
                }

runeContents =  \
                {
                    'a' : 1,
                    'e' : 2,
                    'i' : 3,
                    'o' : 4,
                    'u' : 5,
                    'y' : 6
                }

def spellPower(runes):
    # looks at the positions of the consonants in the alphabet
    # and returns the difference, positive or negative
    i = 0
    a = 0
    b = 0
    while i < len(alphabet):
        if runes[0] == alphabet[i]:
            a = i
        if runes[3] == alphabet[i]:
            b = i
        i += 1
    return (b-a)

def checkRunes(runes):
    # valid form [consonant, vowel, vowel, consonant]
    print runes
    if len(runes) <> 4:
        return "noForm"
    elif runes[1] not in vowels:
        # Error - spell has takes no form
        return "noForm"

    elif runes[2] not in vowels:
        # Error - spell has no content
        print runes[2]
        return "noContent"

    if runes[0] and runes[3] not in consonants or runes[0] == runes[3]:
        # Error - spell has no power
        return "noPower"

    if runes[0] not in alphabet or runes[3] not in alphabet:
        # runes forgotten
        return "forgotten"

    return "success"

def removeLetters(spell):
    # prune the used up consonants from the alphabet
    for l in spell:
        if l not in vowels:
            i = 0
            while i < len(alphabet):
                if l == alphabet[i]:
                    alphabet[i] = " "
                i += 1

def castRunes(runes):
    runeResponse = checkRunes(runes)

    if runeResponse == "success":
        power = spellPower(runes)
        form = runeForms[runes[1]]
        content = runeContents[runes[2]]
        removeLetters(runes)
        return power, form, content, 0

    elif runeResponse == "noForm":
        # display message of formless magic
        return 0, 0, 0, 1

    elif runeResponse == "noContent":
        # display message of contentless magic
        return 0, 0, 0, 2

    elif runeResponse == "noPower":
        # display message of powerless magic
        return 0, 0, 0, 3

    else: return 0, 0, 0, 1

# Read in the runebook | redundant
def readSpellsToDict(filePath):
    # Read a 2-column CSV file into a dictionary
    outputDict = {}

    with open(filePath, 'rb') as source:
        for line in source:
            sides = line.split(',')

            outputDict[sides[0]] = sides[1][:-2]
    return outputDict

#Line shaped spells
