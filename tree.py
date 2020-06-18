from collections import deque, OrderedDict

END = -1
START = 0


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


class Leaf:
    def __init__(self, parent, data):
        super().__init__()
        self.name = None
        self.parent = parent

    @property
    def tree(self):
        parent = self.parent

        while parent:
            parent = parent.parent

        if not parent:
            parent = self
        return parent

    def delete(self, item=None):
        node = item if item else self
        idx = node.parent.index(node)
        del node.parent[idx]

    def is_node(self, item=None):
        if not item:
            item = self
        return True if isinstance(item, Node) else False


class Node(deque, Leaf):
    def __init__(self, x=None, data=None):
        deque.__init__(self)
        Leaf.__init__(self, x, data)

        if data:
            self.populate(data)

    def dump(self, parent=None, indent=3):
        if not parent:
            parent = self

        def walk(_parent, level=0):
            for _node in _parent:
                pad = '' if not level else ' ' * indent * level
                print(pad, _node.name, _node.parent.name)
                if _parent.is_node(_node):
                    walk(_node, level+1)

        walk(parent)

    def append(self, data):
        super(Node, self).append(data)
        # print(id(self.tree), type(self.tree), self[len(self)-1].name)

    def insert(self, idx, data):
        if idx == END:
            idx = len(self)
        elif idx < 0:
            idx = 0
        super(Node, self).insert(idx, data)

    def to_list(self, parent=None):
        def get_data(_item, _data):
            for node in _item:
                _item_data = {'name': node.name}
                _data.append(_item_data)
                if node.is_node():
                    _item_data['children'] = []
                    get_data(node, _item_data['children'])

        data = []
        parent = parent if parent else self
        for item in parent:
            if item.is_node():
                item_data = {'name': item.name, 'children': []}
                data.append(item_data)
                get_data(item, item_data['children'])
            else:
                item_data = {'name': item.name}
                data.append(item_data)
        return data

    def populate(self, config):
        for cfg in config:
            item = Leaf(self, cfg) if 'children' not in cfg else Node(self, cfg.pop('children', ()))
            item.name = cfg['name']
            self.append(item)

    def get_by_name(self, name):
        for c in self:
            if c.name == name:
                return c


class Tree(Node):
    def __init__(self, data=None):
        super().__init__(None, data)
        self.size = 0
        self.name = '.'

    def next_id(self):
        idx = self.size
        self.size += 1
        return idx


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

    t = Tree(cfg)
    # t.dump()

    # print(t[0][1][0].parent.name, len(t))


if __name__ == '__main__':
    main()
