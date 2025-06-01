#!/usr/bin/python3 
#
#
# Desc: Plays through a level once a level is loaded.
#
# 
#


import ctypes

import keyboard
import pyautogui
import pydirectinput

import playsound
import time
from PIL import Image, ImageGrab
from pytesseract import pytesseract
import numpy as np
import cv2 # if installing, try 'pip install opencv-python'
import os

from monkey_info.monkey_hotkeys import hotkeys, reversed_hotkeys
from monkey_info.monkey_info import monkey_info
from monkey_info.monkey_class import Monkey
from action_class import Action
print('------------------')


# region --Initial Set-up--  
# Setting up tesseract (Only needed if tesseract executable is not in your PATH)
# For windows, there is a tesseract installer that is needed. Look it up.
path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.tesseract_cmd = path_to_tesseract

# Variables to determine screenshot ranges (formed from tests done on my local computer)
# (Update: looking back on this code it looks like a standard 1920x1080 resolution, which should be the default for the game)
test_scrn_width = 1920 
test_scrn_height = 1080 

# Get screen size
user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
screen_width = screensize[0]
screen_height = screensize[1]
print(f'Screensize: {screensize}')

# Define storage important to running a game
monkey_dict = {}
game_mode = 'hard'

# Special case (This map screws with the code b/c monkeys move)
map_is_sanctuary = False
manual_rounds = False

# endregion

# region ------------- Image Grabbing Methods --------------
def get_money():
    '''Extract money value using a small screenshot of the game'''
    # First indicator a screenshot is going to be taken
    # playsound.playsound(r"D:\randy\Audio\Sound Effects\The Nut Button - When Memes Become Reality.mp3")

    print_stats = False
    # Screenshot
    img = ImageGrab.grab(bbox = (int(344/test_scrn_width*int(screensize[0])), # left bound
                                int(10/test_scrn_height*int(screensize[1])), # upper bound
                                int(500/test_scrn_width*int(screensize[0])), # right bound
                                int(75/test_scrn_height*int(screensize[1]))  # lower bound
                            )
    )
    # img.show()
    img = np.asfarray(img)
    height = len(img)
    width = len(img[0])
    img.setflags(write=1)
    for loop1 in range(height):
        for loop2 in range(width):
            r,g,b = img[loop1,loop2]
            if sum([r,g,b]) < 700:
                img[loop1,loop2] = [0,0,0]

    img = Image.fromarray(np.uint8(img))
    # img.show()

    # Convert to text. (psm 6,7,8 seem to be best)
    text = pytesseract.image_to_string(img, config='--psm 7')
    if print_stats: print(f'Text:{text}')
    money = ''

    # Convert money text to number
    try:
        for char in text:
            if char.isdigit():
                money += char
        money = int(money)
        if print_stats: print(f'**********************money:{money}')
    except:
        if print_stats: print('money not recognized')
        money = -1

    return money


def get_round():
    '''Extract round value using a small screenshot of the game'''
    # First indicator a screenshot is going to be taken
    playsound.playsound(r"D:\randy\Audio\Sound Effects\The Nut Button - When Memes Become Reality.mp3")

    # Screenshot
    img = ImageGrab.grab(bbox = (int(1480/test_scrn_width*int(screensize[0])), # left bound
                                int(10/test_scrn_height*int(screensize[1])), # upper bound
                                int(1570/test_scrn_width*int(screensize[0])), # right bound
                                int(75/test_scrn_height*int(screensize[1]))  # lower bound
                            )
    )
    img.show()

    # 6,7,8 seem to be best
    text = pytesseract.image_to_string(img, config='--psm 7')
    print(f'Text:{text}')
    round = ''

    # Convert money text to number
    try:
        for char in text:
            if char.isdigit():
                round += char
        money = int(round)
        print(f'round:{round}')
    except:
        print('round not recognized')
        round = -1

    return round


