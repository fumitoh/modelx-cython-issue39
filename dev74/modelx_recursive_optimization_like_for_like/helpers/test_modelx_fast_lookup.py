from modelx_fast_lookup import (
    build_exact1, build_exact2, exact1, exact2,
    build_step1, step1,
    build_grouped_step2, grouped_step2,
    column_value,
)

x1 = build_exact1([(1, 10.0), (2, 20.0)])
assert exact1(x1, 2) == 20.0
x2 = build_exact2([("M", 30, 0.1), ("F", 30, 0.08)])
assert exact2(x2, "F", 30) == 0.08
s = build_step1([(0, 1.0), (12, 2.0), (24, 3.0)])
assert step1(s, 13) == 2.0
g = build_grouped_step2([
    (1, "A", 0, 0.01), (1, "A", 12, 0.02),
    (1, "B", 0, 0.03),
])
assert grouped_step2(g, 1, "A", 18) == 0.02
assert column_value((7, 8, 9), 1) == 8
print("ok")
