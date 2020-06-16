from collections import deque


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


cfg = (
    {'n1': {
        'text': 'text n1',
        'i1': {'text': 'test i 1'}
    }},
    {'n2': {
        'text': 'text n1',
        'i1': {'text': 'test i 1'}
    }},
)

START = 0
END = -1


class Tree(deque):
    def __init__(self, parent, data):
        super().__init__()

        self.populate('', data)

    def add(self, parent, index=END, **data):
        if not parent:
            if index == END:
                self.append(data)
            else:
                self.insert(index, **data)

    def populate(self, parent, data):
        def walk(_node):
            self.append(data)
            print(111, _node)

        for node in data:
            walk(node)


def main():
    t = Tree('', cfg)
    t.add('', **{'test': 123})

    for item in t:
        print(222, item)


if __name__ == '__main__':
    main()
