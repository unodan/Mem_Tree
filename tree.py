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

    def parent(self):
        return self._parent


class Node(deque):
    def __init__(self, parent, data):
        super().__init__()
        self.name = None
        self._parent = parent

        self.populate(data)

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
        if self._parent:
            parent = self._parent
        else:
            parent = self

        items = list(parent)
        idx = 0 if not item else items.index(item) - 1
        if idx < len(self):
            return items[idx]

    def next(self, item=None):
        if self._parent:
            parent = self._parent
        else:
            parent = self

        items = list(parent)
        idx = 0 if not item else items.index(item) + 1
        if idx < len(self):
            return items[idx]

    def populate(self, config):
        for item in config:
            if 'children' in item:
                n = Node(self, item.pop('children', ()))
                n.name = item['name']
                self.append(n)
            else:
                self.append(Leaf(self, item))

    def get_children(self):
        return list(self)

    def get_by_name(self, name):
        for c in self:
            if c.name == name:
                return c
            if self.is_node(c):
                return c.get_by_name(name)

    def insert(self, idx, data):
        return super(Node, self).insert(idx, data)


class Tree(Node):
    def __init__(self, data):
        super().__init__(None, data)
        self.name = '.'

    def parent(self, item=None):
        parent = self if not item else item.parent()
        return parent


def main():
    t = Tree(cfg)
    print('-------------------------------')
    t.dump()
    print('-------------------------------')
    leaf = Leaf(t, {'name': 'Leaf 333333333'})
    print(1, leaf, leaf.parent())
    print('-------------------------------')
    print(2, t.next())
    print('-------------------------------')
    print(3, t.next())
    print(4, t.next(t.next()))
    print(5, t.next(t.next(t.next())))
    print(6, t.next(t.next(t.next(t.next()))))
    print(7, t.prev().name)
    print(8, t.prev(t.next(t.next(t.next()))))
    print('-------------------------------')
    x = t.get_by_name('Node 1').get_by_name('Node 1-1')
    print(9, x.name)
    print('-------------------------------')

    parent = t.get_by_name('Node 1').get_by_name('Node 1-1')
    leaf = Leaf(parent, {'name': 'Leaf 3'})
    t.get_by_name('Node 1').get_by_name('Node 1-1').insert(0, leaf)
    print('-------------------------------')
    t.dump()


if __name__ == '__main__':
    main()
