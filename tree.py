from collections import deque


cfg = (
    {
        'text': 'Node 1',
        'children': (
            {
                'text': 'Leaf n1'
            },
            {
                'text': 'Leaf n2'
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
        self.parent = parent
        self.text = data['text']


class Node(deque):
    def __init__(self, parent, data):
        super().__init__()
        self.text = None
        self.parent = parent
        self.children = deque()

        self.populate(data)

    def __len__(self):
        return len(self.children)

    @staticmethod
    def has_children(item):
        return True if 'children' in item else False

    @staticmethod
    def is_node(item):
        return True if isinstance(item, Node) else False

    def populate(self, data):
        for itm in data:
            if 'children' in itm:
                self.text = itm['text']
                n = Node(self, itm.pop('children', ()))
                n.text = itm['text']
                self.children.append(n)
            else:
                self.children.append(Leaf(self, itm))

    def get_children(self, parent=None):
        if not parent:
            return self.children


class Tree(Node):
    def __init__(self, data):
        super().__init__(None, data)


def main():
    t = Tree(cfg)
    for x in t.get_children():
        if t.is_node(x):
            print(x.text)
            for c in x.get_children():
                print('\t', c.text)
        else:
            print(x.text)


if __name__ == '__main__':
    main()
