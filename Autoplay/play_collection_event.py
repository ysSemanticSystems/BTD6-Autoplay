#!/usr/bin/python3
#
# Desc: Cycles menus, finds the bonus-reward expert map, and plays it.
# Expert grid updated for the 14-map layout as of September 2026.
#

from __future__ import annotations

import sys
import time
from pathlib import Path

from PIL import ImageGrab

AUTOPLAY_DIR = Path(__file__).resolve().parent
if str(AUTOPLAY_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOPLAY_DIR))

import autoplayV2
from config import REFERENCE_DIR, USE_LMSTUDIO_VISION
from input_backend import click as click_logical, click_design
from lmstudio_client import classify_ui, is_available as lmstudio_available

print('-----------')

current_map = ''
bonus_rewards_image = str(REFERENCE_DIR / 'oct_bonus_rewards.png')
collection_event_image = str(REFERENCE_DIR / 'oct_collection_event.png')

# 2026 expert pages are 2 rows x 3 cols. Scripts exist only for the original 10.
# Maps without a script are skipped so the bot does not start an unwinnable game.
EXPERT_PAGES = [
    [
        ['tricky_tracks_script', 'glacial_trail_script', 'dark_dungeons_script'],
        ['sanctuary_script', 'ravine_script', 'flooded_valley_script'],
    ],
    [
        ['infernal_script', 'bloody_puddles_script', 'workshop_script'],
        ['quad_script', 'dark_castle_script', 'muddy_puddles_script'],
    ],
    [
        ['ouch_script', 'blons_script', None],
        [None, None, None],
    ],
]
SCRIPTED_MAPS = {
    'sanctuary_script',
    'ravine_script',
    'flooded_valley_script',
    'infernal_script',
    'bloody_puddles_script',
    'workshop_script',
    'quad_script',
    'dark_castle_script',
    'muddy_puddles_script',
    'ouch_script',
}
FALLBACK_MAP = 'dark_castle_script'

def find_image(given_image: str):
    '''
    See if bonus rewards symbol is on the screen.
    :returns: True if symbol found, false otherwise.
              Logical location of best match.
    '''
    found, location, score = autoplayV2.find_image_location(given_image)
    if found:
        print('Found it')
        return True, location
    return False, location


def find_bonus_rewards_symbol():   
    '''
    Finds the map that contains the bonus reward and starts up a game in that map.
    
    :returns: action script of map selected
              if the bonus rewards symbol was found (bool)
    '''
    global bonus_rewards_image
    page_num = 1 # there are two expert map selection pages

    # Click so that we consistently see the left expert maps screen
    click_play()
    time.sleep(.7)  
    click_beginner() 
    time.sleep(.3)
    click_expert()
    time.sleep(1)

    for page_num in range(1, len(EXPERT_PAGES) + 1):
        found_symbol, location = find_image(bonus_rewards_image)
        if found_symbol:
            expert_map = get_expert_map(location, page_num)
            if expert_map is None:
                print('Bonus map has no script; falling back to Dark Castle')
                return load_named_map(FALLBACK_MAP), True
            click(location)
            time.sleep(.7)
            click_hard()
            time.sleep(.7)
            click_standard()
            return expert_map, True
        if page_num < len(EXPERT_PAGES):
            click_page_right()
            time.sleep(1)

    if USE_LMSTUDIO_VISION and lmstudio_available():
        state = classify_ui(ImageGrab.grab())
        print(f'LM Studio UI state: {state}')
        if state.get('bonus_rewards') or str(state.get('screen', '')).lower() == 'map_select':
            print('Template miss; using Dark Castle so farming still continues')
            return load_named_map(FALLBACK_MAP), True

    print('Reward symbol not found')
    return 'None', False


def load_named_map(script_name: str):
    """Open Hard Standard on Dark Castle when the bonus map has no script."""
    click_beginner()
    time.sleep(.3)
    click_expert()
    time.sleep(1)
    click_page_right()
    time.sleep(.8)
    # Dark Castle is page 2, bottom-middle on the 2026 grid.
    click_design((960, 720))
    time.sleep(.7)
    click_hard()
    time.sleep(.7)
    click_standard()
    return get_script(script_name)


