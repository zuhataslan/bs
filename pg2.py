from os import path
from random import choice
import pygame as pg
from pygame.locals import *
from collections import namedtuple
from itertools import cycle
from dataclasses import dataclass
# Extended image support?
if not pg.image.get_extended():
    raise SystemExit("No extended image module!")


class GameSession:

    @dataclass
    class Presets:
        """Defines some game constants"""

        # Rectangels: x, y, width, height
        SCREENRECT = pg.Rect(0, 0, 723, 1024)
        ARECT = pg.Rect(317, 410, 360, 360)
        BRECT = pg.Rect(71, 164, 250, 250)

        # Colors
        WHITE = pg.Color('White')

        # Ships:
        ship_types = ('carrier', 'battleship',
                      'cruiser', 'destroyer',
                      'submarines')

        ship_images = ('carrier.png', 'battleship.png',
                       'cruiser.png', 'destroyers.png',
                       'submarines.png')

        ship_hps = (5, 4, 3, 2, 1)      # Hit points
        ship_qtys = (1, 1, 1, 2, 2)     # Quantity of each ship type in a fleet
        SHIPS = zip(ship_qtys, ship_types, ship_hps)

    @dataclass
    class Player:
        _id_: int
        _name_: str
        _move_: tuple
        _moves_: list
        _score_: int
        _hits_: int
        _misses_: int
        _turn_: bool

    @dataclass
    class Vessel:
        stype: str
        image: str
        hp: int


#              Game Constants
##################################################
# Ships:
SHIP = namedtuple('SHIP', ['type', 'image', 'hp'])
CARRIER = SHIP('carrier', 'carrier.png', 5)
BATTLESHIP = SHIP('battleship', 'battleship.png', 4)
CRUISER = SHIP('cruiser', 'cruiser.png', 3)
DESTROYER = SHIP('destroyer', 'destroyers.png', 2)
SUBMARINES = SHIP('submarines', 'submarines.png', 1)

# Screen:
SCREENRECT = pg.Rect(0, 0, 723, 1024)  # Rectangel drawn one whole screen
ARECT = pg.Rect(317, 410, 360, 360)   # Rectangel drawn on main grid
BRECT = pg.Rect(71, 164, 250, 250)    # Ractangel drwan on mini grid
##################################################


def load_image(image):
    """Get image for graphical representation of ship
    and other related data"""
    APPDIR = path.split(path.abspath(__file__))[0]
    file = path.join(APPDIR, "images", image)

    try:
        img = pg.image.load(file)
    except pg.error:
        raise SystemExit(f"Could not load image: {file}, {pg.get_error()}")
    # Return type, hitpoints, image surface, pg.Rect of image
    return img # .convert_alpha()


class Ship(pg.sprite.DirtySprite):
    """ Representing ship """
    # TODO: Use enum class for orientation


    def __init__(self, _type):
        """
        _type: type of ship
        on_rect: rect surface to blit on
        """
        pg.sprite.Sprite.__init__(self, self.containers)

        # random orientation of ship.  -1: Horizontal, 1: Vertical
        self.facing = choice((1, -1))
        self.speed = 36         # One grid cell is 36 pixels.
        self.type = _type.type       # Classification of ship. neccessary attr???
        self.hp = _type.hp      # Size on grid andHitpoints: Ship sinks at 0
        self.lock = False       # When True, don't move

        # graphical representation of ship object
        # used by pg.sprite.Group() to draw and redraw
        # sprites on display and position at coordinates
        self.frame = 0
        self.image = load_image(_type.image)
        self.rect = self.image.get_rect()
        self.center = self.rect.center

    def update(self):
        """This method is called on each loop"""
        if self.hp < 1:     # If ship is not alive
            self.kill()     # removethe sprite from all groups containing it
        if not ARECT.contains(self.rect):
            self._clamp()
        self.frame = self.frame + 1     # make it dirty to update each loop

    def move(self, Xdir, Ydir):
        """Move ship by offset
        """
        if not self.lock:
            if Xdir or Ydir:
                """Move on X- and Y-axis"""
                Xdir = Xdir * self.speed    # multiply by speed to move in steps
                Ydir = Ydir * self.speed    # (speed == one grid square in pixels)
                before = self.rect
                self.rect.x += Xdir
                self.rect.y += Ydir
                self.frame = self.frame + 1
                self._clamp()

    def rotate(self):
        """Rotates the ship image"""
        rotate_by = 90
        times = 0
        if not self.lock:
            center = self.center  # current coordinates of object center
            if facing == 1:
                # object is displayed horizontally, rotate to vertical
                # rotate() rotates image counterclockwise
                # transform returns pygame.Surface object
                times = 3   # Rotate 3 times, 270 degrees
                angel = rotate_by * times
                temp = pygame.transform.rotate(self.image, angel)
                self.rect = temp.get_rect()
                self.facing = -1
            elif facing == -1:
                # object is displayed vertically, rotate to horizontal
                times = 1
                angel = rotate_by * times
                temp = pygame.transform.rotate(self.image, angel)
                self.rect = temp.get_rect()
                self.facing = 1
            self.rect.center = center       # Rotate on center
            self.frame = self.frame + 1     # Make sprite dirty
            self._clamp()

    def _clamp(self):
        """Confines the object in a rect's boundaries"""
        self.rect = self.rect.clamp(ARECT)

    def lock(self):
        """Lock the ship placement and orientation"""
        self.lock = True


def main():

    # Init pygame
    pg.init()
    flags = pg.RESIZABLE | pg.SCALED | pg.HWSURFACE | pg.DOUBLEBUF
    # Check best depth
    depth = pg.display.mode_ok(SCREENRECT.size, SRCALPHA, flags)
    # Init screen
    screen = pg.display.set_mode(SCREENRECT.size)
    screen.fill(pg.Color('White'))

    agrid = pg.Surface(ARECT.size, SRCALPHA)
    bgrid = pg.Surface(BRECT.size, SRCALPHA)
#    agrid.fill((255,255,255))
#    bgrid.fill((255,255,255))
    board = pg.image.load('723pxsvg.png').convert_alpha()

    # Put all on screen
    screen.blit(board, (0, 0))
    screen.blit(agrid, ARECT)
    screen.blit(bgrid, BRECT)
    # Update display with above
    pg.display.flip()
    fps = pg.time.Clock()

    pg.display.set_caption("Battleship")
    pg.mouse.set_visible(1)

    # Create the sprite group to add ship objects
    # and track dirty sprites
    ships = pg.sprite.Group()
    all = pg.sprite.RenderUpdates()

    # assign sprite groups to sprite classes
    Ship.containers = ships, all
    carrier = Ship(CARRIER)
    ships.add(carrier)
    pg.key.set_repeat()  # Turn off key repeat

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()

            elif event.type == pg.KEYDOWN:
                if any([K_LEFT, K_RIGHT, K_DOWN, K_UP]):
                    keystate = pg.key.get_pressed()
                    pg.event.clear()
                    # Movement input:
                    # Subtract left from up, up from left.
                    # gives -1 or 1. Multiplicated by 'speed' to
                    # move once in direction:
                    xdir = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]
                    ydir = keystate[pg.K_DOWN] - keystate[pg.K_UP]
                    print(xdir, ydir)
                    carrier.move(xdir, ydir)
                pg.event.clear()

        # Clear screen from all sprites
        all.clear(screen, board)
        # Update all sprites
        all.update()
        dirty = all.draw(screen)
        pg.display.update(dirty)
        pg.display.flip()

        fps.tick(24)


if __name__ == '__main__':
    main()


