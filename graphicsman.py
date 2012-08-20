"""Graphics manager. Organizes retrieving of different graphics from different
graphics or tile sets."""


import os
import yaml
import image

class hset (set, yaml.YAMLObject):
    """hset: hashable version of set. Can be used as dictionary keys."""
    yaml_tag = "!hset"
    def __init__(self, iterable=[]):
        set.__init__(self, iterable)
    def __hash__(self):
        li = list(self)
        li.sort()
        return hash(tuple(li))

    @staticmethod
    def from_yaml(loader, vals):
        print "hset.from_yaml:"
        print vals
        if len(vals.value)>0:
            return hset(map(lambda x : str(x.value), vals.value))
        else:
            return hset([])
        

class GraphicsMan (yaml.YAMLObject):
    """Graphics Set Manager class.
See loadfile()"""
    yaml_tag = "!GraphicsMan"
    def __init__(self):
        self.set_basedir = ''
        self.set_title = ''
        self.set_specfile = ''
        
        #self.gmap = { 'dummy': {hset():('dummy.png',(0,0,64,64))} }
        self.gmap = {}
    
    def get(self, name, state=hset()):
        """usage:
get(graphic_name, state_set)
get((graphic_name, state_set,))
get((graphic_name, state_str1, state_str2, ...))"""
        #check in which one of the styles it was called:
        if type(name)==tuple:
            tu = name
            name = tu[0]
            if len(tu)==2:
                state = hset(tu[1])
            elif len(tu)>2:
                state = hset(tu[1:])

        if type(name) is not str:
            name = str(name)
        if type(state) is not hset:
            state = hset(state)

        if name not in self.gmap:
            #try returning a dummy graphic if no graphic found
            name = 'dummy'

        if state not in self.gmap[name]:
            #default to the base state
            state = hset() #TODO: look for the best partial state match?
        
        filename, rect = self.gmap[name][state]
        return image.get(os.path.join(self.set_basedir, filename), rect=rect)
    
    #def add(self, name, state, filename, rect):
    #    if not name in self.gmap: self.gmap[name]={}
    #    self.gmap[name][state] = (filename, rect)


    @classmethod
    def loadfile(self, filename):
        """Return a new instance of GraphicsMan, correctly loaded from a spec file.
Use this instead of yaml.load, as this function sets the set_basedir appropriately."""
        contents = file(filename, 'r').read()
        new = yaml.load(contents)
        
        new.set_basedir = os.path.abspath(os.path.dirname(filename))
        new.set_specfile = filename
        return new
    
    #for yaml to load:
    def __setstate__(self, dic):
        self.set_title = dic['title']
        self.gmap = {}
        for name, states in dic['images'].items():
            self.gmap[name] = {}
            for state, spec in states.items():
                if not(state) or state=='None':
                    state = hset()
                if type(state)==str:
                    state = hset(state)
                filename = spec[0]
                rect = tuple(spec[1:5])
                self.gmap[name][state] = (filename, rect)



if __name__ == "__main__":

    gm = GraphicsMan.loadfile("images/tilesets/isometric/default/spec.yaml")

    print gm.gmap

    print 'testing:'
    print gm.get('pc')

