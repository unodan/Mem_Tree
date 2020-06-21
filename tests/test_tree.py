import unittest
import json
from tree import Tree, Leaf, Node
from config import data

from copy import deepcopy


class TestTree(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures, if any."""
        self.cfg = deepcopy(data)
        self.t = Tree(self.cfg)

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_get(self):
        # Action, get tree
        t = self.t

        # Asert, that get() gets the correct column value.
        self.assertEqual('Node One', t[0].get(0))
        self.assertEqual('Node', t[0].get(1))
        self.assertEqual('Leaf Three', t[0][3][0].get(0))
        self.assertEqual('Leaf', t[0][3][0].get(1))

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

        # Action, set a new values for columns.
        t[0][3][0].set(0, 'Some Name')
        t[0][3][0].set(1, '101 items')

        # Asert, make sure we get the correct column values.
        self.assertEqual('Some Name', t[0][3][0].get(0))
        self.assertEqual('101 items', t[0][3][0].get(1))

    def test_query(self):
        # Action, get tree.
        t = self.t

        # Asert, make sure we get the correct target from the query.
        self.assertEqual('Node One', t.query('Node One').name)  # Query by name.
        _id = t.query('Leaf Three').id
        self.assertEqual('Leaf Three', t.query(_id).name)  # Query by id.

    def test_append(self):
        # Action, get tree.
        t = self.t

        # Action, append leaf in the root of tree.
        leaf = Leaf({'name': 'test leaf'})
        t.append(leaf)

        # Asert, leaf == last item, in the root of the tree.
        self.assertEqual(leaf, t[-1])

        # Action, append leaf in the root of a subtree.
        subtree = t.query_by_name('Node Four')
        subtree.append(leaf)

        # Asert, leaf == last item, in the root of the subtree.
        self.assertEqual(leaf, subtree[-1])

    def test_insert(self):
        # Action, get tree.
        t = deepcopy(self.t)
        t.size = 0

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
        subtree = t.query_by_name('Node Three')

        # Action, insert leafs.
        subtree.insert(0, leaf1)
        subtree.insert(2, leaf2)
        subtree.insert(len(subtree), leaf3)

        # Asert, leaf == item inserted at index.
        self.assertEqual(subtree, t.query_by_name('Node Three'))
        self.assertEqual(leaf1, subtree[0])
        self.assertEqual(leaf2, subtree[2])
        self.assertEqual(leaf3, subtree[len(subtree)-1])

    def test_get_cell(self):
        # Action, get tree.
        t = self.t

        # Asert, column value == expected value.
        self.assertEqual('Node', t.get_cell(7, 1))
        self.assertEqual('0 items', t.get_cell('Node Three', 2))

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

        # Action, assign source and target data, complete tree.
        cfg = deepcopy(data)
        _list = json.dumps(cfg, sort_keys=True)
        _dump = json.dumps(t.to_list(), sort_keys=True)

        # Asert, source and target are equal.
        self.assertEqual(_list, _dump)

        # Action, assign source and target data, complete node.
        node = t.query_by_name('Node Three')
        _list = json.dumps(node.to_list(), sort_keys=True)
        _dump = json.dumps(cfg[0]['children'][3]['children'], sort_keys=True)

        # Asert, source and target are equal.
        self.assertEqual(_list, _dump)

    def test_query_by_id(self):
        # Action, get tree.
        t = self.t

        # Action, get target id.
        target = t[0]
        _id = target.id

        # Asert, ids match from query.
        self.assertEqual(_id, t.query_by_id(_id).id)

    def test_query_by_name(self):
        # Action, get tree.
        t = self.t

        # Asert, get target name.
        target = t[0]
        name = target.name

        # Asert, names match from query.
        self.assertEqual(name, t.query_by_name(name).name)