def find_image(given_image: str, maxLoc_thresh = .05):
    '''
    See if given image is on the screen.
    :returns: True if symbol found, false otherwise.
              maxloc of match
    '''
    # with Image.open(given_image) as im:
    #     im.show()

    found = False # found image
    location = [0, 0]

    method = cv2.TM_SQDIFF_NORMED

    # Read images 
    image = pyautogui.screenshot()
    # make image compatible with cv2
    large_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    small_image = cv2.imread(given_image) 

    result = cv2.matchTemplate(small_image, large_image, method)

    # We want the minimum squared difference
    maxLoc, minLoc, comparedLoc, _ = cv2.minMaxLoc(result)
    
    # Location of best match
    MPx,MPy = comparedLoc
    location = [MPx, MPy]

     # Step 2: Get the size of the template. This is the same size as the match.
    trows,tcols = small_image.shape[:2]

    # Step 3: Draw the rectangle on large_image
    cv2.rectangle(large_image, (MPx,MPy),(MPx+tcols,MPy+trows),(0,0,255),3)

    img = cv2.cvtColor(large_image, cv2.COLOR_BGR2RGB)
    im_pil = Image.fromarray(img)
    

    if maxLoc < maxLoc_thresh:
        found = True
        #im_pil.show()
        # print(maxLoc, minLoc)
        return found, maxLoc
    else:
        return found, maxLoc


def round_finished() -> bool:
    '''
    Checks if the round is finished by looking at play/start-round button
    
    :returns: True if round is stopped, False if round is still going
    '''
    result, stopped = find_image('Autoplay/reference_images/round_stopped.png')
    result2, going = find_image('Autoplay/reference_images/round_going.png')
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
    found_victory, _ = find_image('Autoplay/reference_images/victory.png')
    found_loss, _ = find_image('Autoplay/reference_images/defeat.png')
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
    # pyautogui.moveTo(1835, 1016)
    # pyautogui.click(1835, 1016)
    
    # pyautogui.moveTo(1835, 1016)
    # pyautogui.click(1835, 1016)
    pydirectinput.press('space')
    pydirectinput.press('space')


def start_round(round_count: int=0) -> int: 
    '''start the round'''
    pydirectinput.press('space')
    # pyautogui.moveTo(1835, 1016)
    # pyautogui.click(1835, 1016)
    round_count += 1
    return round_count


