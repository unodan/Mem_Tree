from collections import deque


cfg = (
    {
        'name': 'Node 1',
        'children': (
            {
                'name': 'Leaf n1'
            },
            {
                'name': 'Node 1-1',
                'children': (
                    {
                        'name': 'Leaf 1-1'
                    },
                    {
                        'name': 'Leaf 1-2'
                    },
                )
            },
        )
    },
    {
        'name': 'Leaf 1',
    },
    {
        'name': 'Leaf 2',
    },
)


def has_children(_dict):
    return True if 'children' in _dict else False


class Leaf:
    def __init__(self, parent, data):
        super().__init__()
        self._parent = parent
        if 'name' in data:
            self.name = data['name']

    def __len__(self):
        return len(self.name)

    def __str__(self):
        return self.name

    def index(self, item, start=None, stop=None):
        return self._parent.index(item)

    def parent(self):
        return self._parent

    def prev(self, item=None):
        idx = self.index(item) - 1
        if idx >= 0:
            return idx
        else:
            return

    def next(self, item=None):
        if not item:
            item = self
        idx = self.index(item) + 1

        if idx >= len(self.parent()) or idx < 0:
            idx = 0
            if self.index(self) <= len(self.parent()):
                return self.parent().children[idx+1]

        return self.parent().children[idx+1]


class Node(deque):
    def __init__(self, parent, data):
        super().__init__()
        self.name = None
        self._parent = parent
        self.children = deque()

        self.populate(data)

    def __len__(self):
        return len(self.children)

    def __str__(self):
        return self.name

    @staticmethod
    def is_node(item):
        return True if isinstance(item, Node) else False

    def dump(self, parent=None, indent=3):
        if not parent:
            parent = self

        def walk(_parent, level=0):
            for _node in _parent.get_children():
                pad = '' if not level else ' ' * indent * level
                print(pad, _node.name)
                if _parent.is_node(_node):
                    walk(_node, level+1)

        walk(parent)

    def prev(self, item=None):
        if not item:
            return self

        idx = item.index(item) - 1
        if idx < 0:
            return None

        return self.children[idx]

    def next(self, item=None):
        if not item:
            item = self

        idx = item.index(item) + 1
        if idx >= len(self) or idx < 0:
            return None

        return self.children[idx]

    def index(self, item, start=None, stop=None):
        return self.children.index(item)

    def populate(self, config):
        for item in config:
            if 'children' in item:
                n = Node(self, item.pop('children', ()))
                n.name = item['name']
                self.children.append(n)
            else:
                self.children.append(Leaf(self, item))

    def get_children(self, parent=None):
        if not parent:
            return self.children

    def append(self, *args, **kwargs):
        self.children.append(*args, **kwargs)

    def get_by_name(self, name):
        for c in self.children:
            if c.name == name:
                return c
            if self.is_node(c):
                return c.get_by_name(name)


class Tree(Node):
    def __init__(self, data):
        super().__init__(None, data)
        self.name = '.'

    def parent(self, item=None):
        parent = self if not item else item.parent()
        return parent

    def insert(self, parent=None, index=-1, **data):
        if not parent:
            parent = self

        if has_children(data):
            print(11111)
        else:
            leaf = Leaf(self, data)
            if index == -1:
                return parent.append(leaf)
            elif parent.name == '.':
                self.children.insert(index, leaf)


def main():
    t = Tree(cfg)
    print('-------------------------------')
    t.dump()
    print('-------------------------------')
    t.insert(index=2, **{'name': 'Leaf 3'})
    t.dump()
    print('-------------------------------')

    print(1, t.next().name)
    print(2, t.next(t.next()).name)
    print(3, t.next(t.next(t.next())).name)
    print(4, t.next(t.next(t.next(t.next()))))
    print('-------------------------------')
    print(1, t.next(t.prev()).name)
    print(2, t.prev().name)

    x = t.get_by_name('Node 1')
    x = t.get_by_name('Node 1').get_by_name('Node 1-1')

    print(x.name)


if __name__ == '__main__':
    main()
