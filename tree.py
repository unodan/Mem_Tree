from enum import IntEnum
from collections import deque
from config import data as config

const = IntEnum('Constants', 'END START', start=-1)


class Base:
    def __init__(self, data=None, **kwargs):
        self.uri = None

        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.parent = kwargs.get('parent')
        self.columns = kwargs.get('columns')
        if data:
            self.id = data.get('id')
            self.name = data.get('name')
            self.parent = data.get('parent')
            self.columns = data.get('columns')

    @property
    def tree(self):
        item = self
        while not isinstance(item, Tree):
            item = item.parent
        return item

    def get(self, column):
        if not column:
            return self.name
        elif len(self.columns) > column >= 1:
            return self.columns[column-1]

    def set(self, column, value):
        if column < 0 or column > len(self.columns):
            return
        elif not column:
            self.name = value
        else:
            self.columns[column-1] = value

    def path(self, uri=None):
        if not uri:
            parts = [self.name]

            node = self.parent
            while node and node:
                parts.append(node.name)
                node = node.parent
            return '/'.join(list(reversed(parts)))

        item = None
        parts = uri.split('/')
        while parts:
            item = self.tree.query(parts.pop(0)) if isinstance(self, Tree) else self.query(parts.pop(0))
        return item

    def delete(self, item=None):
        node = item if item else self
        idx = node.parent.index(node)
        del node.parent[idx]

    def is_node(self, item=None):
        if not item:
            item = self
        return True if isinstance(item, Node) else False


class Leaf(Base):
    def __init__(self, data=None,  **kwargs):
        super().__init__(data, **kwargs)

    def __len__(self):
        return 0


class Node(Base, deque):
    def __init__(self, data=None, **kwargs):
        Base.__init__(self, data, **kwargs)
        deque.__init__(self)

        if data and 'children' not in data and not isinstance(self, Tree):
            data['children'] = []
            return

    @property
    def children(self):
        return self

    def show(self, parent=None, indent=2, index_pad=4):
        def walk(_parent, level=0):
            if not _parent.is_node():
                return _parent

            for idx, _node in enumerate(_parent):
                pad = '' if not level else ' ' * (indent * level)
                print(f' {str(_node.id).zfill(index_pad)}:{pad} {_node.name}, {_node.columns}')
                if _parent.is_node(_node):
                    walk(_node, level+1)

        print('-----------------------------------------------------')
        print(f'   ID: Name, Columns: {str(self.tree.headings)}')
        print('-----------------------------------------------------')
        walk(parent if parent else self)

    def query(self, query):
        if isinstance(query, int):
            return self.query_by_id(query)
        elif isinstance(query, str):
            return self.query_by_name(query)

    def append(self, item):
        if isinstance(item, Leaf) or isinstance(item, Node):
            super(Node, self).append(item)
            item.id = self.tree.next_id()

    def insert(self, idx, data):
        if idx == int(const.END):
            idx = len(self)
        elif idx < int(const.START):
            idx = int(const.START)

        if isinstance(data, Leaf) or isinstance(data, Node):
            super(Node, self).insert(idx, data)
            data.id = self.tree.next_id()

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

    def populate(self, data, **kwargs):
        self.tree.populate(data, parent=self)

    def get_cell(self, row, column):
        item = self.query(row)
        if item is None:
            return
        elif column:
            return item.get(column)
        else:
            return self.name

    def set_cell(self, row, column, value):
        item = self.query(row)
        if item is None:
            return
        elif column:
            item.set(column, value)
        else:
            item.name = value

    def query_by_id(self, _id):
        def walk(_item):
            if _item.id == _id:
                return _item
            elif not _item.is_node():
                return None

            for child in _item:
                if child.id == _id:
                    return child
                elif child.is_node():
                    _result = walk(child)
                    if _result and _result.id == _id:
                        return child

        for item in self:
            if item.id == _id:
                return item
            elif item.is_node and len(item):
                result = walk(item)
                if result is not None and result.id == _id:
                    return result

    def query_by_name(self, name):
        def walk(_item):
            if _item.name == name:
                return _item
            elif not _item.is_node():
                return None

            for child in _item:
                if child.name == name:
                    return child
                elif child.is_node():
                    _result = walk(child)
                    if _result and _result.name == name:
                        return _result

        for item in self:
            if item.name == name:
                return item
            elif item.is_node and len(item):
                result = walk(item)
                if result is not None and result.name == name:
                    return result


