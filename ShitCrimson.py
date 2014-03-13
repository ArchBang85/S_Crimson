__author__ = 'Autio'
################################################
# Shit Crimson - 7DRL 2014 - By ArchBang       #
# 9/3/2014 - 16/3/2014                         #
################################################
# Based on Roguebasin.com's roguelike tutorial #
#                                              #
#
#
#
#TODO labyrinth

###############################################################################
#                                                                INITIALISATION
import os
import libtcodpy as libtcod
import math
import textwrap
import Vallat


#size of window
SCREEN_WIDTH = 120
SCREEN_HEIGHT = 75

ROOM_MAX_SIZE = 14
ROOM_MIN_SIZE = 6
MAX_ROOMS = 35
MAX_ROOM_MONSTERS = 3
MAX_ROOM_ITEMS = 2

#size of map
MAP_WIDTH = 80
MAP_HEIGHT = 55

LIMIT_FPS = 20

#GUI Settings
BAR_WIDTH = 20
PANEL_HEIGHT = 14
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

# Default FOV algorithm
FOV_ALGO = 2
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10 #ever x turns diminish torch
TORCH_COUNTER = 0

# Inventory settings
INVENTORY_LIMIT = 26
INVENTORY_WIDTH = 50

# Item stats
HEAL_AMOUNT = 4 # how much a potion heals by
LIGHTNING_RANGE = 5
LIGHTNING_DAMAGE = 20

color_dark_wall = libtcod.Color(0, 0, 100) # darker purple
color_dark_ground = libtcod.Color(25, 50, 150) # darkish purple/blue
color_light_wall = libtcod.Color(50, 50, 150) # purplish
color_light_ground = libtcod.Color(100, 140, 170) # light blue

# counters

# jitters
#description move counter
dCount = 500
descriptionX = SCREEN_WIDTH - 40
descriptionY = 0


###############################################################################
#                                                                         WORDS

####################  Read in texts from the preset files  #####################

def readCSVtoArray(filePath):
    outputArray = []

    with open(filePath, 'rb') as source:
        for line in source:
            outputArray.append(line[:-2])
    return outputArray

toimiVallat = readCSVtoArray("sanat\\toimiVallat.csv")
ilkiVallat = readCSVtoArray("sanat\\ilkiVallat.csv")

ikkunat = readCSVtoArray("sanat\\ikkunat.csv")
ovet = readCSVtoArray("sanat\\ovet.csv")
esineet = readCSVtoArray("sanat\\esineet.csv")

print toimiVallat
print ilkiVallat
print ikkunat
print ovet
print esineet

###############################################################################
#                                                                       CLASSES

class Tile:
    #a tile on the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
        self.explored = False

        #If a tile is blocked, it also blocks sight by default
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

class Object:
    #this is a generic object
    #always represented by a character on the screen
    def __init__(self, x, y, char, name, color, blocks = False, fighter = None, ai = None, item = None):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks

        self.fighter = fighter
        if self.fighter: #tell the fighter component its ownner
            self.fighter.owner = self

        self.ai = ai
        if self.ai: #tell the AI component its owner
            self.ai.owner = self

        self.item = item
        if self.item: #tell the item component its owner
            self.item.owner = self

        self.description = setDescription()

    def move_towards(self, target_x, target_y):
        # get the distance and vector from self to target
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        #keep the movement steady in a grid by normalising, rounding and converting to int
        dx = int(round(dx/distance))
        dy = int(round(dy/distance))
        self.move(dx, dy)

    def move(self, dx, dy):
        #move by the given amount
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def distance_to(self, other):
        #return the distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def draw(self):
        #set the color and then draw the character that represents this object at its position
        # only draw if in fov
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

    def send_to_back(self):
        #push this to the top of the objects array so it gets drawn first,
        #i.e. before player and monsters - meant for corpses and items
        global objects
        objects.remove(self)
        objects.insert(0, self)



class Item:
    def __init__(self, use_function=None):
        self.use_function = use_function

    def pick_up(self):
        #add to the player's inventory and take away from the map
        if len(inventory) >= INVENTORY_LIMIT:
            message('Your inventory is full, cannot pick up ' + self.owner.name + '.', libtcod.red)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', libtcod.green)

    def use(self):
        #calls the object's 'use_function' if defined:
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')

        else:
            if self.use_function != 'cancelled':
                self.use_function()
                inventory.remove(self.owner) #destroy after usage

