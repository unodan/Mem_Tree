from collections import deque


def dump(data, indent=None):
    indent = indent if indent else '.'

    print('-------------------------------------------------------------------------------------------------------')
    if data:
        def walk(_data, count):
            count += 1
            for key, value in _data.items():
                if isinstance(value, dict):
                    print(indent * count, key)
                    walk(value, count)
                else:
                    if isinstance(value, str):
                        value = f'"{value}"'
                    print(indent * count, key, f'value={value}')

        walk(data, 0)
    else:
        print(' (No Data)')

    print('-------------------------------------------------------------------------------------------------------')


cfg1 = (
    {
        'text': 'node 1',
        'children': (
            {
                'text': 'node 2',
                'children': (
                    {'text': 'testing s1'},
                ),
            },
        )
    },
)


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

START = 0
END = -1


def has_nodes(obj):
    if 'children' in obj:
        return True
    return False


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
