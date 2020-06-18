from collections import deque
import config

END = -1
START = 0


class Leaf:
    def __init__(self, data):
        super().__init__()
        self.id = None
        self.parent = None
        self.name = data['name'] if isinstance(data, dict) else data[0]['name']

    @property
    def tree(self):
        parent = self
        while parent:
            if not parent.parent:
                break
            parent = parent.parent
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
    def __init__(self, data=None):
        Leaf.__init__(self, data)
        deque.__init__(self)

        if data:
            self.populate(data)

    def show(self, parent=None, indent=3):
        def walk(_parent, level=0):
            for _node in _parent:
                pad = '' if not level else ' ' * (indent * level)
                if _node.parent:
                    print(f'{_node.id}   {pad}', _node.name)
                if _parent.is_node(_node):
                    walk(_node, level+1)

        if not parent:
            parent = self
        print('-----------------------------------------------------')
        print('ID : Name')
        print('-----------------------------------------------------')
        walk(parent)
        print('-----------------------------------------------------')

    def append(self, data):
        super(Node, self).append(data)
        item = self[len(self)-1]
        item.id = self.tree.next_id()
        item.parent = self

    def insert(self, idx, data):
        if idx == END:
            idx = len(self)
        elif idx < 0:
            idx = 0
        super(Node, self).insert(idx, data)
        item = self[idx]
        item.id = self.tree.next_id()
        item.parent = self

    def to_list(self, parent=None):
        def set_data(_item, _data):
            for node in _item:
                _item_data = {'name': node.name}
                _data.append(_item_data)
                if node.is_node():
                    _item_data['children'] = []
                    set_data(node, _item_data['children'])

        data = []
        parent = parent if parent else self
        for item in parent:
            if item.is_node():
                item_data = {'name': item.name, 'children': []}
                data.append(item_data)
                set_data(item, item_data['children'])
            else:
                item_data = {'name': item.name}
                data.append(item_data)
        return data

    def populate(self, data):
        for cfg in data:
            item = Node(cfg.pop('children', ())) if 'children' in cfg else Leaf(cfg)
            item.parent = self
            item.name = cfg['name']
            super(Node, self).append(item)

    def get(self, query):
        if isinstance(query, int):
            return self.get_by_id(query)
        elif isinstance(query, str):
            return self.get_by_name(query)

    def get_by_id(self, _id):
        def walk(_item):
            if _item.id == _id:
                return _item

            if not _item.is_node():
                return

            for child in _item:
                if child.is_node():
                    _result = walk(child)
                    if _result:
                        return _result
                elif child.id == _id:
                    return child

        for item in self:
            result = walk(item)
            if result:
                return result

    def get_by_name(self, name):
        def walk(_item):
            if _item.name == name:
                return _item

            if not _item.is_node():
                return

            for child in _item:
                if child.is_node():
                    _result = walk(child)
                    if _result:
                        return _result
                elif child.name == name:
                    return child

        for item in self:
            result = walk(item)
            if result:
                return result


class Tree(Node):
    def __init__(self, data=None):
        super().__init__(data)
        self.size = 0
        self.name = '.'
        self.reindex()

    def next_id(self):
        self.size += 1
        return self.size

    def reindex(self, start=0):
        def walk(_parent, level=0):
            for _node in _parent:
                _node.id = self.next_id()
                if _parent.is_node(_node):
                    walk(_node, level+1)

        self.size = start
        walk(self)


def main():
    t = Tree(config.data)
    t.show()


if __name__ == '__main__':
    main()