class Rect:
    #rectangle on the map
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def centre(self):
        centre_x = (self.x1 + self.x2)/2
        centre_y = (self.y1 + self.y2)/2
        return(centre_x, centre_y)

    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1)

class Fighter:
    #combat-related properties and methods (monster, player, NPC)
    def __init__(self, hp, defense, power, death_function = None):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.death_function = death_function

    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage

            if self.hp <= 0:
                function = self.death_function
                if function is not None:
                    function(self.owner)

    def attack(self, target):
        damage = self.power - target.fighter.defense
        if damage > 0:
            print self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' points.'
            target.fighter.take_damage(damage)
        else:
            print 'No damage'

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

def player_death(player):
    #game over
    global game_state
    print 'It is all over.'
    game_state = 'dead'

    player.char = '%'
    player.color = libtcod.dark_red

def monster_death(monster):
    #transform monster to a corpse
    print monster.name.capitalize() + ' has died!'
    monster.send_to_back() #draw this object first
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name

class BasicMonster:
    #AI for the basic monster type
    def take_turn(self):
        print 'The ' + self.owner.name + ' growls'

        #If you can see the basic monster, so can they see you
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):

            #Move towards player if far away (if feeling up to the task?)
            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)

            #Attack when close by
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)
                #print 'The attack of the ' + monster.name + ' does you no harm!'

###############################################################################
#                                                                     FUNCTIONS

def setDescription():
    # Build how descriptions are set for objects here
    roll = libtcod.random_get_int(0, 0, len(esineet)-1)
    return esineet[roll]

### WORLD GENERATION ##########################################################
def create_room(room):
    global map
    #go through tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False

def create_h_tunnel(x1, x2, y):
    global map
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
    global map
    for y in range(min(y1, y2), max(y1, y2)+ 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def create_monster(x, y):
    roll = libtcod.random_get_int(0, 0, 100)
    if roll < 70: # chance of getting a smell
        fighter_component = Fighter(hp = 10, defense=0, power=3, death_function=monster_death)
        ai_component = BasicMonster()
        monster = Object(x, y, 's', 'Smell', libtcod.red, blocks = True, fighter=fighter_component, ai = ai_component)

    elif roll < 70 + 20:
        fighter_component = Fighter(hp = 15, defense=1, power=5, death_function=monster_death)
        ai_component = BasicMonster()
        monster = Object(x, y, 'p', 'Pain', libtcod.orange, blocks=True, fighter = fighter_component, ai = ai_component)

    else:
        # memory
        fighter_component = Fighter(hp = 20, defense=2, power=5, death_function = monster_death)
        ai_component = BasicMonster()
        monster = Object(x, y, 'M', 'Memory', libtcod.dark_pink, blocks = True, fighter=fighter_component,ai = ai_component)

    objects.append(monster)

def create_item(x, y):

    roll = libtcod.random_get_int(0, 0, 100)

    if roll < 20:
        item_component = Item(use_function=cast_heal)
        item = Object(x, y, '!', 'healing potion', libtcod.violet, item = item_component)
    elif roll < 40:
        item_component = Item(use_function=cast_heal)
        item = Object(x, y, 'i', 'happy potion', libtcod.lightest_sepia, item = item_component)
    else:
        item_component = Item(use_function=cast_heal)
        item = Object(x, y, 'z', 'scroll of lightning thwack', libtcod.lighter_yellow, item = item_component)
    objects.append(item)
    item.send_to_back()

def place_objects(room):
    #choose random number of monsters
    num_monsters = libtcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)
    num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)

    for i in range(num_monsters):
        #choose random spot for this monster
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        if not is_blocked(x, y):
            create_monster(x, y)

    for i in range(num_items):
        #random spot for item
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        create_item(x, y)

def is_blocked(x, y):
    # test the map tile
    if map[x][y].blocked:
        return True

    # now check for blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True
    return False

