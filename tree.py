from enum import IntEnum
from datetime import datetime
from collections import deque

import cProfile, pstats, io

const = IntEnum('Constants', 'END START', start=-1)


class Base:
    def __init__(self, data=None, **kwargs):
        self.type = None
        if data:
            self.id = data.get('id')
            self.name = data.get('name')
            self.parent = data.get('parent')
            self.columns = data.get('columns', [])
        else:
            self.id = kwargs.get('id')
            self.name = kwargs.get('name')
            self.parent = kwargs.get('parent')
            self.columns = kwargs.get('columns', [])

    @property
    def tree(self):
        item = self
        while not isinstance(item, Tree):
            item = item.parent
        return item

    def clone(self, dst):
        if isinstance(self, Node):
            node = Node(name=self.name)
            items = [node]
            results = []
            if isinstance(dst, Node):
                dst.append(node)
                results = node.populate(self.to_list())

            return items + results

    def get(self, columns=None):
        if columns is None:
            columns = tuple(range(0, len(self.tree.headings)+1))
        elif isinstance(columns, int):
            columns = (columns, )
        elif not isinstance(columns, tuple):
            return

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
        if isinstance(columns, int):
            columns = (columns, )
        elif not isinstance(columns, tuple):
            return

        if not isinstance(values, tuple):
            values = (values, )

        for column, value in dict(zip(columns, values)).items():
            if column < 0 or column > len(self.columns):
                continue
            elif not column:
                self.name = value
            else:
                self.columns[column-1] = value

    def path(self):
        uri = []
        item = self
        while item is not None:
            uri.append(item.name)
            item = item.parent
        return '/'.join(list(reversed(uri))).lstrip('.')

    def delete(self, item=None):
        node = item if item else self
        parent = node.parent
        del parent[parent.index(node)]

    def is_node(self, item=None):
        if item is None:
            item = self
        return True if isinstance(item, Node) else False


class Leaf(Base):
    def __init__(self, data=None,  **kwargs):
        super().__init__(data, **kwargs)
        self.type = 'Leaf'
        if self.parent is not None:
            self.parent.append(self)

    def __len__(self):
        return None


class Node(Base, deque):
    def __init__(self, data=None, **kwargs):
        Base.__init__(self, data, **kwargs)
        deque.__init__(self)
        self.type = 'Node'
        if self.parent is not None:
            self.parent.append(self)

    @property
    def children(self):
        return self

    def move(self, dst):
        if isinstance(dst, Node):
            node = Node(name=self.name)
            items = [node]
            dst.append(node)
            items += node.populate(self.to_list())
            self.delete()
            return items

    def show(self, **kwargs):
        label = kwargs.get('label', '')
        indent = kwargs.get('indent', 2)
        index_pad = kwargs.get('index_pad', 2)
        parent = kwargs.get('parent', self)

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
        if label:
            label = f' {label}\n'
        print('-----------------------------------------------------')
        print(f'{label}   ID: Name{header_postfix}')
        print('-----------------------------------------------------')
        walk(parent)

    def query(self, query):
        if isinstance(query, int):
            item = self.find_by_id(query)
        elif isinstance(query, str):
            item = self.find(query)
        else:
            item = None

        return item

    def append(self, item, parent=None) -> str:
        parent = parent if parent else self

        if self.tree.unique:
            for i in parent:
                if i.name == item.name:
                    raise ValueError(f'duplicate name {item.name} found.')

        new_item = None
        if isinstance(item, Leaf) or isinstance(item, Node):
            super(Node, self).append(item)

            new_item = parent[len(parent)-1]
            if new_item.parent is None:
                new_item.parent = parent

            item.id = self.tree.next_id()
            item.columns += [None] * (len(self.tree.headings) - len(item.columns))

        return new_item

    def insert(self, idx, item, parent=None):
        parent = parent if parent else self

        if self.tree.unique:
            for i in parent:
                if i.name == item.name:
                    raise ValueError(f'duplicate name {item.name}" found.')

        if idx == int(const.END):
            idx = len(parent)
        elif idx < int(const.START):
            idx = int(const.START)

        if isinstance(item, Leaf) or isinstance(item, Node):
            super(Node, self).insert(idx, item)

            if item.parent is None:
                item.parent = parent

            item.id = self.tree.next_id()
            item.columns += [None] * (len(self.tree.headings) - len(item.columns))
        return item

    def to_list(self, parent=None):
        def set_data(_item, _data):
            for node in _item:
                _item_data = {'name': node.name, 'columns': node.columns}
                _data.append(_item_data)
                if node.is_node():
                    _item_data['children'] = []
                    set_data(node, _item_data['children'])

        data = []
        parent = parent if parent else self
        for item in parent:
            if item.is_node():
                item_data = {'name': item.name, 'columns': item.columns, 'children': []}
                data.append(item_data)
                set_data(item, item_data['children'])
            else:
                item_data = {'name': item.name, 'columns': item.columns}
                data.append(item_data)
        return data

    def populate(self, data, **kwargs):
        def walk(parent, item):
            if 'children' in item:
                new_node = Node(**item)
                parent.append(new_node, parent=parent)
                if 'children' in item and len(item['children']):
                    for node in item['children']:
                        walk(new_node, node)
            else:
                new_node = Leaf(**item)
                parent.append(new_node, parent=parent)

            items.append(new_node)

        if not data:
            return

        items = []
        if isinstance(data, list):
            for cfg in data:
                walk(kwargs.get('parent', self), cfg)

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

    def find_all(self, query, recursive=False):
        def find(item):
            if item.name == query:
                items.append(item)

            for child in item:
                if '/' in query and query not in child.path() and child.is_node():
                    for d in child:
                        if query in d.path() and d not in items:
                            items.append(d)
                        if d.is_node() and recursive:
                            find(d)
                elif query in child.path() and child not in items:
                    items.append(child)
                elif recursive and child.is_node():
                    find(child)

        items = []
        find(self)
        return items

    def find_by_id(self, _id):
        for child in self:
            if child.id == _id:
                return child

            if child.is_node() and len(child):
                result = child.query(_id)
                if result is not None:
                    return result

    def find(self, query, **kwargs):
        def search(parent, _query):
            for _child in parent:
                if _child.name == _query:
                    return _child

            for _child in parent:
                if _child.is_node():
                    result = search(_child, _query)
                    if result is not None:
                        return result

        _all = kwargs.get('all', False)

        if _all:
            return self.find_all(query, recursive=True)

        if '/' in query:
            if query.startswith('/'):
                item = None
                parts = query.lstrip('/').split('/', 1)
                for child in self.tree:
                    if child.name == parts[0]:
                        item = child
                        break
            else:
                parts = query.split('/', 1)
                item = search(self, parts.pop(0))

            if item and query in item.path():
                return item
            elif item:
                return item.find(parts[0])
        else:
            return search(self, query)


