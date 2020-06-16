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
                print(pad, _node.text)
                if _parent.is_node(_node):
                    walk(_node, level+1)

        walk(parent)

    def populate(self, config):
        for item in config:
            if 'children' in item:
                n = Node(self, item.pop('children', ()))
                n.text = item['text']
                self.children.append(n)
            else:
                self.children.append(Leaf(self, item))

    def get_children(self, parent=None):
        if not parent:
            return self.children


class Tree(Node):
    def __init__(self, data):
        super().__init__(None, data)


def main():
    t = Tree(cfg)
    t.dump()


if __name__ == '__main__':
    main()
