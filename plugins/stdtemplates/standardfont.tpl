class StandardFont(Font):
    filename = '${font_path}standardfont.png' 
    color = (255,255,255) 
    font_face = "Baskerville"
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789&(-_"
    widths = (12,12,10,13,10,15,13,12,8,11,12,8,20,13,11,14,12,11,10,8,12,11,16,11,15,10,15,15,16,17,14,15,16,20,10,16,19,14,23,18,16,16,19,16,12,16,17,16,22,18,16,15,11,10,11,11,11,12,12,13,11,11,16,12,7,10,7,12)

    def __init__(self):
        Font.__init__(self, self.letters, self.filename, self.widths)

