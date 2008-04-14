behaviours = []
import pypoujol
from script import is_derived_from

class BehaviourFoo(object):
    pass
    
class BehaviourMetaClass(pypoujol.SceneMetaClass, pypoujol.AnimationMetaClass, pypoujol.GameMetaClass):
    def __init__(self, name, bases, dict):
        append = True
        for i in bases:
            if not is_derived_from(i, BehaviourFoo):
                append = False
                break
        if bases[0].__bases__[0] != BehaviourFoo:
            append = False
        if append:
            behaviours.append(name)
        super(type, self).__init__(name, bases, dict)

class Behaviour(BehaviourFoo):
    __metaclass__ = BehaviourMetaClass
    
    def __init__(self):
        pass

class Blinking(Behaviour):
    apply_on = "Scene"
    
    def __init__(self):
        self.blinking = True
