import random 
def gen_array(size=30, min_val=30, max_val=100):
    return [random.randint(min_val, max_val) for _ in range (size)]
def bubble_sort(values):
    n=len(values)
    for i in range (n-1, 0, -1):
        swapped=False

        for j in range (i):
            yield {
                'type': 'compare',
                'indices': (j, j+1),
                'values': values.copy()
            }
            if values[j]>values[j+1]:
                values[j], values[j+1] = values[j+1], values[j]
                swapped = True
                yield {
                    'type': 'swap',
                    'indices': (j, j+1),
                    'values': values.copy()
                }
        if not swapped:
            break
    yield {
        'type': 'sorted',
        'indices': list(range(n)),
        'values': values.copy()
    }
def sort_choice(values):
    n = len(values)
    for i in range(n - 1):
        min_index = i
        for j in range(i + 1, n):
            yield {
                'type': 'compare',
                'indices': (j, min_index),
                'values': values.copy()
            }
            if values[j] < values[min_index]:
                min_index = j
                yield {
                    'type': 'new_min',
                    'indices': (min_index,),
                    'values': values.copy()
                }
        if min_index != i:
            values[i], values[min_index] = values[min_index], values[i]
            yield {
                'type': 'swap',
                'indices': (i, min_index),
                'values': values.copy()
            }
    yield {
        'type': 'sorted',
        'indices': list(range(n)),
        'values': values.copy()
    }
def binary_search(values, target):
    left=0
    right=len(values)-1
    while left<=right:
        mid = (left+right)//2
        yield {
            'type': 'check',
            'left': left,
            'right': right, 
            'mid': mid,
            'target': target,
            'values': values.copy()
        }
        if values[mid]==target:
            yield {
                'type': 'found',
                'index': mid,
                'values': values.copy()
            }
            return 
        elif values[mid]<target:
            left= mid +1
        else:
            right = mid-1
    yield{
        'type': 'not_found',
        'left': left, 
        'right': right,
        'values': values.copy()
    }
