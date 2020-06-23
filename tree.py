from enum import IntEnum
from collections import deque
from datetime import datetime

const = IntEnum('Constants', 'END START', start=-1)


class Base:
    def __init__(self, data=None, **kwargs):
        self.type = None

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

    def path(self):
        parts = []
        item = self
        while item is not None:
            parts.append(item.name)
            item = item.parent

        return '/'.join(list(reversed(parts))).lstrip('.')

    def clone(self, src, dst):
        items = []
        if src.is_node():
            for item in src:
                if item.is_node():
                    node = Node(parent=dst, name=item.name, columns=item.columns.copy())
                    new_item = dst.append(node)
                    new_item.parent = dst
                    items.append(new_item)

                    if len(item):
                        self.clone(item, new_item)
                else:
                    item = Leaf(parent=dst, name=item.name, columns=item.columns.copy())
                    new_item = dst.append(item)
                    new_item.parent = dst
                    items.append(new_item)
        else:
            pass

        return items

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

    def query(self, query):
        def search():
            for child in self:
                if child.name == query:
                    return child
                if child.is_node():
                    result = child.query(query)
                    if result is not None:
                        return result

        def get_by_id():
            _id = query

            for child in self:
                if child.id == _id:
                    return child

                if child.is_node() and len(child):
                    result = child.query(_id)
                    if result is not None:
                        return result

        def get_by_name():
            _query = query.lstrip('/').split('/', 1)

            segment = _query.pop(0)
            for child in self:
                if child.name == segment:
                    if not _query:
                        return child
                    else:
                        result = child.query(_query[0])
                        if result is not None:
                            return result
            else:
                return search()

        if isinstance(query, int):
            item = get_by_id()
        elif isinstance(query, str):
            item = get_by_name()
        else:
            item = None

        return item

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

        if isinstance(item, Leaf) or isinstance(item, Node):
            super(Node, self).insert(idx, item)

            if item.parent is None:
                item.parent = self

            item.id = self.tree.next_id()
            _list = [None] * (len(self.tree.headings) - len(item.columns))
            item.columns += _list
        return item

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


class Tree(Node):
    def __init__(self, **kwargs):
        self.items = 0
        self.headings = kwargs.get('headings', [])
        super().__init__()

        self.name = '.'
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

    def test2():
        def get_size(_node):
            return '1 item' if len(_node) == 1 else f'{len(_node)} items'

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

    def test4():
        t = Tree(headings=['Type', 'Size', 'Path'])
        items = t.populate(data)
        for item in items:
            word = '0 Kb'
            if item.is_node():
                word = '1 item' if len(item) == 1 else f'{len(item)} items'
            item.set((1, 2, 3), (item.type, word, item.path()))
        # t.reindex()
        t.show()
        print('------------------------------------------------------')

        # Clone data from one node to another,
        for i in t.clone(t.query('Sub Node 1a'), t.query('Node 1a-1')):
            i.set(3, i.path())
        t.show()

        # Removed the node cloned.
        x = t.query('Node 1a-1')
        print(x.id, x.name, x.path())

        # t.reindex()
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
    # test2()
    # test3()
    # test4()


if __name__ == '__main__':
    main()