class Tree(Node):
    def __init__(self, **kwargs):
        self.items = 0
        self.unique = kwargs.get('unique', True)
        self.headings = kwargs.get('headings', [])
        super().__init__()

        self.id = 0
        self.name = '.'
        self.label = kwargs.get('label', '')
        self.type = 'Tree'
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
    def examples1():
        print('\n## EXAMPLE 1 ###############################################')
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
        leaf.set((1, 2, 3, 4), (leaf.type, '0 Kb', dt_string, leaf.path()))

        sub_node = Node(name='Test 4', columns=['Node', '0 items'])
        node.append(sub_node)
        sub_node.set((1, 2, 3, 4), (sub_node.type, '0 items', dt_string, sub_node.path()))

        leaf = Leaf(name='Leaf 55', columns=['Leaf', '0 Kb'])
        # Append the leaf to the node.
        sub_node.append(leaf)
        leaf.set((1, 2, 3, 4), (leaf.type, '0 Kb', dt_string, leaf.path()))

        # Update 3 column values.
        node.set((2, 3, 4), ('1 item', dt_string, leaf.path()))

        t.show()

    def examples2():
        def get_size(_node):
            return '1 item' if len(_node) == 1 else f'{len(_node)} items'

        print('\n## EXAMPLE 2 ###############################################')

        t = Tree(headings=['Type', 'Size', 'Path'])

        node = t.append(Node(name='Test Node 1'))
        node.set((1, 3), (node.type, node.path()))

        item = node.append(Leaf(name='Test Leaf 1'))
        item.set((1, 2, 3), (item.type, '0 Kb', item.path()))
        node.set(2, get_size(node))

        item = node.insert(0, Leaf({'name': 'Test Leaf 2'}))  # Insert this leaf at the start of the node.
        item.set((1, 2, 3), (item.type, '0 Kb', item.path()))
        node.set(2, get_size(node))

        sub_node = node.append(Node(name='Test Sub Node 1'))
        sub_node.set((1, 2, 3), (item.type, '0 items', sub_node.path()))
        node.set(2, get_size(node))

        leaf = sub_node.append(Leaf({'name': 'Test Sub Leaf 1'}))
        leaf.set((1, 2, 3), (item.type, '0 items', leaf.path()))
        sub_node.set(2, get_size(sub_node))

        t.show()

    def examples3():
        print('\n## EXAMPLE 3 ###############################################')

        t = Tree(headings=['Type', 'Size', 'Path'])
        items = t.populate(data1)

        for item in items:
            word = '0 Kb'
            if item.is_node():
                word = '1 item' if len(item) == 1 else f'{len(item)} items'
            item.set((1, 2, 3), (item.type, word, item.path()))
        t.show()

        items = t.query('Node 1a-1').populate(data1)
        for item in items:
            word = '0 Kb'
            if item.is_node():
                word = '1 item' if len(item) == 1 else f'{len(item)} items'
            item.set((1, 2, 3), (item.type, word, item.path()))
        t.show()

        t.reindex()
        t.show()

    def examples4():
        print('\n## EXAMPLE 4 ###############################################')

        t = Tree(headings=['Type', 'Size', 'Path'])
        items = t.populate(data1)
        for item in items:
            word = '0 Kb'
            if item.is_node():
                word = '1 item' if len(item) == 1 else f'{len(item)} items'
            item.set((1, 2, 3), (item.type, word, item.path()))
        # t.reindex()
        t.show()
        print('------------------------------------------------------')

    def examples5():
        print('\n## EXAMPLE 5 ###############################################')
        t = Tree(unique=False)

        # Create item with kwargs.
        Leaf(name='Test 2', parent=t)
        Leaf(name='Test 3', parent=t)
        Leaf(name='Test 3', parent=t)

        node = Node(name='Test 1', parent=t)
        Leaf(name='Test 3', parent=node)

        node = Node(name='Test 1', parent=t)
        Leaf(name='Test 3', parent=node)

        node_x = Node(name='Test 1', parent=node)
        Leaf(name='Test 3', parent=node_x)

        node_y = Node(name='Test 1', parent=node_x)
        Leaf(name='Test 3', parent=node_y)

        t.reindex()
        t.show()

        print('-- 1 ------------------------------------------------')
        print('Find all "Test 3" items in the root of the tree, none recursive.')
        for i in t.find('Test 3', all=True):
            print(f'{str(i.id).zfill(4)}:', i.name)

        print('-- 2 ------------------------------------------------')
        print('Find all "Test 3" items in the tree, recursively.')
        for i in t.find('Test 3', all=True):
            print(f'{str(i.id).zfill(4)}:', i.name)

        print('-- 3 ------------------------------------------------')
        print('Find all "Test 1/Test 3" items in the tree, recursively.')

        for i in t.find('Test 1/Test 3', all=True):
            print(f'{str(i.id).zfill(4)}:', i.name)

        print('-- 4 ------------------------------------------------')
        print('Find all "Test 1/Test 1/Test 3" items in the tree, recursively.')

        for i in t.find('Test 1/Test 1/Test 3', all=True):
            print(f'{str(i.id).zfill(4)}:', i.name)

        print('-- 5 ------------------------------------------------')
        print('Find all "Test 1/Test 1/Test 1/Test 3" items in the tree, recursively.')

        for i in t.find('Test 1/Test 1/Test 1/Test 3', all=True):
            print(f'{str(i.id).zfill(4)}:', i.name)

        print('-----------------------------------------------------')

    def examples6():
        print('\n## EXAMPLE 6 ###############################################')
        now = datetime.now()
        dt_string = now.strftime("%Y/%m/%d %H:%M:%S")

        t1 = Tree(headings=['Type', 'Date', 'Path'], unique=False)

        for i in range(1, 3):
            data2[0]['name'] = f'Node {i}'
            items = t1.populate(data2)
            for item in items:
                item.set((1, 2, 3), (item.type, dt_string, item.path()))
        t1.show(label='Tree: One')

        src = t1.query('Node 1')
        node2 = t1.query('Node 2')

        t2 = Tree(headings=['Type', 'Date', 'Path'], unique=False)

        for i in src.clone(t2):
            i.set((1, 2, 3), (i.type, dt_string, i.path()))

        for i in t2.query('Node n1-2-2').populate(src.to_list()):
            i.set((1, 2, 3), (i.type, dt_string, i.path()))

        for i in node2.move(t2):
            i.set((1, 2, 3), (i.type, dt_string, i.path()))

        t1.show(label='Tree: One')

        t2.show(label='Tree: Two')

    data1 = [{
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

    data2 = [{
        'name': 'Node 1',
        'children': [
            {
                'name': 'Leaf n1-1',
            },
            {
                'name': 'Node n1-1',
                'children': [],
            },
            {
                'name': 'Leaf n1-2',
            },
            {
                'name': 'Node n1-2',
                'children': [
                    {
                        'name': 'Leaf n1-2-1',
                    },
                    {
                        'name': 'Node n1-2-1',
                        'children': [],
                    },
                    {
                        'name': 'Leaf n1-2-2',
                    },
                    {
                        'name': 'Node n1-2-2',
                        'children': [
                            {
                                'name': 'Leaf n1-2-2-1',
                            },
                        ]
                    },
                ]
            },
        ],
    }]

    # examples1()
    # examples2()
    # examples3()
    # examples4()
    examples5()
    # examples6()


if __name__ == '__main__':
    main()