def make_map():
    global map

    rooms = []
    num_rooms = 0

    #fill map with "blocked" tiles
    map = [[ Tile(True)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]

    for r in range(MAX_ROOMS):
        #random width and height
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random position without going outside the map
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

        new_room = Rect(x, y, w, h)

        #run through the rooms and check for intersections
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
        #room has no intersections
            create_room(new_room)
            place_objects(new_room)

            #centre coordinates of the new room
            (new_x, new_y) = new_room.centre()

            if num_rooms == 0:
                player.x = new_x
                player.y = new_y
            else:
                #all rooms after the first:
                #connect to the previous room with a tunnel

                #centre coordinates of the previous room
                (prev_x, prev_y) = rooms[num_rooms - 1].centre()

                #draw a coin (0 or 1)
                if libtcod.random_get_int(0, 0, 1) == 1:
                    #first move horizontally, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    #first vertically, then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)
            #finally, append the new room to the list
            rooms.append(new_room)
            num_rooms += 1
###############################################################################

### MAP DRAWING ###############################################################
def render_all():
    global fov_map, color_dark_wall, color_light_wall
    global color_light_groundm, color_dark_ground
    global fov_recompute
    global dCount, descriptionX, descriptionY

    if fov_recompute:
        #recompute FOV if needed
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        #cycle through tiles and set their bg colour
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = map[x][y].block_sight
                if not visible:
                    if map[x][y].explored:
                        if wall:
                            libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
                else:
                    #it is visible
                    if wall:
                        libtcod.console_set_char_background(con, x, y, color_light_wall)
                    else:
                        libtcod.console_set_char_background(con, x, y, color_light_ground)
                    # because it is visible, explore it
                    map[x][y].explored = True

    #draw all objects in the list
    for object in objects:
        #Exclude the player so she can be drawn last
        if object != player:
            object.draw()
        player.draw()

    #blit con to the root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    #prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    #show the player's stats
    render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp, libtcod.light_red, libtcod.darker_red)

    #print the game messages
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1

    #display names of objects under the mouse
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())

    # Randomise the description display point slightly
    dCount -= 1
    if dCount < 0:
        descriptionX = SCREEN_WIDTH - 42 + libtcod.random_get_int(0, 0, 3)
        descriptionY = libtcod.random_get_int(0, 0, 3)
        dCount = libtcod.random_get_int(0, 490, 510)

    #print the description lines
    y = 1
    for line in get_description_under_mouse():
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, descriptionX, descriptionY + y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1



    #blit the panel to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)
###############################################################################

def torch_dimmer():
    global TORCH_COUNTER
    global TORCH_RADIUS

    TORCH_COUNTER += 1

    if TORCH_COUNTER % 30 == 0:
        TORCH_RADIUS -= 1

def player_move_or_attack(dx, dy):
    global fov_recompute

    #where is the player moving to or attacking
    x = player.x + dx
    y = player.y + dy

    #see if there's anything to attack
    target = None
    for object in objects:
        if object.fighter and object.x == x and object.y == y:
            target = object
            break
    #attack if target found, move otherwise
    if target is not None:
        player.fighter.attack(target)
        # print 'The ' + target.name + ' evades your ire.'
    else:
        player.move(dx, dy)
        fov_recompute = True

### CONTROLS ##################################################################

def handle_keys():
    global key
    global fov_recompute
    #key = libtcod.console_check_for_keypress()  #real-time

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt + Enter toggles fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit' #exit game

    if game_state == 'playing':

        #movement keys
        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
            player_move_or_attack(0, -1)
        elif key.vk == libtcod.KEY_DOWN  or key.vk == libtcod.KEY_KP2:
            player_move_or_attack(0, 1)
        elif key.vk == libtcod.KEY_LEFT  or key.vk == libtcod.KEY_KP4:
            player_move_or_attack(-1, 0)
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
            player_move_or_attack(1, 0)
        #diagonals
        elif key.vk == libtcod.KEY_KP9:
            player_move_or_attack(1, -1)
        elif key.vk == libtcod.KEY_KP3:
            player_move_or_attack(1, 1)
        elif key.vk == libtcod.KEY_KP7:
            player_move_or_attack(-1, -1)
        elif key.vk == libtcod.KEY_KP1:
            player_move_or_attack(-1, 1)
        else:
            #check for other keys
            key_char = chr(key.c)

            if key_char == 'g':
                #pick item up
                for object in objects:
                    if object.x == player.x and object.y == player.y and object.item:
                        object.item.pick_up()
                        break

            if key_char == 'i':
                #display inventory
                active_item = inventory_menu('Press the relevant letter to use the item, anything else to cancel.\n')
                if active_item is not None:
                    active_item.use()
                    message('Used item.', libtcod.blue)

            return 'no-turn-taken'

        #

### ITEM FUNCTIONS ############################################################

def cast_heal():
    #unit healing
    if player.fighter.hp == player.fighter.max_hp:
        message('You have no wounds to heal.', libtcod.red)
        return 'cancelled'

    message('You feel better.', libtcod.light_cyan)
    player.fighter.heal(HEAL_AMOUNT)

