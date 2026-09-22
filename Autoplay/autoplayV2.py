#!/usr/bin/python3
#
# Desc: Plays through a level once a level is loaded.
# Adapted for macOS (Mac mini M4 Pro) and BTD6 as of September 2026.
#
from __future__ import annotations

import sys
import time
from pathlib import Path

import cv2
import numpy as np
import pyautogui
from PIL import Image, ImageGrab
from pytesseract import pytesseract

AUTOPLAY_DIR = Path(__file__).resolve().parent
if str(AUTOPLAY_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOPLAY_DIR))

from action_class import Action
from config import GAME_MODE, REFERENCE_DIR, TESSERACT_CMD, USE_LMSTUDIO_VISION
from input_backend import click_design, press
from lmstudio_client import classify_ui, is_available as lmstudio_available, read_money
from monkey_info.monkey_class import Monkey
from monkey_info.monkey_hotkeys import hotkeys, reversed_hotkeys
from monkey_info.monkey_info import monkey_info
from screen import get_screen

print("------------------")

# region --Initial Set-up--
pytesseract.tesseract_cmd = TESSERACT_CMD

# Action scripts and menu clicks were authored against 1920x1080.
test_scrn_width = 1920
test_scrn_height = 1080

_screen = get_screen()
screensize = (_screen.logical_width, _screen.logical_height)
screen_width = _screen.logical_width
screen_height = _screen.logical_height
print(
    f"Screensize: {screensize}  pixels={_screen.pixel_width}x{_screen.pixel_height}  "
    f"scale={_screen.scale:.2f}  mode={GAME_MODE}"
)

monkey_dict = {}
game_mode = GAME_MODE

map_is_sanctuary = False
manual_rounds = False

# endregion

# region ------------- Image Grabbing Methods --------------
def _resolve_reference(given_image: str) -> str:
    path = Path(given_image)
    if path.exists():
        return str(path)
    candidate = REFERENCE_DIR / path.name
    if candidate.exists():
        return str(candidate)
    return given_image


def _money_crop() -> Image.Image:
    bbox = get_screen().to_pixel_bbox(344, 10, 500, 75)
    return ImageGrab.grab(bbox=bbox)


def get_money():
    """Extract cash from the HUD. Tesseract first, local Gemma vision as backup."""
    print_stats = False
    img = _money_crop()
    arr = np.array(img)
    height, width = arr.shape[:2]
    for loop1 in range(height):
        for loop2 in range(width):
            r, g, b = arr[loop1, loop2][:3]
            if int(r) + int(g) + int(b) < 700:
                arr[loop1, loop2] = [0, 0, 0] + list(arr[loop1, loop2][3:])
    cleaned = Image.fromarray(arr)

    text = pytesseract.image_to_string(cleaned, config="--psm 7")
    if print_stats:
        print(f"Text:{text}")
    money = "".join(ch for ch in text if ch.isdigit())
    try:
        value = int(money)
    except ValueError:
        value = -1

    if value < 0 and USE_LMSTUDIO_VISION and lmstudio_available():
        value = read_money(img)
        if print_stats:
            print(f"LM Studio money:{value}")
    return value


def get_round():
    """Extract the current round from the HUD."""
    bbox = get_screen().to_pixel_bbox(1480, 10, 1570, 75)
    img = ImageGrab.grab(bbox=bbox)
    text = pytesseract.image_to_string(img, config="--psm 7")
    print(f"Text:{text}")
    digits = "".join(ch for ch in text if ch.isdigit())
    try:
        return int(digits)
    except ValueError:
        print("round not recognized")
        return -1


