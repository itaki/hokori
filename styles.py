from prompt_toolkit.styles import Style

import curses

def get_styles():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    HEADING = curses.color_pair(1)
    WARNING = curses.color_pair(2)
    STATUS = curses.color_pair(3)
    return{'heading': HEADING,'warning': WARNING, 'status': STATUS}


custom_style_fancy = Style([
    ('separator', 'fg:#cc5454'),
    ('qmark', 'fg:#673ab7 bold'),
    ('question', ''),
    ('selected', 'fg:#cc5454'),
    ('pointer', 'fg:#673ab7 bold'),
    ('answer', 'fg:#f44336 bold'),
])

custom_style_dope = Style([
    ('separator', 'fg:#6C6C6C'),
    ('qmark', 'fg:#FF9D00 bold'),
    ('question', ''),
    ('selected', 'fg:#5F819D'),
    ('pointer', 'fg:#FF9D00 bold'),
    ('answer', 'fg:#5F819D bold'),
])

custom_style_genius = Style([
    ('qmark', 'fg:#E91E63 bold'),
    ('question', ''),
    ('selected', 'fg:#673AB7 bold'),
    ('answer', 'fg:#2196f3 bold'),
])


def main():
    styles = get_styles
    

if __name__ == "__main__":
    main()