class Tree(Node):
    def __init__(self, data=None):
        self.size = 0
        self.headings = ['Type', 'Size', 'Parent']
        super().__init__()

        self.name = '.'
        self.parent = None
        self.populate(data)

    def next_id(self):
        self.size += 1
        return self.size

    def reindex(self, start=0):
        def walk(_parent):
            for _item in _parent:
                _item.id = self.next_id()
                if _item.is_node():
                    walk(_item)

        self.size = start
        for item in self:
            item.id = self.next_id()
            if item.is_node():
                walk(item)

    def populate(self, data, **kwargs):
        if not data:
            return

        def walk(_parent, _item):
            if 'children' in _item:
                _item['columns'] = ['Node', '0 items', _parent.name]
                item = Node(parent=_parent, **_item)
                if 'children' in _item and len(_item['children']):
                    for node in _item['children']:
                        walk(item, node)
            else:
                _item['columns'] = ['Leaf', '0 Kb', _parent.name]
                item = Leaf(parent=_parent, **_item)
            _parent.append(item)

        parent = kwargs.get('parent', self)
        if isinstance(data, list):
            for cfg in data:
                walk(parent, cfg)


def main():
    t = Tree()
    # Create node with kwargs.
    node = Node(parent=t, name='Test 1', columns=['Node', '0 items', t.name])
    t.append(node)

    leaf = Leaf(parent=t, name='Test 2', columns=['Leaf', '0 Kb', t.name])
    t.append(leaf)

    # Create node with dict.
    node = Node({'parent': t, 'name': 'Test 3', 'columns': ['Node', '0 items', t.name]})
    t.append(node)

    node = Node(parent=t, name='Test 4', columns=['Node', '0 items', t.name])
    t.append(node)

    node = Node(parent=t, name='Test 5', columns=['Node', '0 items', t.name])
    t.append(node)

    leaf = Leaf(parent=node, name='Leaf 5-1', columns=['Leaf', '0 Kb', node.name])
    node.append(leaf)

    t.show()

    cfg = [{
        'name': 'Node 1a',
        'children': [
            {
                'name': 'Leaf 1a',
            },
            {
                'name': 'Node 1a-1',
                'children': [],
            },
            {
                'name': 'Leaf 2a',
            },
            {
                'name': 'Sub Node 1a',
                'children': [
                    {
                        'name': 'Sub Leaf 1a',
                    },

                    {
                        'name': 'Leaf 1a',
                    },
                    {
                        'name': 'Node 1a-1',
                        'children': [],
                    },
                    {
                        'name': 'Leaf 2a',
                    },
                    {
                        'name': 'Sub Node 1a',
                        'children': [
                            {
                                'name': 'Sub Leaf 1a',
                            },
                        ]
                    },
                ]
            },
        ],
    }]

    t = Tree(cfg)
    t.show()

    t[0][1].populate(cfg)
    t.show()

    item = Node({'name': 'Test Node 1', 'columns': ['Node', '0 items', t[0].name]})
    t[0].insert(1, item)

    item = Leaf({'name': 'Test Leaf 1', 'columns': ['Leaf', '0 Kb', t[0].name]})
    t[0].insert(1, item)

    item = Leaf({'name': 'Test Leaf 2', 'columns': ['Leaf', '0 Kb', t.name]})
    t.append(item)

    t.reindex()
    t.show()

    print('------------------------------------------------------')

    t = Tree(config)
    t.show()

    item = t.path('Node One/Node Three')
    print(item.name, item.path())
    item = item.path('Node One/Node Three/Node Four/Leaf Four')
    print(item.name, item.path())

    print('------------------------------------------------------')


if __name__ == '__main__':
    main()
