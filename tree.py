from collections import deque, OrderedDict
import setup

END = -1
START = 0


class Leaf:
    def __init__(self, parent, data):
        super().__init__()
        self.name = None
        self.name = data['name'] if isinstance(data, dict) else data[0]['name']
        self.parent = parent

    @property
    def tree(self):
        parent = self.parent
        print(1111, self.name, id(self.parent), type(self.parent))
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


class Node(Leaf, deque):
    def __init__(self, parent, data=None):
        Leaf.__init__(self, parent, data)
        deque.__init__(self)

        if data:
            self.populate(data)

    def dump(self, parent=None, indent=3):
        def walk(_parent, level=0):
            for _node in _parent:
                pad = '' if not level else ' ' * (indent * level)
                if _node.parent:
                    print(pad, _node.name, _node.parent.name)
                if _parent.is_node(_node):
                    walk(_node, level+1)

        if not parent:
            parent = self
        print('-----------------------------------------------------')
        walk(parent)
        print('-----------------------------------------------------')

    def append(self, data):
        self.tree
        super(Node, self).append(data)

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
            item.parent = self
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
    t = Tree(setup.config)
    t.dump()

    # print(t[0][1][0].parent.name, len(t))


if __name__ == '__main__':
    main()
