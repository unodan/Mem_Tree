import unittest
from json import dumps
from tree import Tree, Leaf, Node
from config import data
from copy import deepcopy


class TestTree(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures, if any."""
        self.cfg = data
        self.t = Tree(headings=['Column1', 'Column2', 'Column3'])
        self.t.populate(data=self.cfg)

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_get(self):
        # Action, get tree
        t = self.t

        # Asert, that we get the correct cell value.
        self.assertEqual('Node One', t[0].get(0))
        self.assertEqual('Node One', t.query('Node One').get(0))

        # Action, get an item.
        item = t.query('Node One/Node Two')

        # Action, set cell value.
        item.set(1, item.type)

        # Asert, that the value == value set.
        self.assertEqual(item.type, item.get(1))

        # Asert, that the get value is correct.
        self.assertEqual('Leaf Three', t[0][3][0].get(0))
        self.assertEqual('Leaf Three', t.query('Leaf Three').get(0))

        # Action, set cell value.
        t[0][3][0].set(1, 'Leaf')  # Note, t[0][3][0] == /Node One/Node Three/Leaf Three
        # Asert, that the get value is correct.
        self.assertEqual('Leaf', t.query('Node One/Node Three/Leaf Three').get(1))

    def test_set(self):
        # Action, get tree
        t = self.t

        # Asert, make sure we have the correct target.
        self.assertEqual('Node One', t[0].get(0))

        # Action, set a new values for columns.
        t[0].set(0, 'New Name')
        t[0].set(1, '99 items')

        # Asert, make sure we get the correct column values.
        self.assertEqual('New Name', t[0].get(0))
        self.assertEqual('99 items', t[0].get(1))

        # Action, set new values for columns.
        t[0][3][0].set(0, 'Some Name')
        t[0][3][0].set(1, '101 items')

        # Asert, make sure we get the correct column values.
        self.assertEqual('Some Name', t[0][3][0].get(0))
        node = t.query('New Name/Node Three/Some Name')
        node.set(1, '102 items')
        self.assertEqual('102 items', t[0][3][0].get(1))

        # Action, set new values for columns.
        node.set((1, 2, 3), ('One', 'Two', 'Three'))

        # # Asert, make sure we get the correct column values.
        self.assertEqual('One', node.get(1))
        self.assertEqual('Two', node.get(2))
        self.assertEqual('Three', node.get(3))
        self.assertEqual(('One', 'Two', 'Three'), node.get((1, 2, 3)))
        self.assertEqual(node.get(), ('Some Name', 'One', 'Two', 'Three'))

    def test_find(self):
        # Action, get tree
        t = self.t

        # Asert, that we get the correct cell value.
        _id = t.query('Node One').id
        self.assertEqual('Node One', t[0].get(0))
        self.assertEqual('Node One', t.find_by_id(_id).get(0))
        self.assertEqual('Node One', t.find('Node One').get(0))

        # Asert, that we get the correct cell value.
        _id = t.query('Node Four').id
        self.assertEqual('Node Four', t[0][3][1].get(0))
        self.assertEqual('Node Four', t.find_by_id(_id).get(0))
        self.assertEqual('Node Four', t.find('Node Four').get(0))

    def test_path(self):
        # Action, get tree
        t = self.t

        # Action, get an item by name and get an item by path.
        item_by_name = t.query('Leaf Four')
        # Asert, test that both paths are equal.
        self.assertEqual('/Node One/Node Three/Node Four/Leaf Four', item_by_name.path())

    def test_query(self):
        # Action, get tree.
        t = self.t

        # Asert, make sure we get the correct target from the query.
        self.assertEqual('Node One', t.query('Node One').name)  # Query by name.

        # Action, get an id from a leaf, used to verify query success.
        _id = t.query('Leaf Three').id

        # Asert, make sure we get the correct target from the query.
        self.assertEqual('Leaf Three', t.query(_id).name)  # Query by id.

        # Action, get an id from a leaf, used to verify query success.
        _id = t.query('Node One/Node Three/Node Four/Leaf Four').id

        # Asert, make sure we get the correct target from the query.
        self.assertEqual('Leaf Four', t.query(_id).name)  # Query by id.
        self.assertEqual('Leaf Four', t.query('Node One/Node Three/Node Four/Leaf Four').name)  # Query by id.

    def test_delete(self):
        # Action, get tree.
        t = self.t

        # Action, assign a node to delete.
        node = t.query('Node Two')

        # Asert, make sure the node exists.
        self.assertIsNotNone(node)

        # Action, delete the node.
        node.delete()

        # Action, query for deleted node.
        node = t.query('Node Two')

        # Asert, test to see if node was deleted.
        self.assertIsNone(node)

        # Action, get node.

    def test_append(self):
        # Action, get tree.
        t = self.t

        # Action, append leaf in the root of tree.
        leaf = Leaf({'name': 'test leaf'})
        t.append(leaf)

        # Asert, leaf == last item, in the root of the tree.
        self.assertEqual(leaf, t[-1])

        # Action, append leaf in the root of a subtree.
        subtree = t.query('Node Four')
        subtree.append(leaf)

        # Asert, leaf == last item, in the root of the subtree.
        self.assertEqual(leaf, subtree[-1])

    def test_insert(self):
        # Action, get tree.
        t = deepcopy(self.t)
        t = self.t
        # Action, set item counter to 0.
        t.items = 0

        # Action, create leafs.
        leaf1 = Leaf({'name': 'test leaf1'})
        leaf2 = Leaf({'name': 'test leaf2'})
        leaf3 = Leaf({'name': 'test leaf3'})

        # Action, insert leafs.
        t.insert(0, leaf1)
        t.insert(2, leaf2)
        t.insert(len(t), leaf3)

        # Asert, leaf == item inserted at index.
        self.assertEqual(leaf1, t[0])
        self.assertEqual(leaf2, t[2])
        self.assertEqual(leaf3, t[len(t)-1])

        # Action, create leafs.
        leaf1 = Leaf({'name': 'test leaf1'})
        leaf2 = Leaf({'name': 'test leaf2'})
        leaf3 = Leaf({'name': 'test leaf3'})

        # Action, get node.
        t = deepcopy(self.t)
        subtree = t.query('Node Three')

        # Action, insert leafs.
        subtree.insert(0, leaf1)
        subtree.insert(2, leaf2)
        subtree.insert(len(subtree), leaf3)

        # Asert, leaf == item inserted at index.
        self.assertEqual(subtree, t.query('Node Three'))
        self.assertEqual(leaf1, subtree[0])
        self.assertEqual(leaf2, subtree[2])
        self.assertEqual(leaf3, subtree[len(subtree)-1])

    def test_is_node(self):
        # Action, get tree.
        t = self.t

        # Action, get a node.
        node = t.query('Node One/Node Two')

        # Asert, test that the types are equal.
        self.assertEqual(Node, type(node))

        # Action, get a leaf.
        leaf = t.query('Node One/Leaf One')

        # Asert, test that the types are equal.
        self.assertEqual(Leaf, type(leaf))

    def test_populate(self):
        # Action, get config and convert to json string.
        config_data = dumps(self.cfg, sort_keys=True)

        # Action, create tree from config.
        t = Tree()
        t.populate(self.cfg)

        # Action, convert tree to json.
        tree_data = dumps(t.to_list(), sort_keys=True)

        # Asert, that the tree contains the populate data.
        self.assertEqual(tree_data, config_data)

    def test_get_cell(self):
        # Action, get tree.
        t = self.t

        # Action, get an item.
        node = t.query('Node Three')
        node.set(1, 'Test Node')
        node.set(2, '101 items')

        # Asert, column value == expected value, by id.
        self.assertEqual('Test Node', t.get_cell(node.id, 1))

        # Asert, column value == expected value, by name.
        self.assertEqual('101 items', t.get_cell('Node Three', 2))

    def test_set_cell(self):
        # Action, get tree.
        t = self.t

        # Action, insert leaf in the root of tree.
        leaf = Leaf({'name': 'test leaf', 'columns': ['test1', 'test2', 'test3']})
        t.append(leaf)

        # Asert, leaf was appended.
        self.assertEqual(leaf.name, t.query('test leaf').name)

        # Asert, column value == 'test1'
        self.assertEqual('test1', t.get_cell(leaf.id, 1))
        self.assertEqual('test1', t.get_cell('test leaf', 1))

        # Action, set column value.
        t.set_cell('test leaf', 2, 'TEST2')
        # Asert, column value == 'TWO' (upper case)
        self.assertEqual('TEST2', t.get_cell('test leaf', 2))

    def test_to_list(self):
        # Action, get tree.
        t = self.t

        _list = dumps(self.cfg, sort_keys=True)
        _dump = dumps(t.to_list(), sort_keys=True)

        # Asert, source and target are equal.
        self.assertEqual(_list, _dump)

        # Action, assign source and target data, complete node.
        node = t.query('Node Three')
        _list = dumps(node.to_list(), sort_keys=True)
        _dump = dumps(self.cfg[0]['children'][3]['children'], sort_keys=True)

        # Asert, source and target are equal.
        self.assertEqual(_list, _dump)

    # def test_query_by_id(self):
    #     # Action, get tree.
    #     t = self.t
    #
    #     # Action, get target id.
    #     target = t[0]
    #     _id = target.id
    #
    #     # Asert, ids match from query.
    #     self.assertEqual(_id, t.query_by_id(_id).id)
    #
    # def test_query_by_name(self):
    #     # Action, get tree.
    #     t = self.t
    #
    #     # Asert, get target name.
    #     target = t[0]
    #     name = target.name
    #
    #     # Asert, names match from query.
    #     self.assertEqual(name, t.query_by_name(name).name)