def cast_lightning():
    # find the closest enemy within a maximum range and damage it
    monster = closest_monster(LIGHTNING_RANGE) # closest_monster still needs to be defined
    if monster is None: # No enemy within maximum range
        message('No enemy is close enough for the lightning to strike.', libtcod.dark_red)
        return 'cancelled'

    # thwack!
    message('A lightning bolt strikes the ' + monster.name + ' with a loud thunder causing ' + str(LIGHTNING_DAMAGE) + ' points of damage.', libtcod.blue)
    monster.fighter.take_damage(LIGHTNING_DAMAGE)

### GUI FUNCTIONS ###

def message(new_msg, color = libtcod.white):
    #split message if needed
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        #when the buffer is full, pop out the top line
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        #add the new line as a tuple
        game_msgs.append( (line, color) )

def get_names_under_mouse():
    global mouse
    #return a string with all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)

    #make a list with names of all legit objects
    names = [obj.name for obj in objects
        if obj.x ==x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]

    #join names with a comma
    names = ', '.join(names)
    return names.capitalize()

def get_description_under_mouse():
    global mouse
    #return a string with all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)

    #make a list with descriptions of all legit objects
    descriptions = [obj.description for obj in objects
        if obj.x ==x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]

    # descriptions need to break lines after each 28 characters
    n = 36

    #textwrap.wrap(
    #join names with a comma
    descriptions = ', '.join(descriptions)
    d = str(descriptions)
    return textwrap.wrap(d, n)

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    #render a GUI bar
    #calculate bar width
    bar_width = int(float(value) / maximum * total_width)

    #render background
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    #then render the actual bar
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    #display text with values
        libtcod.console_set_default_foreground(panel, libtcod.pink)
        libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
        name + ': ' + str(value) + '/' + str(maximum))

def menu(header, options, width):
    img = libtcod.image_load('bff1.png')
    libtcod.image_blit_2x(img, 0, 0, 0)
    message("blitted image", libtcod.gray)

    if len(options) > INVENTORY_LIMIT: raise ValueError('Cannot have a menu with more than ' + str(INVENTORY_LIMIT) + ' options.')

    #Work out height of header after the automatic wrapping and give one line per menu option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    height = len(options) + header_height

    #create an off-screen console for the menu's window
    menu_window = libtcod.console_new(width, height)

    #print header
    libtcod.console_set_default_foreground(menu_window, libtcod.light_gray)
    libtcod.console_print_rect_ex(menu_window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    #print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(menu_window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    #blit to the root console
    x = 3# SCREEN_WIDTH/2 - 35
    y = SCREEN_HEIGHT/2 - 35# - height
    libtcod.console_blit(menu_window, 0, 0, width, height, 0, x, y, 1.0, 0.7) # last two params define transparency

    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    #converting ASCII to an index
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None

def inventory_menu(header):
    #show a menu with the inventory items as options
    if len(inventory) == 0:
        options = ['You are not carrying anything.']
    else:
        options = [item.name for item in inventory]

    index = menu(header, options, INVENTORY_WIDTH)
    if index is None or len(inventory) == 0: return None
    return inventory[index].item

###############################################################################
#                                                                     MAIN LOOP

libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
libtcod.sys_set_fps(LIMIT_FPS)

### GUI ###
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

#list of game messages with their colors
game_msgs = []

#create player object
fighter_component = Fighter(hp = 30, defense = 2, power = 5, death_function = player_death)
player = Object(0, 0, '@', 'player', libtcod.white, blocks = True, fighter = fighter_component)

#list of objects, starting with player
objects = [player]
inventory = []

#generate map(not yet drawn)
make_map()

#create the FOV map based on the map just generated
fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

#Game States
fov_recompute = True
game_state = 'playing'
player_action = None

### MOUSE FUNCTIONALITY ###
mouse = libtcod.Mouse()
key = libtcod.Key()

### LOOP ###
message("Shit Crimson", libtcod.gray)
libtcod.sys_set_fps(LIMIT_FPS)
while not libtcod.console_is_window_closed():

    #check for mouse
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
    render_all()

    libtcod.console_flush()

    #erase all objects at their old locations, before they move
    for object in objects:
        object.clear()

    #handle keys and exit game if needed
    player_action = handle_keys()
    if player_action == 'exit':
        break

    #monsters do their stuff
    if game_state == 'playing' and player_action != 'no-turn-taken':
        for object in objects:
            if object.ai:
                object.ai.take_turn()

        # increment fov_range ticker
        torch_dimmer()