def find_image(given_image: str, maxLoc_thresh=0.05):
    """
    See if given image is on the screen.
    Templates were captured at 1920x1080; they are resized to this display.
    :returns: True if symbol found, false otherwise.
              maxloc of match (or logical [x, y] when used by play_collection_event)
    """
    method = cv2.TM_SQDIFF_NORMED
    image = pyautogui.screenshot()
    large_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    small_image = cv2.imread(_resolve_reference(given_image))
    if small_image is None:
        print(f"Template missing: {given_image}")
        return False, 1.0

    fx, fy = get_screen().template_scale()
    if abs(fx - 1.0) > 0.02 or abs(fy - 1.0) > 0.02:
        new_w = max(1, int(small_image.shape[1] * fx))
        new_h = max(1, int(small_image.shape[0] * fy))
        small_image = cv2.resize(small_image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    if small_image.shape[0] > large_image.shape[0] or small_image.shape[1] > large_image.shape[1]:
        return False, 1.0

    result = cv2.matchTemplate(small_image, large_image, method)
    maxLoc, minLoc, comparedLoc, _ = cv2.minMaxLoc(result)
    if maxLoc < maxLoc_thresh:
        return True, maxLoc
    return False, maxLoc


def find_image_location(given_image: str, maxLoc_thresh=0.05):
    """Like find_image, but also returns the logical-pixel match location."""
    method = cv2.TM_SQDIFF_NORMED
    image = pyautogui.screenshot()
    large_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    small_image = cv2.imread(_resolve_reference(given_image))
    if small_image is None:
        return False, [0, 0], 1.0

    fx, fy = get_screen().template_scale()
    if abs(fx - 1.0) > 0.02 or abs(fy - 1.0) > 0.02:
        new_w = max(1, int(small_image.shape[1] * fx))
        new_h = max(1, int(small_image.shape[0] * fy))
        small_image = cv2.resize(small_image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    result = cv2.matchTemplate(small_image, large_image, method)
    maxLoc, minLoc, comparedLoc, _ = cv2.minMaxLoc(result)
    logical = list(get_screen().pixel_to_logical(*comparedLoc))
    return maxLoc < maxLoc_thresh, logical, maxLoc


def round_finished() -> bool:
    '''
    Checks if the round is finished by looking at play/start-round button
    
    :returns: True if round is stopped, False if round is still going
    '''
    result, stopped = find_image(str(REFERENCE_DIR / 'round_stopped.png'))
    result2, going = find_image(str(REFERENCE_DIR / 'round_going.png'))
    # print(result, stopped, result2, going)
    # Less means better match
    if stopped < going:
        return True # round is stopped
    else:
        return False # round is still going


def check_victory_loss():
    '''
    Check if we have won or lost the game.
    
    :returns: found_victory (bool), found_loss (bool)
    '''
    found_victory, _ = find_image(str(REFERENCE_DIR / 'victory.png'))
    found_loss, _ = find_image(str(REFERENCE_DIR / 'defeat.png'))
    if not found_victory and not found_loss and USE_LMSTUDIO_VISION and lmstudio_available():
        state = classify_ui(ImageGrab.grab())
        screen = str(state.get('screen', '')).lower()
        found_victory = screen == 'victory'
        found_loss = screen == 'defeat'
    return found_victory, found_loss
    

def wait_till_victory():
    for _ in range(50):
        found_victory, found_loss = check_victory_loss()
        if found_victory:
            print('Victory!')
            return True
        if found_loss:
            print('Loss :(')
            return False
        time.sleep(15)


# endregion

# region ------------- Clicking-Only Methods -----------------

def start_game():
    '''start the game'''
    print('\nStarting Game')
    press('space')
    press('space')


def start_round(round_count: int=0) -> int: 
    '''start the round'''
    press('space')
    round_count += 1
    return round_count


def change_auto_start():
    '''Flip the auto-start switch'''
    click_design((1601, 41))
    time.sleep(.2)
    click_design((1322, 334))
    time.sleep(.2)
    click_design((1601, 41))
# endregion

# region ------ Data-Using/Data-Manipulating Methods -------
# TODO: (optional) move action functions to action class
def do_action(action: Action, old_gold: int, action_cost: int) -> bool:
    '''Perform the given action. This function assumes there is enough money to do so.'''
    ####
    # Placing actions
    if action.type == 'place':
        # check if monkey already in monkey_dict
        if action.name in monkey_dict:
            print(f'YO. Your duplicated a monkey name dude. Fix that please. Name:{action.name}')

        # add monkey to monkey_dict
        monkey_dict[action.name] = Monkey(position=action.position, name=action.name, mtype=reversed_hotkeys[hotkeys[action.action.title()]])

        act_name = action.action
        # Place monkey
        key = hotkeys[act_name.title()]
        if not key:
            print(f'{act_name} has no default hotkey. Bind it in BTD6 settings.')
            return False
        press(key)
        click_design(action.position) 

        return True

    ####
    # Upgrading actions
    if action.type == 'upgrade':
        monkey: Monkey
        monkey = monkey_dict[action.name]

        if action_cost > 4000 and  old_gold > action_cost*1.2:
            print('Possible misread of money:', old_gold)
            return False

        # Click Monkey
        click_design(monkey.position)
        time.sleep(.1)

        # Upgrade monkey
        press(hotkeys[action.action.title()])
        
        # Click away to reset gui
        click_design((1600, 1040))

        # Check to make sure action actually occurred an there wasn't a misread of money. 
        # (This functionality should be double checked)
        if action.cost > 4000:
            print(f'Upgrade over 4000. old_gold: {old_gold}') 
            time.sleep(2)
            new_money = get_money()
            if new_money - old_gold > 0:
                # action never occurred
                print('Upgrade Failed')
                return False
            else:
                print('Success?')

        # Update stored monkey data
        monkey.upgrade(int("".join(filter(str.isdigit, action.action))))

        return True
    
    ####
    # Targeting actions
    if action.type == 'target':
        if action.action == 'Strong':
            # Find monkey
            monkey: Monkey
            monkey = monkey_dict[action.name]

            # Click monkey
            click_design(monkey.position)

            # Change targeting from first to strong
            press('ctrl tab')
            
            # Click away to reset gui
            click_design((1600, 1040))

            return True

        if action.action == 'First':
            # Find monkey
            monkey: Monkey
            monkey = monkey_dict[action.name]

            # Click monkey
            click_design(monkey.position)

            # Change targeting from strong to first
            press('tab')

            return True

    ####
    # Starting game
    if action.type == 'start':
        start_game()
        return True

    ####
    # Clicking spot
    if action.type == 'click':
        click_design(action.position)

        return True

    ####
    # Finishing game
    if action.type == 'finish':
        return True

    # if the actions failed, return False
    return False


def do_action_manual(action: Action, old_gold: int, action_cost: int, round_count: int):
    '''
    Perform the given action. This function assumes there is enough money to do so.
    
    :returns: True if action was completed (bool)
              round_count (int)
    '''
    global manual_rounds
    ####
    # Placing actions
    if action.type == 'place':
        # check if monkey already in monkey_dict
        if action.name in monkey_dict:
            print(f'YO. Your duplicated a monkey name dude. Fix that please. Name:{action.name}')

        # add monkey to monkey_dict
        monkey_dict[action.name] = Monkey(position=action.position, name=action.name, mtype=reversed_hotkeys[hotkeys[action.action.title()]])
        #setattr(monkey_dict[action.name], 'island', island)

        act_name = action.action
        # Place monkey
        key = hotkeys[act_name.title()]
        if not key:
            print(f'{act_name} has no default hotkey. Bind it in BTD6 settings.')
            return False, round_count
        press(key)
        click_design(action.position) 

        return True, round_count

    ####
    # Upgrading actions
    if action.type == 'upgrade':
        monkey: Monkey
        monkey = monkey_dict[action.name]

        # account for misreads of money
        if action_cost > 4000 and  old_gold > action_cost*1.2:
            print('Possible misread of money:', old_gold)
            return False, round_count

        # Click Monkey
        click_design(monkey.position)
        time.sleep(.1)

        # Upgrade monkey
        press(hotkeys[action.action.title()])
        
        # Click away to reset gui
        click_design((1600, 1040))

        # Check to make sure action actually occurred an there wasn't a misread of money. This functionality needs to be double checked
        if action.cost > 4000:
            print('Upgrade over 4000')
            time.sleep(2)
            new_money = get_money()
            if new_money - old_gold > 0:
                # action never occurred
                print('Upgrade Failed')
                return False, round_count

        # Update stored monkey data
        monkey.upgrade(int("".join(filter(str.isdigit, action.action))))

        return True, round_count
    
    ####
    # Targeting actions
    if action.type == 'target':
        if action.action == 'Strong':
            # Find monkey
            monkey: Monkey
            monkey = monkey_dict[action.name]
            
            # Click Monkey
            click_design(monkey.position)
            time.sleep(.1)

            # Change targeting from first to strong
            press('ctrl tab')
            
            # Click away to reset gui
            click_design((1600, 1040))

            return True, round_count

        if action.action == 'First':
            # Find monkey
            monkey: Monkey
            monkey = monkey_dict[action.name]

            # Click monkey
            click_design(monkey.position)

            # Change targeting from strong to first
            press('tab')

            return True, round_count

    ####
    # Starting game
    if action.type == 'start':
        change_auto_start()
        if round_finished():
            start_round()
        return True, round_count + 1
    
    ####
    # Finish
    if action.type == 'finish':
        change_auto_start()
        manual_rounds = False 
        start_round(round_count)
        return True, round_count

    # if the actions failed, return False
    return False, round_count


def do_action_sanctuary(action: Action, old_gold: int, action_cost: int, round_count: int):
    '''
    Perform the given action in Sanctuary map. This function assumes there is enough money to do so.

    :returns: True if action was completed (bool)
              round_count (int)

    All positions are based on the middle island. Adjusted from there.
    This is very similar to do_action(), but because this is a one-off thing, I made this a separate function 
    so that do_action() is less confusing
    '''
    global manual_rounds
    # Find whether top island is left, mid, or right
    island = ''
    if round_count%2 == 0:
        island = 'mid'
    if round_count%4 == 1: 
        island = 'right'
    if round_count%4 == 3:
        island = 'left'

    print(f'island: {island} round: {round_count}')

    dx = 0
    dy = 0
 
    # Adjust for shifts in island
    if island == 'left':
        dx = -145
        dy = -20
    if island == 'right':
        dx = 145
        dy = -20
    

    ####
    # Placing actions
    if action.type == 'place':
        # check if monkey already in monkey_dict
        if action.name in monkey_dict:
            print(f'YO. Your duplicated a monkey name dude. Fix that please. Name:{action.name}')

        # add monkey to monkey_dict
        monkey_dict[action.name] = Monkey(position=action.position, name=action.name, mtype=reversed_hotkeys[hotkeys[action.action.title()]])
        #setattr(monkey_dict[action.name], 'island', island)

        act_name = action.action
        # Place monkey
        key = hotkeys[act_name.title()]
        if not key:
            print(f'{act_name} has no default hotkey. Bind it in BTD6 settings.')
            return False, round_count
        press(key)
        click_design(tuple(np.array(action.position) + np.array([dx, dy]))) 

        return True, round_count

    ####
    # Upgrading actions
    if action.type == 'upgrade':
        monkey: Monkey
        monkey = monkey_dict[action.name]

        # account for misreads of money
        if action_cost > 4000 and  old_gold > action_cost*1.2:
            print('Possible misread of money:', old_gold)
            return False, round_count

        # Click Monkey
        click_design(tuple(np.array(monkey.position) + np.array([dx, dy])))
        time.sleep(.1)

        # Upgrade monkey
        press(hotkeys[action.action.title()])
        
        # Click away to reset gui
        click_design((1600, 1040))

        # Check to make sure action actually occurred an there wasn't a misread of money. This functionality needs to be double checked
        if action.cost > 4000:
            print('Upgrade over 4000')
            time.sleep(2)
            new_money = get_money()
            if new_money - old_gold > 0:
                # action never occurred
                print('Upgrade Failed')
                return False, round_count

        # Update stored monkey data
        monkey.upgrade(int("".join(filter(str.isdigit, action.action))))

        return True, round_count
    
    ####
    # Targeting actions
    if action.type == 'target':
        if action.action == 'Strong':
            # Find monkey
            monkey: Monkey
            monkey = monkey_dict[action.name]
            
            # Click Monkey
            click_design(tuple(np.array(monkey.position) + np.array([dx, dy])))
            time.sleep(.1)

            # Change targeting from first to strong
            press('ctrl tab')
            
            # Click away to reset gui
            click_design((1600, 1040))

            return True, round_count

        if action.action == 'First':
            # Find monkey
            monkey: Monkey
            monkey = monkey_dict[action.name]

            # Click monkey
            click_design(tuple(np.array(monkey.position) + np.array([dx, dy])))

            # Change targeting from strong to first
            press('tab')

            return True, round_count

    ####
    # Starting game
    if action.type == 'start':
        change_auto_start()
        start_game()
        return True, round_count + 1
    
    ####
    # Finish
    if action.type == 'finish':
        change_auto_start()
        manual_rounds = False 
        start_round(round_count)
        return True, round_count

    # if the actions failed, return False
    return False, round_count


def get_action_cost(action: Action) -> int:
    '''Get cost of action (especially useful when action.cost is not explicitly given)'''
    if action.cost != None:
        return action.cost

    # Get official name of monkey, ex 'Ninja Monkey'. (weird dict stuff works around the shorthand names)
    monkey_type = reversed_hotkeys[hotkeys[action.action.title()]]

    # Placing Monkeys
    if action.type == 'place' or action.type == 'monkey':
        if monkey_type != 'Hero':
            cost = monkey_info[monkey_type]['place']
        else:
            cost = monkey_info[monkey_type][action.name]
        action.cost = cost
        return cost

    # Upgrading Monkeys
    if action.type == 'upgrade':
        # Get specific monkey
        monkey = monkey_dict[action.name]
        if action.action == 'upgrade 1':
            tier_number = monkey.upgrades[0] + 1
            cost = monkey_info[monkey.mtype]['top'+str(tier_number)]
        elif action.action == 'upgrade 2':
            tier_number = monkey.upgrades[1] + 1
            cost = monkey_info[monkey.mtype]['middle'+str(tier_number)]
        elif action.action == 'upgrade 3':
            tier_number = monkey.upgrades[2] + 1
            cost = monkey_info[monkey.mtype]['bottom'+str(tier_number)]
        else:
            print(r"Upgrading action was not 'upgrade [1,2 or 3]'. Exitting.")
            exit(1)
        action.cost = cost
        return cost


    # if not placing or upgrading a monkey, action is free
    action.cost = 0
    return 0
# endregion

# -------------- Running Code -----------------
def game_loop(script) -> bool:
    '''
    Play through a game
    
    :returns: True if run was successful, False otherwise
    '''
    global manual_rounds
    global map_is_sanctuary
    # region Initialization
    # Tell if something has gone wrong in the loop, maybe it isn't seeing the money correctly
    broken_counter = 0
    broken_thresh = 650
    # To monitor the script
    script_pos = 0
    action: Action
    action = script[script_pos]
    action_cost = get_action_cost(action)
    if action_cost == None:
        print('First action somehow wasnt placing a tower, exitting program')
        exit(1)
    # To monitor gold
    old_gold = 0
    old_gold_break = 0
    same_gold_count = 0
    same_gold_thresh = 40
    # Manual Rounds
    time_last_round = time.time()
    round_count = 2

    # Check if the map is sanctuary and activate manual rounds
    if map_is_sanctuary:
        manual_rounds = True
    # endregion

    #### 
    # Main Loop
    while script_pos < len(script):
        broken_counter += 1
        # Get current money amount
        current_gold = get_money()
        # dealing with player level increased pop-ups through gold count
        if old_gold == current_gold:
            same_gold_count += 1
            if same_gold_count == same_gold_thresh:
                print('possible level up. (gold hasnt changed in a while)')
                win, loss = check_victory_loss() # just in case
                if not win or not loss:
                    for _ in range(3):
                        # Click middle to reset gui
                        click_design((837, 564))
                        time.sleep(1.5)
                    start_round(1)
                else:
                    return False
        else:
            same_gold_count = 0

        # Account for a misread of the gold
        if current_gold > old_gold*1.5 + 400 and old_gold_break <= 3:
            old_gold_break += 1
            continue
        else:
            old_gold = current_gold
            old_gold_break = 0

        # Do action if affordable
        if action_cost == 0 or action_cost <= current_gold:
            print(f'Performing action: {action.name} {action.action} | ', end='')
            if map_is_sanctuary:
                done, round_count = do_action_sanctuary(action, current_gold, action_cost, round_count)
            elif manual_rounds:
                done, round_count = do_action_manual(action, current_gold,  action_cost, round_count)
            else:
                done = do_action(action, current_gold, action_cost)
            time.sleep(.1)
            if done:
                # Move to next action
                script_pos += 1
                try:
                    action = script[script_pos]
                except:
                    break
                # Update action cost
                action_cost = get_action_cost(action)
                print(f'Next action name: {action.name} {action.action}, Cost: {action_cost}')
                broken_counter = 0
            else:
                print('********logging that an action failed. Are we ok?')

        # If we level-up mid game, click out of it
        if broken_counter == int(broken_thresh/1.5):
            print('possible level up broken')
            win, loss = check_victory_loss() # just in case
            if not win or not loss:
                for _ in range(4):
                    # Click middle to reset gui
                    click_design((837, 564))
                    time.sleep(1.5)
                start_round(1)
            else:
                return False

        # Exit if loop somehow broke
        if broken_counter > broken_thresh:
            print(f'Nothing has occurred within broken_thresh:{broken_thresh} loops. Something has probably gone wrong.')
            from knowledge_store import record_error, record_failure
            record_failure(
                'Game loop made no progress',
                f'No affordable action completed within {broken_thresh} polls. '
                f'Next action was {action.name} {action.action} costing {action_cost}. '
                'Money OCR, a stale click, or a price change can cause this.',
                tags=['game-loop', 'money', str(action.name)],
            )
            record_error(
                'Game loop exceeded the stall threshold',
                f'broken_thresh={broken_thresh} action={action.name} {action.action} cost={action_cost}',
                tags=['game-loop'],
            )
            return False

        # Manually update rounds based on sanctuary
        if manual_rounds:
            # move to next round if psi's ability is grayed out
            if round_count > 7:
                if round_finished():
                    #print(round_count)
                    round_count = start_round(round_count)
                    time.sleep(1)

            # increased wait time for round 7
            elif round_count == 7:
                time_elapsed = time.time() - time_last_round
                if time_elapsed > 22: 
                    print('(round 7) low round time start')
                    round_count = start_round(round_count)
                    time_last_round = time.time()
            # waiting a set time between early rounds
            else:
                time_elapsed = time.time() - time_last_round
                if time_elapsed > 20: 
                    print('low round time start')
                    round_count = start_round(round_count)
                    time_last_round = time.time()
                                    

        time.sleep(.5)

    # All actions have been completed, wait for game to end
    won = wait_till_victory()
    from knowledge_store import record_failure, record_success
    if won:
        record_success(
            'Action script finished and the game was won',
            f'Script length {len(script)} on mode {game_mode}.',
            tags=['game-loop', 'victory', game_mode],
        )
    else:
        record_failure(
            'Action script finished but the game was not won',
            'Victory was not detected before the wait timed out, or a defeat screen appeared.',
            tags=['game-loop', 'defeat', game_mode],
        )
    return won


def main():
    # --- EXAMPLE OF RUNNING A SCRIPT:
    # from action_scripts.collection_scripts.infernal_script import infernal_script
    # game_completed = game_loop(infernal_script)
    pass


if __name__ == '__main__':
    main()
        




