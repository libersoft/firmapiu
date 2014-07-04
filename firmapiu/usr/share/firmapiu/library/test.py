import curses

class Pippo(object):
    
    def __new__(cls, *args, **kwargs):
        print '__new__'
        return object.__new__(cls, *args, **kwargs)
    
    def __init__(self):
        print '__init__'

    def __enter__(self):
        print '__enter__'
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        print '__exit__'
        
    def __del__(self):
        print '__del__'

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)
begin_x = 20; begin_y = 7
height = 5; width = 40
win = curses.newwin(height, width, begin_y, begin_x)
pad = curses.newpad(100, 100)
#  These loops fill the pad with letters; this is
# explained in the next section
for y in range(0, 100):
    for x in range(0, 100):
        try:
            pad.addch(y,x, ord('a') + (x*x+y*y) % 26)
        except curses.error:
            pass

#  Displays a section of the pad in the middle of the screen
pad.refresh(0,0, 5,5, 20,75)
while 1:
    c = stdscr.getch()
    if c == ord('p'):
        print 'pippo'
    elif c == ord('q'):
        break  # Exit the while()
    elif c == curses.KEY_HOME:
        x = y = 0
