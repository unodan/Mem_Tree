from enum import IntEnum
from collections import deque
from datetime import datetime
from config import data as config
from copy import deepcopy

const = IntEnum('Constants', 'END START', start=-1)


class Base:
    def __init__(self, data=None, **kwargs):
        self.uri = None

        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.parent = kwargs.get('parent')
        self.columns = kwargs.get('columns', [])
        if data:
            self.id = data.get('id')
            self.name = data.get('name')
            self.parent = data.get('parent')
            self.columns = data.get('columns', [])

    @property
    def tree(self):
        item = self
        while not isinstance(item, Tree):
            item = item.parent
        return item

    @staticmethod
    def copy(src, dst):
        dst.append(deepcopy(src))

    def get(self, columns=None):
        if columns is None:
            columns = tuple(range(0, len(self.tree.headings)+1))
        elif not isinstance(columns, tuple):
            columns = (columns, )

        data = []
        for column in columns:
            if column < 0 or column > len(self.columns):
                continue
            elif not column:
                data.append(self.name)
            elif 0 < column < len(self.columns)+1:
                data.append(self.columns[column-1])

        return data[0] if len(data) == 1 else tuple(data) if data else None

    def set(self, columns, values):
        if not isinstance(columns, tuple):
            columns = (columns, )
        if not isinstance(values, tuple):
            values = (values, )

        for column, value in dict(zip(columns, values)).items():
            if column < 0 or column > len(self.columns):
                continue
            elif not column:
                self.name = value
            else:
                self.columns[column-1] = value

    def path(self, uri=None):
        if uri and uri.startswith('.'):
            uri = uri.lstrip('.')

        if not uri:
            parts = [self.name] if not isinstance(self.parent, Tree) else ['']

            node = self.parent
            while node and node:
                parts.append(node.name)
                node = node.parent

            return '/'.join(list(reversed(parts))).lstrip('.')

        item = None
        parts = uri.split('/')
        while parts:
            if isinstance(self, Tree):
                item = self.tree.query(parts.pop(0))
            elif isinstance(self, Node):
                item = self.query(parts.pop(0))
            else:
                item = self.query(parts.pop(0))

        return item

    def query(self, query):
        node = self if not isinstance(self, Tree) else self.tree

        if isinstance(query, int):
            return node.query_by_id(query)
        elif isinstance(query, str):
            if '/' in query:
                return self.path(query)
            else:
                return self.tree.query_by_name(query)

    def delete(self, item=None):
        node = item if item else self
        idx = node.parent.index(node)
        del node.parent[idx]

    def is_node(self, item=None):
        if item is None:
            item = self
        return True if isinstance(item, Node) else False


class Leaf(Base):
    def __init__(self, data=None,  **kwargs):
        super().__init__(data, **kwargs)
        self.type = 'Leaf'

    def __len__(self):
        return None


class Node(Base, deque):
    def __init__(self, data=None, **kwargs):
        Base.__init__(self, data, **kwargs)
        deque.__init__(self)
        self.type = 'Node'

    @property
    def children(self):
        return self

    def show(self, parent=None, indent=2, index_pad=4):
        def walk(_parent, level=0):
            if not _parent.is_node():
                return _parent

            for idx, _node in enumerate(_parent):
                pad = '' if not level else ' ' * (indent * level)
                columns = '' if not _node.columns else f', {str(_node.columns)}'
                print(f' {str(_node.id).zfill(index_pad)}:{pad} {_node.name}{columns}')
                if _parent.is_node(_node):
                    walk(_node, level+1)

        header_postfix = f', Columns: {str(self.tree.headings)}' if self.tree.headings else ''
        print('-----------------------------------------------------')
        print(f'   ID: Name{header_postfix}')
        print('-----------------------------------------------------')
        walk(parent if parent else self)

    def append(self, item) -> str:
        new_item = None
        if isinstance(item, Leaf) or isinstance(item, Node):
            super(Node, self).append(item)
            new_item = self[len(self)-1]
            if new_item.parent is None:
                new_item.parent = self

            item.id = self.tree.next_id()
            _list = [None] * (len(self.tree.headings) - len(item.columns))
            item.columns += _list

        return new_item

    def insert(self, idx, item):
        if idx == int(const.END):
            idx = len(self)
        elif idx < int(const.START):
            idx = int(const.START)

        new_item = None
        if isinstance(item, Leaf) or isinstance(item, Node):
            super(Node, self).insert(idx, item)
            new_item = self[len(self)-1]
            if new_item.parent is None:
                new_item.parent = self

            item.id = self.tree.next_id()
            _list = [None] * (len(self.tree.headings) - len(item.columns))
            item.columns += _list
        return new_item

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
        def walk(_parent, _item):
            if 'children' in _item:
                item = Node(parent=_parent, **_item)
                if 'children' in _item and len(_item['children']):
                    for node in _item['children']:
                        walk(item, node)
            else:
                item = Leaf(parent=_parent, **_item)
            items.append(item)
            _parent.append(item)

        if not data:
            return

        items = []
        parent = kwargs.get('parent', self)
        if isinstance(data, list):
            for cfg in data:
                walk(parent, cfg)

        return items

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
                    if _result is not None and _result.id == _id:
                        return _result

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
                    if _result is not None and _result.name == name:
                        return _result

        for item in self:
            if item.name == name:
                return item
            elif item.is_node and len(item):
                result = walk(item)
                if result is not None and result.name == name:
                    return result


