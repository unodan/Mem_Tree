import unittest
import json
from tree import Tree, Leaf, END, START


class TestTree(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures, if any."""
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
        self.t = Tree(cfg)

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_append(self):
        # Action, append leaf in the root of tree.
        t = self.t
        leaf = Leaf(t, {'name': 'test leaf'})
        t.append(leaf)
        # Asert, leaf == last item
        self.assertEqual(leaf, t[-1])

        # Action, append leaf in the root of subtree
        subtree = t.get_by_name('Node 1').get_by_name('Node 1-1')
        subtree.append(leaf)
        # Asert, leaf == last item
        self.assertEqual(leaf, subtree[-1])

    def test_insert(self):
        # Action, insert leaf in the root of tree.
        t = self.t
        leaf = Leaf(t, {'name': 'test leaf'})
        t.insert(START, leaf)
        t.insert(2, leaf)
        t.insert(END, leaf)
        # Asert, leaf == item at insert index
        self.assertEqual(leaf, t[START])
        self.assertEqual(leaf, t[2])
        self.assertEqual(leaf.name, t[END].name)

        # Action, insert leaf in the the root of subtree
        leaf = Leaf(t, {'name': 'test leaf'})
        subtree = t.get_by_name('Node 1').get_by_name('Node 1-1')
        subtree.insert(START, leaf)
        subtree.insert(2, leaf)
        subtree.insert(END, leaf)
        # Asert, leaf == item at insert index
        self.assertEqual(leaf, subtree[START])
        self.assertEqual(leaf, subtree[2])
        self.assertEqual(leaf, subtree[END])

    def test_to_list(self):
        # Action, assign source data.
        t = self.t
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
        _list = json.dumps(cfg, sort_keys=True)
        _dump = json.dumps(t.to_list(), sort_keys=True)
        # Asert, source and target are equal.
        self.assertEqual(_list, _dump)

        node = t.get_by_name('Node 1')
        _list = json.dumps(node.to_list(), sort_keys=True)
        _dump = json.dumps(cfg[0]['children'], sort_keys=True)
        self.assertEqual(_list, _dump)

    def test_populate(self):
        # Action, assign source and target.
        t = self.t
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
        # Action, get copy of tree data then empty the tree.
        _list = json.dumps(cfg, sort_keys=True)
        t.clear()
        # Asert, tree is empty.
        self.assertEqual(len(t), 0)
        # Action, populate tree with config data.
        t.populate(cfg)
        _dump = json.dumps(t.to_list(), sort_keys=True)
        # Asert, tree data == config data.
        self.assertEqual(_list, _dump)

    def test_get_by_name(self):
        # Action, assign source and target.
        t = self.t
        target = t[1]
        item = t.get_by_name(target.name)
        # Asert, item is in list.
        self.assertEqual(target, item)
