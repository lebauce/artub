class Font:
    font_face = ""
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789&\"'(-_"
    scale = (1.0, 1.0)
    alpha = 1.0
    color = (255, 255, 255, 255)

    def __init__(self):
        pass

    def __init__(self, letters, filename, widths):
        self.letters = letters
        self.filename = filename
        self.widths = widths

    def draw(self):
        pass
        
    def get_size(self):
        return None
        
   
