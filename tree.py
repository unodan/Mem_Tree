from collections import deque

END = -1


class Leaf:
    def __init__(self, data):
        super().__init__()
        self._parent = None
        if 'name' in data:
            self.name = data['name']

    def __len__(self):
        return len(self.name)

    def __str__(self):
        return self.name

    def parent(self):
        return self._parent


class Node(deque):
    def __init__(self, data=None):
        super().__init__()
        self.name = None
        self._parent = None

        if data:
            self.populate(data)

    def __str__(self):
        return self.name

    @staticmethod
    def is_node(item):
        return True if isinstance(item, Node) else False

    def prev(self, item=None):
        if self._parent:
            parent = self._parent
        else:
            parent = self

        items = list(parent)
        idx = 0 if not item else items.index(item)-1

        if not idx and self._parent:
            idx = items.index(self)-1
            if idx >= 0:
                return items[idx]

        if 0 <= idx < len(self) and item:
            return items[idx]

    def next(self, item=None):
        if self._parent:
            parent = self._parent
        else:
            parent = self

        items = list(parent)
        idx = 0 if not item else items.index(item)+1
        if idx < len(self):
            return items[idx]

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

    def insert(self, idx, data):
        if idx == END:
            idx = len(self)
        return super(Node, self).insert(idx, data)

    def parent(self):
        return self._parent

    def populate(self, config):
        for item in config:
            if 'children' in item:
                n = Node(item.pop('children', ()))
                n.name = item['name']
                n._parent = self
                self.append(n)
            else:
                leaf = Leaf(item)
                leaf._parent = self
                self.append(leaf)

    def get_children(self):
        return list(self)

    def get_by_name(self, name):
        for c in self:
            if c.name == name:
                return c
            if self.is_node(c):
                return c.get_by_name(name)


class Tree(Node):
    def __init__(self, data=None):
        super().__init__(data)
        self.name = '.'


def main():
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

    print('-------------------------------')
    t = Tree()
    leaf = Leaf({'name': 'My Leaf'})
    t.insert(0, leaf)
    print(t.next())

    print('-------------------------------')
    t = Tree(cfg)
    print(t.parent())
    print('-------------------------------')
    t.dump()
    print('-------------------------------')
    leaf = Leaf({'name': 'My New Leaf'})
    print(leaf)
    print('parent->', leaf.parent(), '( . is the root of the tree)')
    print('-------------------------------')
    print(1, t.prev())
    print(2, t.next())
    print(3, t.next(t.next()))
    print(4, t.next(t.next(t.next())))
    print(5, t.next(t.next(t.next(t.next()))))
    print(6, t.prev(t.next(t.next())))
    print(7, t.prev(t.next(t.next(t.next()))))
    x = t.get_by_name('Node 1').get_by_name('Node 1-1')
    print(8, f'{x.name}, {x.prev()}')
    print(9, f'{x.name}, {x.parent()}')
    x.insert(1, leaf)
    print('-------------------------------')

    parent = t.get_by_name('Node 1').get_by_name('Node 1-1')

    leaf = Leaf({'name': 'Leaf Insert Test'})
    parent.insert(END, leaf)

    t.dump()


if __name__ == '__main__':
    main()