def get_script(script_name: str):
    global current_map
    current_map = script_name
    autoplayV2.map_is_sanctuary = script_name == 'sanctuary_script'
    autoplayV2.manual_rounds = script_name == 'sanctuary_script'
    module = __import__('action_scripts.collection_scripts.' + script_name, fromlist=[script_name])
    return getattr(module, script_name)


def get_expert_map(position, page_num):
    '''
    Get the expert map from the position of the bonus rewards symbol.

    :returns: list of actions, or None if that map has no script
    '''
    height = autoplayV2.screen_height
    width = autoplayV2.screen_width

    yindex = 0 if position[1] < height / 3 else 1
    if position[0] < width / 2.5:
        xindex = 0
    elif width / 2.5 <= position[0] <= width - width / 2.5:
        xindex = 1
    else:
        xindex = 2

    try:
        expert_map = EXPERT_PAGES[page_num - 1][yindex][xindex]
    except (IndexError, TypeError):
        print(f'Could not resolve expert map page={page_num} pos={position}')
        return None

    print(expert_map)
    if expert_map is None or expert_map not in SCRIPTED_MAPS:
        return None
    return get_script(expert_map)


# region ------------- Clicking-Only Methods -----------------
def click(position):
    '''Click a logical-screen position (already scaled, e.g. from template match).'''
    click_logical(position)

def click_play():
    click_design((835, 930))

def click_beginner():
    click_design((582, 981))

def click_expert():
    click_design((1338, 976))

def click_page_right():
    click_design((1642, 432))

def click_hard():
    click_design((1296, 418))

def click_standard():
    click_design((632, 587))

def click_home():
    click_design((702, 859))

def click_home_loss():
    click_design((575, 823))

def click_victory_next():
    click_design((939, 907))

def collect_event():
    '''Collect event rewards after beating a level'''
    click_design((962, 683))
    time.sleep(3)
    for i in range(30):
        click_design((553 + i * 30, 544))
        time.sleep(.1)
    click_design((81, 55))

# endregion


def main():

    num_games = 35
    beat_level = False
    broken_log = []
    start_collection = time.time()

    for i in range(num_games):
        # Launch the game with the bonus rewards symbol
        expert_map, found = find_bonus_rewards_symbol()
        if found:
            # Beat the level
            beat_level = autoplayV2.game_loop(expert_map)
        else:
            print('Reward symbol not found, exitting program')
            exit()
        # log if we somehow didn't beat the level
        if beat_level == False:
            print('didnt beat level')
            broken_log.append(current_map)
            # Exit to main menu by pressing home button
            click_home_loss()
            time.sleep(.1)
            click_home() # shouldn't be needed, but it's there just in case
        else:
            # Exit to home after victory
            click_victory_next()
            time.sleep(1.5)
            click_home()
            time.sleep(1.5)
            
        time.sleep(7)
        # Collect event rewards if needed
        found_collection, _ = find_image(collection_event_image)
        if not found_collection and USE_LMSTUDIO_VISION and lmstudio_available():
            state = classify_ui(ImageGrab.grab())
            found_collection = str(state.get('screen', '')).lower() == 'collection'
        if found_collection:
            collect_event() 
        
        # Clear stored monkeys from previous level
        autoplayV2.monkey_dict.clear()

        # Show updated stats of session
        print(f'Number of games won: {i + 1 - len(broken_log)}')
        print('broken_log:')
        for item in broken_log:
            print(item) 

        time.sleep(2)

        end_collection = time.time()
        time_collection = end_collection - start_collection
        print(f'Number of games run: {i + 1}, Time taken: {time_collection/60} minutes, Average time per game: {(int(time_collection)/(i + 1))/60} minutes')

if __name__ == '__main__':
    main()
