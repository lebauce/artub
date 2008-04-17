# Glumol - An adventure game creator
# Copyright (C) 1998-2008  Sylvain Baubeau & Alexis Contour

# This file is part of Glumol.

# Glumol is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# Glumol is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Glumol.  If not, see <http://www.gnu.org/licenses/>.

POINT_WIDTH = 5
SNAP = 11

class Box:
    def __init__(self, parent = None):
        self.points = []
        self.gpoints = []
        self.contour = None
        if parent:
            parent.boxes.append(self)

class BoxSystemManager:
    def __init__(self):
        self.bxsystems = []

class BoxSystem:
    def __init__(self):
        self.boxes = []

    def show(self, state):
        for i in boxes:
            i.visible = state

    def get_point_at(self, pos):
        for i in self.boxes:
            index = 0
            for j in i.points:
                if pos[0] <= j[0] + SNAP / 2 and \
                   pos[0] >= j[0] - SNAP and \
                   pos[1] <= j[1] + SNAP / 2 and \
                   pos[1] >= j[1] - SNAP / 2:
                    return (i, index)
                index = index + 1
        return None

    def add_a_box(self):
        box = Box()
        self.boxes.append(box)
        return box
