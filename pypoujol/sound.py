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
            
