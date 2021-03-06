#!/usr/bin/env python
# -*- coding: utf-8 -*-
#       
#       Copyright 2012 Anne Archibald <peridot.faceted@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#       
# 

import gamemap

class ActionFailure(Exception):
	"""Action.__call__ can raise this whenever the action fails for
	any reason."""
	pass

class Action(object):
    """An action is a request for the game to do something atomic.
    
    This may be "turn left", "swing my sword at this monster", or
    "try picking this lock". It takes a certain amount of time and/or
    resources, and it cannot be interrupted.
    
    Often actions are too fine-grained for convenient use by the player,
    who instead issues higher-level commands, which yield a sequence
    of actions. That said, every change the user makes in the game
    world passes through actions; they handle making sure that (for
    example) things that are supposed to take time, do take time.
    """
    def __call__(self, gameboard):
        raise NotImplemented

class Turn(Action):
    def __init__(self, right): #FIXME: does 'right' mean clockwise?
        self.right = right
    def __call__(self, gameboard):
        if self.right:
            gameboard.PC.orientation += 1
        else:
            gameboard.PC.orientation -= 1
        gameboard.PC.orientation %= 8

class Advance(Action):
    def __call__(self, gameboard):
        x, y = gameboard.PC.coords
        delta_x, delta_y = gamemap.orientation_to_delta[gameboard.PC.orientation]
        to_x, to_y = x+delta_x, y+delta_y
        if gameboard.gamemap.is_passable((to_x,to_y)):

            #check if any doors in the way
            #doors register as always passable, so pathing can work
            #if filter(lambda x: isinstance(x,gamemap.Door), gameboard.gamemap.objects)
            #^ temporarily cancelled: made door.passable depend on open, disadvantage being no pathing through doors

            gameboard.gamemap.objects[gameboard.PC.coords].remove(gameboard.PC)
            gameboard.PC.coords = to_x, to_y
            gameboard.gamemap.objects[gameboard.PC.coords].append(gameboard.PC)
        else:
            raise ActionFailure, "Cannot advance into (%i,%i): blocked by terrain"\
                % (to_x, to_y)

class OpenDoor(Action):
    def __init__(self, subj, obj):
        self.subj = subj
        self.door = obj
    def __call__(self, gameboard):
        if not gamemap.adjacent(self.subj.coords, self.door.coords):
            raise ActionFailure, "Cannot open door: not adjacent to it."
        if self.door.closed:
            self.door.closed = False

class CloseDoor(Action):
    def __init__(self, subj, obj):
        self.subj = subj
        self.door = obj
    def __call__(self, gameboard):
        if not gamemap.adjacent(self.subj.coords, self.door.coords):
            raise ActionFailure, "Cannot close door: not next to it."
        if not self.door.closed:
            self.door.closed = True


if __name__=='__main__':
    pass
