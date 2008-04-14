class Sound(object):
    def __glumolinit__(self):
        pass
        
    def __init__(self, filename):
        pass
        
    def play(self):
        pass
        
    def stop(self):
        pass
        
    def get_playing(self):
        return False
        
    def set_playing(self, state):
        pass
        
    playing = property(get_playing, set_playing)
    
    def get_echo(self):
        return 0
        
    def set_echo(self, echo):
        pass
        
    echo = property(get_echo, set_echo)
    
    def get_invert_echo(self):
        return False
        
    def set_invert_echo(self, invert_echo):
        pass
        
    invert_echo = property(get_invert_echo, set_invert_echo)

    def fade_to_volume(self, volume, duration):
        pass
        
    def get_volume(self):
        return 1.0
        
    def set_volume(self, volume):
        pass
        
    volume = property(get_volume, set_volume)
            
