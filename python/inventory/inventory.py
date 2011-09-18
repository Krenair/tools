"API for the SR inventory"
import os, sys, re, yaml
import assetcode, codecs

RE_ASSY = re.compile( "^(.+)-assy-sr([%s]+)$" % "".join(assetcode.alphabet_lut) )
RE_PART = re.compile( "^(.+)-sr([%s]+)$" % "".join(assetcode.alphabet_lut) )

def should_ignore(path):
    "Return True if the path should be ignored"
    if path[0] == ".":
        return True

    if path[-1] == "~":
        return True

    return False

class Item(object):
    "An item in the inventory"
    def __init__(self, path):
        self.path = path
        m = RE_PART.match(os.path.basename(path))
        self.name = m.group(1)
        self.code = m.group(2)

        # Load data from yaml file
        self.yaml = yaml.load( codecs.open(path, "r", encoding="utf-8") )

        # TODO: Verify that assetcode matches filename


class ItemAssembly(Item):
    "An assembly"
    def __init__(self, path):
        self.path = path
        self.children = {}
        self._find_children()

        m = RE_ASSY.match(os.path.basename(path))
        self.name = m.group(1)
        self.code = m.group(2)

        # Load info from 'info' file
        self.yaml = yaml.load( codecs.open( os.path.join( path, "info" ),
                                            "r", encoding="utf-8") )

    def _find_children(self):
        for fname in os.listdir(self.path):
            if should_ignore(fname):
                continue
            if fname == "info":
                "The info file is not a child"
                continue

            p = os.path.join(self.path, fname)

            i = Item(p)
            self.children[i.code] = p

class ItemTree(object):
    def __init__(self, path):
        self.name = os.path.basename(path)
        self.path = path
        self.children = {}
        self._find_children()

    def _find_children(self):
        for fname in os.listdir(self.path):
            if should_ignore(fname):
                continue
            p = os.path.join(self.path, fname)

            if os.path.isfile(p):
                "It's got to be an item"
                i = Item(p)
                self.children[i.code] = i

            elif os.path.isdir(p):
                "Could either be an assembly or a collection"

                if RE_ASSY.match(p) != None:
                    a = ItemAssembly(p)
                    self.children[a.code] = a
                else:
                    t = ItemTree(p)
                    self.children[t.name] = t

    def walk(self):
        pass

class Inventory(object):
    def __init__(self, rootpath):
        self.rootpath = rootpath
        self.root = ItemTree(rootpath)