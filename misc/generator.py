def gen_fn():
    result = yield 1
    print('result of yield: {}'.format(result))
    result2 = yield 3
    print('result of 2nd yield: {}'.format(result2))
    return 'done'

try:
    g = gen_fn()
    print(g)

    return_value = next(g)
    print(return_value)

    return_value = g.send(2)
    print(return_value)

    g.send(4)
except StopIteration:
    pass
