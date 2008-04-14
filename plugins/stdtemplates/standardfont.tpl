class StandardFont(Font):
    filename = '${font_path}standardfont.png' 
    color = (255,255,255) 
    font_face = "Baskerville"
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789&(-_"
    widths = (12,11,10,13,10,14,12,12,7,10,12,8,20,13,11,13,12,10,11,8,13,11,16,10,14,9,14,13,15,15,14,14,16,19,11,15,18,14,22,18,16,14,19,15,12,16,17,15,22,19,15,13,11,10,10,10,11,11,12,12,11,11,15,12,6,9,7,11) 

    def __init__(self):
        Font.__init__(self, self.letters, self.filename, self.widths)