class Tree(Node):
    def __init__(self, **kwargs):
        self.items = 0
        self.headings = kwargs.get('headings', [])
        super().__init__()

        self.name = '.'
        self.parent = None

    def next_id(self):
        self.items += 1
        return self.items

    def reindex(self, start=0):
        def walk(_parent):
            for _item in _parent:
                _item.id = self.next_id()
                if _item.is_node():
                    walk(_item)

        self.items = start
        for item in self:
            item.id = self.next_id()
            if item.is_node():
                walk(item)


def main():
    def test1():
        now = datetime.now()
        dt_string = now.strftime("%Y/%m/%d %H:%M:%S")

        # Create a tree one item at a time, using either kwargs or a dictionary.
        t = Tree(headings=['Type', 'Size', 'Last Modified', 'Path'])

        # Create node with kwargs.
        node = Node(name='Test 1', columns=['Node', '0 items'])
        # Append the node to the tree root.
        t.append(node)
        # Update two columns, one at a time.
        node.set(3, dt_string)
        node.set(4, node.path())

        # Create node with dictionary, and update some columns.
        node = Node({'name': 'Test 2', 'columns': ['Node', '0 items']})
        # Append the node to the tree.
        t.append(node)
        # Update two columns, one at a time.
        node.set(3, dt_string)
        node.set(4, node.path())

        leaf = Leaf(name='Test 3', columns=['Leaf', '0 Kb'])
        t.append(leaf)
        leaf.set(3, dt_string)
        leaf.set(4, leaf.path())

        node = Node(name='Test 4', columns=['Node', '0 items'])
        t.append(node)
        node.set(3, dt_string)
        node.set(4, node.path())

        node = Node(name='Test 5', columns=['Node', '0 items'])
        t.append(node)
        node.set(3, dt_string)
        node.set(4, node.path())

        leaf = Leaf(name='Leaf 5-1', columns=['Leaf', '0 Kb'])
        # Append the leaf to the node.
        node.append(leaf)

        # Update 3 column values.
        node.set((2, 3, 4), ('1 item', dt_string, leaf.path()))

        t.show()

    def test2():
        t = Tree(headings=['Type', 'Size', 'Path'])

        node = t.append(Node(name='Test Node 1'))
        node.set((1, 3), (node.type, node.path()))

        item = node.append(Leaf(name='Test Leaf 1'))

        item.set((1, 2, 3), (item.type, '0 Kb', item.path()))
        node.set(2, '1 item' if len(node) == 1 else f'{len(node)} items')

        item = node.insert(0, Leaf({'name': 'Test Leaf 2'}))  # Insert this leaf at the start of the node.
        item.set((1, 2, 3), (item.type, '0 Kb', item.path()))
        node.set(2, '1 item' if len(node) == 1 else f'{len(node)} items')

        sub_node = Node({'name': 'Test Sub Node 1'})
        node.append(sub_node)
        sub_node.set((1, 2, 3), (item.type, '0 items', item.path()))
        node.set(2, '1 item' if len(node) == 1 else f'{len(node)} items')

        item = Leaf({'name': 'Test Sub Leaf 1'})
        sub_node.append(item)
        item.set((1, 2, 3), (item.type, '0 Kb', item.path()))

        cell_data = '1 item' if len(sub_node) == 1 else f'{len(sub_node)} items'
        sub_node.set(2, cell_data)

        t.show()

    def test3():
        t = Tree(headings=['Type', 'Size', 'Path'])
        items = t.populate(data)

        for item in items:
            word = '0 Kb'
            if item.is_node():
                word = '1 item' if len(item) == 1 else f'{len(item)} items'
            item.set((1, 2, 3), (item.type, word, item.path()))
        t.show()

        items = t.query('Node 1a-1').populate(data)  # ./Node 1a/Node 1a-1, populate node from dictionary.
        for item in items:
            word = '0 Kb'
            if item.is_node():
                word = '1 item' if len(item) == 1 else f'{len(item)} items'
            item.set((1, 2, 3), (item.type, word, item.path()))
        t.show()

        t.reindex()  # Reindex the complete tree.
        t.show()

    data = [{
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

    test1()
    test2()
    test3()


if __name__ == '__main__':
    main()
