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
