class $name(Game):
    class MouseCursor(Sprite):
        class MouseCursorBitmap(Animation):
            filenames = ['${images_path}mousecursor1.png','${images_path}mousecursor2.png','${images_path}mousecursor3.png','${images_path}mousecursor4.png','${images_path}mousecursor5.png']
            delays = [100,100,100,100,100]
            orders = [0,1,2,3,4]
            hotspots = [Point(1, 4)] * 5

        animation = MouseCursorBitmap 

    def __init__(self):
        Game.__init__(self)

    def __glumolinit__(self):
        self.cursor = self.MouseCursor(self.screen)
        self.mouse_sprite = self.cursor

    def create_first_scene(self):
        if hasattr(self, "first_scene") and self.first_scene != 'None':
            self.scene = globals()[self.first_scene](self.screen)
        else:
            self.scene = self.screen
        
    def on_main(self):
        self.create_first_scene()
        $name.__glumolinit__(self)
        if hasattr(self, "first_scene") and self.first_scene != 'None':
            self.scene.on_enter()
        Game.on_main(self)
        
    def set_scene(self, scene):
        self.current_scene = scene

    def on_key_down(self, key):
        if key == SPACE:
            self.scene.transparent = not self.scene.transparent
            self.interface.transparent = not self.interface.transparent
            self.paused = not self.paused
        elif key == ESCAPE:
            self.stop = True
            
    first_scene = '$first_scene'

GameClass = $name
