import dask

data = [1, 2, 3, 4, 5]
output = []


def inc(x):
    return x + 1


def double(x):
    return x * 2


def add(x, y):
    return x + y


for x in data:
    a = dask.delayed(inc)(x)
    b = dask.delayed(double)(x)
    c = dask.delayed(add)(a, b)
    output.append(c)

total = dask.delayed(sum)(output)
total.visualize()
