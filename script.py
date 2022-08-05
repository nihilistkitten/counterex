from counterex import McfOpt, Trace, make_items

a, b, c, d = make_items((1, 2, 3, 4))
cache = McfOpt(2)
t = Trace([a, b, a, c, a])

print(cache.run(t))
