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


class ItemBase:
    def __init__(self):
        super().__init__()
        self.name = None
        self.parent = None

    @property
    def tree(self):
        item = self
        while item.parent:
            item = item.parent
        return item

    def delete(self, item=None):
        node = item if item else self
        idx = node.parent.index(node)
        del node.parent[idx]

    def is_node(self, item=None):
        if not item:
            item = self
        return True if isinstance(item, Node) else False


class Leaf(ItemBase):
    def __init__(self, data):
        super().__init__()
        if 'name' in data:
            self.name = data['name']

    def __len__(self):
        return len(self.name)


class Node(ItemBase, deque):
    def __init__(self, data=None):
        deque.__init__(self)
        ItemBase.__init__(self)

        if data:
            self.populate(data)

    def dump(self, parent=None, file=None, indent=3):
        if not parent:
            parent = self

        def walk(_parent, level=0):
            for _node in _parent:
                pad = '' if not level else ' ' * indent * level
                print(pad, _node.name)
                if _parent.is_node(_node):
                    walk(_node, level+1)

        walk(parent)

    def append(self, data):
        idx = len(self)
        super(Node, self).append(data)
        self[idx].parent = self

    def insert(self, idx, data):
        if idx == END:
            idx = len(self)
        elif idx < START:
            idx = START

        super(Node, self).insert(idx, data)
        self[idx].parent = self

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
            item = Leaf(cfg) if 'children' not in cfg else Node(cfg.pop('children', ()))
            item.name = cfg['name']
            item.parent = self
            self.append(item)

    def get_by_name(self, name):
        for c in self:
            if c.name == name:
                return c


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

    t = Tree(cfg)
    t.dump()


if __name__ == '__main__':
    main()
