import inventory
import fnmatch

class NonTerminal(object):
    pass

class Terminal(object):
    pass

class Not(NonTerminal):
    def __init__(self, node):
        super(Not, self).__init__()
        self.node = node

    def match(self, inv_node):
        return not self.node.match(inv_node)

    def sexpr(self):
        return "(NOT {0})".format(self.node.sexpr())


class And(NonTerminal):
    def __init__(self, left, right):
        super(And, self).__init__()
        self.left = left
        self.right = right

    def match(self, inv_node):
        return self.left.match(inv_node) and self.right.match(inv_node)

    def sexpr(self):
        return "(AND {0} {1})".format(self.left.sexpr(), self.right.sexpr())


class Or(NonTerminal):
    def __init__(self, left, right):
        super(Or, self).__init__()
        self.left = left
        self.right = right

    def match(self, inv_node):
        return self.left.match(inv_node) or self.right.match(inv_node)

    def sexpr(self):
        return "(OR {0} {1})".format(self.left.sexpr(), self.right.sexpr())


class Condition(Terminal):
    def __init__(self, *conditions):
        super(Condition, self).__init__()
        self.conditions = set(conditions)

    def _flatten(self, l):
        if type(l) not in (list, tuple):
           return l
        ret = []
        for i in l:
            if type(i) in (list, tuple):
                ret.extend(self._flatten(i))
            else:
                ret.append(i)
        return ret

    def _state(self, inv_node):
        if isinstance(inv_node, inventory.Item):
            return inv_node.condition

        elif isinstance(inv_node, inventory.ItemGroup):
            expected = inv_node.elements
            if expected is None:
                return 'working'
            ret = []
            for name in expected:
                count = 1
                if type(name) == dict:
                    count = name.values()[0]
                    name = name.keys()[0]
                if not name in inv_node.types:
                    ret.append('broken')
                if name in inv_node.types:
                    c = 0
                    for type_ in inv_node.types[name]:
                        if c == count:
                            break
                        ret.append(self._state(type_))
                        c += 1
                    if c != count:
                        ret.append('broken')
                else:
                    ret.append('broken')
            ret = set(self._flatten(ret))
            if len(ret) == 1:
                return ret.pop()
            if 'broken' in ret:
                return 'broken'
            return 'unknown'

    def match(self, inv_node):
        return self._state(inv_node) in self.conditions

    def sexpr(self):
        return "(Condition {0})".format(list(self.conditions))


class Type(Terminal):
    def __init__(self, *types):
        super(Type, self).__init__()
        self.types = types

    def match(self, inv_node):
        if hasattr(inv_node, 'name'):
            for type in self.types:
                if fnmatch.fnmatch(inv_node.name, type):
                    return True
        return False

    def sexpr(self):
        return "(Type {0})".format(list(self.types))


class Labelled(Terminal):
    def __init__(self, labelled):
        super(Labelled, self).__init__()
        self.labelled = labelled.lower() in ('true', '1')

    def match(self, inv_node):
        if hasattr(inv_node, 'labelled'):
            return inv_node.labelled == self.labelled
        return False

    def sexpr(self):
        return "(Labelled {0})".format(self.labelled)


class Path(Terminal):
    def __init__(self, *paths):
        super(Path, self).__init__()
        self.paths = [path[1:] if path[0] == '/' else path for path in paths]

    def _root_path(self, inv_node):
        n = inv_node
        while n is not None:
            if n.parent is None:
                return n.path
            n = n.parent

    def match(self, inv_node):
        if hasattr(inv_node, 'path'):
            for path in self.paths:
                if inv_node.path[len(self._root_path(inv_node))+1:].startswith(path):
                    return True
        return False

    def sexpr(self):
        return "(Path {0})".format(list(self.paths))


class Code(Terminal):
    def __init__(self, *codes):
        self.codes = set(map(self._tidy, codes))

    def _tidy(self, code):
        code = code.upper()
        if code.startswith('SR'):
            code = code[2:]
        return code

    def match(self, inv_node):
        return inv_node.code in self.codes

    def sexpr(self):
        return "(Code {0})".format(list(self.codes))

