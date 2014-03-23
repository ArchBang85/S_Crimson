Shit_Crimson
============

2014 7DRL

Hello & thanks for stopping by. This is my dilettante's entry to the 2014 7DRL. 

Shit Crimson is my first Roguelike game and much remains to improve but it achieves a bit of the (dark) mood and vision I intended, plus it is completable and has a somewhat interesting spell system and not-quite-trivial combat so hopefully it'll spur a moment of pleasure or confusion. 

============

How to get it up and running:

20/3/2014 - You can get a compiled version from here: http://archbang.itch.io/shit-crimson I used cxFreeze instead of Pyinstaller and it seems to work fine now.

19/3/2014 - {I had some trouble compiling the thing with Pyinstaller, but it all seems to work fine if you download the files and run Shitcrimson.py in a Python 2.7 interpreter. I will get a working compiled version on as soon as I can} 

If you have issues feel free to email me at ArchBang85@gmail.com

============

Synopsis:

You, ostensibly a man in middle age, are dying a miserable death. Something eats away at your bowels. 
Your disease, or the medication you are taking for it, is bringing out the things you have locked away 
over the years. Mind and memory might be failing, but you feel compelled to try and make amends with your complicated past. Perhaps you can even hope to come to accept your traumas. You do not have much in this hostile house of yours, but you feel it might listen to you, it being the house or some more stable part of your mind. You can try to appeal to this
power by calling out the words it recognises, word you will need to discover or invent. Maybe confronting your 
apparitions will help. Dying well is not easy but you will try.

============

Instructions:

G to pick up items, I for inventory, C to try and create a word of power

Use the mouse to look at characters and objects and hopefully glean some atmosphere or even information.

Try and survive and make amends with what apparitions you find.

============

Comments:

Shit Crimson is far from a full-fledged and well-balanced RL but I'm happy to have attempted something ambitious for my abilities and gotten thus far. I picked up many basic RL things for the first time so the process was pretty exhilarating and taught me a bunch of new stuff.

Overall I was kind of aiming for something of a disturbing literary / aesthetic experience on top of a solidly working combinatorial spell system and thus felt compelled to add my non-artists artwork and non-musicians music in the mix.

The themes I wanted to deal with were heavy-ish: facing mortality, memory, the nature of repetition in games / RLs. A bit of inspiration was found from the likes of Borges, Dante, Philip K. Dick and Gene Wolfe. The whole shebang also links up to a fictional future-decayed universe I've been working on in general, so I've been pretty happy drip only fragments of information here and there.

A lot more in the way of written and pictorial content was imagined at the start, so that's something to keep on adding. I kind of imagined that playthroughs would be short, always ending in death, but gradually revealing more about the narrative as well as the mechanics as you play repeatedly. Plenty more basic RL things should be added too, such more items and more complication on the map, bosses, better character (de-)development, interactions.

More mechanics involving diminishment were also planned but not implemented. One I'd like to work on next is the combination of a failing memory and a sentient house displayed in part through a shifting fog of war representing the former and shifting areas under the fog for the latter. 

============

Spoilers:









Revealing the spell system's workings

Valid words are structured Consonant-Vowel-Vowel-Consonant
        
The Consonants set the level of power, i.e. the further the consonants are from each other, the more power the word has

The first Vowel sets the Form of the spell (Area, Line, Target, Self, Nearest, All)
      
The second Vowel sets the Content of the spell (Hurt, Heal, Open, Close, unimplemented:[Wisdom, Ignorance])

Further Spoiler (If You Are Stumped):

For instance B-A-A-M would create an Area spell [first A] with a DamAge effect [second A] and a power of M[letter index 13] - B[letter index 2] = 11

And N-I-O-T will create a line spell with a blOcking effect and a range determined by the distance between the consonants.

Good bye.
