class FirstScene(Scene):
    def __init__(self, parent):
        Scene.__init__(self, parent)
        self.current_anim = Animation("plugins\\stdtemplates\\outdoor.png", 1)