def change_auto_start():
    '''Flip the auto-start switch'''
    # Click Option
    pyautogui.moveTo(1601, 41)
    pyautogui.click(1601, 41)
    time.sleep(.2)

    # Click auto-start switch
    pyautogui.moveTo(1322, 334)
    pyautogui.click(1322, 334)
    time.sleep(.2)

    # Click away to reset gui
    pyautogui.moveTo(1601, 41)
    pyautogui.click(1601, 41)
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
        keyboard.press(hotkeys[act_name.title()].lower())
        keyboard.release(hotkeys[act_name.title()].lower())
        pyautogui.moveTo(action.position)
        pyautogui.click(action.position) 

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
        pyautogui.moveTo(monkey.position)
        pyautogui.click(monkey.position)
        time.sleep(.1)

        # Upgrade monkey
        pydirectinput.press(hotkeys[action.action.title()])
        
        # Click away to reset gui
        pyautogui.moveTo(1600, 1040)
        pyautogui.click(1600, 1040)

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
            pyautogui.moveTo(monkey.position)
            pyautogui.click(monkey.position)

            # Change targeting from first to strong
            pydirectinput.keyDown('ctrl')
            pydirectinput.keyDown('tab')
            time.sleep(.1)
            pydirectinput.keyUp('ctrl')
            pydirectinput.keyUp('tab')
            
            # Click away to reset gui
            pyautogui.moveTo(1600, 1040)
            pyautogui.click(1600, 1040)

            return True

        if action.action == 'First':
            # Find monkey
            monkey: Monkey
            monkey = monkey_dict[action.name]

            # Click monkey
            pyautogui.moveTo(monkey.position)
            pyautogui.click(monkey.position)

            # Change targeting from strong to first
            keyboard.press('tab')
            keyboard.release('tab')

            return True

    ####
    # Starting game
    if action.type == 'start':
        start_game()
        return True

    ####
    # Clicking spot
    if action.type == 'click':
        pyautogui.moveTo(action.position)
        pyautogui.click(action.position)

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
        keyboard.press(hotkeys[act_name.title()].lower())
        keyboard.release(hotkeys[act_name.title()].lower())
        pyautogui.moveTo(action.position)
        pyautogui.click(action.position) 

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
        pyautogui.moveTo(monkey.position)
        pyautogui.click(monkey.position)
        time.sleep(.1)

        # Upgrade monkey
        pydirectinput.press(hotkeys[action.action.title()])
        
        # Click away to reset gui
        pyautogui.moveTo(1600, 1040)
        pyautogui.click(1600, 1040)

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
            pyautogui.moveTo(monkey.position)
            pyautogui.click(monkey.position)
            time.sleep(.1)

            # Change targeting from first to strong
            pydirectinput.keyDown('ctrl')
            pydirectinput.keyDown('tab')
            time.sleep(.1)
            pydirectinput.keyUp('ctrl')
            pydirectinput.keyUp('tab')
            
            # Click away to reset gui
            pyautogui.moveTo(1600, 1040)
            pyautogui.click(1600, 1040)

            return True, round_count

        if action.action == 'First':
            # Find monkey
            monkey: Monkey
            monkey = monkey_dict[action.name]

            # Click monkey
            pyautogui.moveTo(monkey.position)
            pyautogui.click(monkey.position)

            # Change targeting from strong to first
            keyboard.press('tab')
            keyboard.release('tab')

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
        keyboard.press(hotkeys[act_name.title()].lower())
        keyboard.release(hotkeys[act_name.title()].lower())
        pyautogui.moveTo(tuple(np.array(action.position) + np.array([dx, dy])))
        pyautogui.click(tuple(np.array(action.position) + np.array([dx, dy]))) 

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
        pyautogui.moveTo(tuple(np.array(monkey.position) + np.array([dx, dy])))
        pyautogui.click(tuple(np.array(monkey.position) + np.array([dx, dy])))
        time.sleep(.1)

        # Upgrade monkey
        pydirectinput.press(hotkeys[action.action.title()])
        
        # Click away to reset gui
        pyautogui.moveTo(1600, 1040)
        pyautogui.click(1600, 1040)

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
            pyautogui.moveTo(tuple(np.array(monkey.position) + np.array([dx, dy])))
            pyautogui.click(tuple(np.array(monkey.position) + np.array([dx, dy])))
            time.sleep(.1)

            # Change targeting from first to strong
            pydirectinput.keyDown('ctrl')
            pydirectinput.keyDown('tab')
            time.sleep(.1)
            pydirectinput.keyUp('ctrl')
            pydirectinput.keyUp('tab')
            
            # Click away to reset gui
            pyautogui.moveTo(1600, 1040)
            pyautogui.click(1600, 1040)

            return True, round_count

        if action.action == 'First':
            # Find monkey
            monkey: Monkey
            monkey = monkey_dict[action.name]

            # Click monkey
            pyautogui.moveTo(np.array(monkey.position) + np.array([dx, dy]))
            pyautogui.click(np.array(monkey.position) + np.array([dx, dy]))

            # Change targeting from strong to first
            keyboard.press('tab')
            keyboard.release('tab')

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
                        pyautogui.moveTo(837, 564)
                        pyautogui.click(837, 564)
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
                    pyautogui.moveTo(837, 564)
                    pyautogui.click(837, 564)
                    time.sleep(1.5)
                start_round(1)
            else:
                return False

        # Exit if loop somehow broke
        if broken_counter > broken_thresh:
            print(f'Nothing has occurred within broken_thresh:{broken_thresh} loops. Something has probably gone wrong.')
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
    return won


def main():
    # --- EXAMPLE OF RUNNING A SCRIPT:
    # from action_scripts.collection_scripts.infernal_script import infernal_script
    # game_completed = game_loop(infernal_script)
    pass


if __name__ == '__main__':
    main()
        




