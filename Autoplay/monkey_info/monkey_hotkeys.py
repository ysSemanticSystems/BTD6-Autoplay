
# Each entry is either the official name or a shorthand name.
# Shorthand names generally have the word 'monkey' cut out of them,
# or some equivalent. All names have capital first letters
hotkeys = {
    'Hero': 'U',
    'Dart Monkey': 'Q',
    'Dart': 'Q',
    'Boomerang Monkey': 'W',
    'Boomerang': 'W',
    'Boom': 'W',
    'Bomb Shooter': 'E',
    'Bomb': 'E',
    'Tack Shooter': 'R',
    'Tack': 'R',
    'Ice Monkey': 'T',
    'Ice': 'T',
    'Glue Gunner': 'Y',
    'Glue': 'Y',
    'Sniper Monkey': 'Z',
    'Sniper': 'Z',
    'Monkey Sub': 'X',
    'Sub': 'X',
    'Monkey Buccaneer': 'C',
    'Buccaneer': 'C',
    'Monkey Ace': 'V',
    'Ace': 'V',
    'Heli Pilot': 'B',
    'Heli': 'B',
    'Mortar Monkey': 'N',
    'Mortar': 'N',
    'Dartling Gunner': 'M',
    'Gunner': 'M',
    'Wizard Monkey': 'A',
    'Wizard': 'A',
    'Wiz': 'A',
    'Super Monkey': 'S',
    'Super': 'S',
    'Ninja Monkey': 'D',
    'Ninja': 'D',
    'Alchemist': 'F',
    'Alch': 'F',
    'Druid': 'G',
    'Banana Farm': 'H',
    'Farm': 'H',
    'Spike Factory': 'J',
    'Spike Fac': 'J',
    'Spike': 'J',
    'Monkey Village': 'K',
    'Village': 'K',
    'Engineer Monkey': 'L',
    'Engineer': 'L',
    'Beast Handler': 'I',
    'Beast': 'I',
    # No default hotkey in current BTD6. Bind these in Settings → Hotkeys
    # if you want scripts to place them.
    'Mermonkey': '',
    'Mer': '',
    'Desperado': '',
    'Skywarden': '',
    'Upgrade 1': ',',
    'Upgrade 2': '.',
    'Upgrade 3': '/',
    'Sell': 'backspace',
    'Strong': 'ctrl tab'
}

reversed_hotkeys = {
    'U': 'Hero',
    'Q': 'Dart Monkey',
    'W': 'Boomerang Monkey',
    'E': 'Bomb Shooter',
    'R': 'Tack Shooter',
    'T': 'Ice Monkey',
    'Y': 'Glue Gunner',
    'Z': 'Sniper Monkey',
    'X': 'Monkey Sub',
    'C': 'Monkey Buccaneer',
    'V': 'Monkey Ace',
    'B': 'Heli Pilot',
    'N': 'Mortar Monkey',
    'M': 'Dartling Gunner',
    'A': 'Wizard Monkey',
    'S': 'Super Monkey',
    'D': 'Ninja Monkey',
    'F': 'Alchemist',
    'G': 'Druid',
    'H': 'Banana Farm',
    'J': 'Spike Factory',
    'K': 'Monkey Village',
    'L': 'Engineer Monkey',
    'I': 'Beast Handler',
    ',': 'Upgrade 1',
    '.': 'Upgrade 2',
    '/': 'Upgrade 3',
    'backspace': 'Sell',
    'ctrl tab': 'Strong'
}

# --------------------- Not important -------------------
# (it's just how I generated the dicts)

# reversed_hotkeys = {v: k for k, v in hotkeys.items()}
# for name, key in reversed_hotkeys.items():
#     print(f'\'{name}\': \'{key}\',')


def get_dict():
    '''method I used to generate the dict from a copy-paste from online'''
    text = '''
    U	Hero
    Q	Dart Monkey
    W	Boomerang Monkey
    E	Bomb Shooter
    R	Tack Shooter
    T	Ice Monkey
    Y	Glue Gunner
    Z	Sniper Monkey
    X	Monkey Sub
    C	Monkey Buccaneer
    V	Monkey Ace
    B	Heli Pilot
    N	Mortar Monkey
    M	Dartling Gunner
    A	Wizard Monkey
    S	Super Monkey
    D	Ninja Monkey
    F	Alchemist
    G	Druid
    H	Banana Farm
    J	Spike Factory
    K	Monkey Village
    L	Engineer Monkey
    '''
    text = text.split('\n')
    text2 = []
    for item in text:
        if len(item) > 0:
            item = item.split()
            item.append(item[0])
            item.pop(0)
            text2.append(item)

    for item in text2:
        name = ' '.join(item[:-1])
        key = item[-1]
        print(f'\'{name}\': \'{key}\',')

    '''
    , or NUMPAD1	Upgrade on Path 1, Upgrade Hero
    . or NUMPAD 2	Upgrade on Path 2
    / or NUMPAD 3	Upgrade on Path 3
    ← Backspace	Sell
    1-=	Activate Special Abilities
    Ctrl + 1-=	Send bloons (Red-Ceramic) in Sandbox
    Ctrl + O-\	Send bloons (MOAB-BAD) in Sandbox
    ⇧ Shift + 1-9	Activate Powers
    Spacebar	Start/Fast Forward
    ⇧ Shift + Spacebar	Send next round (races)
    Tab ↹	Change Target Priority (right)
    Ctrl + Tab ↹	Change Target Priority (left)
    Esc	Pause or exit menu
    '''