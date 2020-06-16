from collections import deque


cfg = (
    {
        'text': 'Node 1',
        'children': (
            {
                'text': 'Leaf n1'
            },
            {
                'text': 'Node 1-1',
                'children': (
                    {
                        'text': 'Leaf 1-1'
                    },
                    {
                        'text': 'Leaf 1-2'
                    },
                )
            },
        )
    },
    {
        'text': 'Leaf 1',
    },
    {
        'text': 'Leaf 2',
    },
)


class Leaf:
    def __init__(self, parent, data):
        super().__init__()
        self._parent = parent
        self.name = data['text']

    def index(self, item, start=None, stop=None):
        return self._parent.index(item)

    def parent(self):
        return self._parent


class Node(deque):
    def __init__(self, parent, data):
        super().__init__()
        self.name = None
        self._parent = parent
        self.children = deque()

        self.populate(data)

    def __len__(self):
        return len(self.children)

    @staticmethod
    def is_node(item):
        return True if isinstance(item, Node) else False

    @staticmethod
    def has_children(item):
        return True if 'children' in item else False

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

    def prev(self, item):
        idx = self.index(item) - 1
        if idx >= 0:
            return self.children[idx]
        return self

    def next(self, item):
        idx = self.index(item) + 1
        if idx >= len(self) or idx < 0:
            idx = 0

        return self.children[idx]

    def index(self, item, start=None, stop=None):
        return self.children.index(item)

    def populate(self, config):
        for item in config:
            if 'children' in item:
                n = Node(self, item.pop('children', ()))
                n.name = item['text']
                self.children.append(n)
            else:
                self.children.append(Leaf(self, item))

    def get_children(self, parent=None):
        if not parent:
            return self.children


class Tree(Node):
    def __init__(self, data):
        super().__init__(None, data)
        self.name = '.'

    def parent(self, item=None):
        parent = self if not item else item.parent()
        return parent


def main():
    t = Tree(cfg)
    t.dump()

    print('-------------------------------')

    for i in t.get_children():
        print(111, i.name, t.index(i), t.next(i).name)

        if t.is_node(i):
            for j in i.get_children():
                print(j.name, i.index(j), i.next(j).name)


if __name__ == '__main__':
    main()
