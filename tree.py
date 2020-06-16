from collections import deque


data = {
    'n1': {
        'text': 'text n1',
        'i1': {'text': 'test i 1'}
    },
    'n2': {
        'text': 'text n1',
        'i1': {'text': 'test i 1'}
    },
}

que = deque()
for k, v in data.items():
    que.append({k:v})

for idx, item in enumerate(que):
    print(idx, item)

# This is my change!