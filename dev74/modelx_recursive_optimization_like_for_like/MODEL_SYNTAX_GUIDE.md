# Model syntax for fast pure-Python and native recursive execution

The fastest path found in these experiments does **not** require changing recursive Cell semantics.  The useful source-level change is to make hot scalar data access explicit instead of embedding general pandas operations inside every Cell call.

## Preferred hot-Cell syntax

Use a small set of lookup operations with primitive scalar arguments:

```python
from modelx_fast_lookup import exact4, grouped_step2, column_value


def mort_rate(t):
    return exact4(
        mort_table_fast,
        basis(), sex(), smoker(), attained_age(t),
    )


def gross_return(t):
    return grouped_step2(
        return_scenario_fast,
        scenario_id(), subaccount_id(), duration_mth(t),
    )


def age_at_entry():
    return column_value(age_at_entry_col, point_index)
```

The prepared providers are built once when the model/exported runner is prepared.  The hot Cells remain ordinary recursive functions.

## Avoid in hot numeric Cells when a prepared equivalent exists

```python
# repeated pandas row/column lookup
mort_table.loc[(basis(), sex(), smoker(), age(t)), "rate"]

# repeated slicing/filtering to implement a step function
sub = return_scenario.loc[(scenario_id(), subaccount_id())]
month = max(m for m in sub.index if m <= duration_mth(t))
return sub.loc[month, "return"]

# returning a Series only to extract one scalar
model_point_table.loc[point_id]["age_at_entry"]
```

These forms are readable for authoring, but they drag pandas Index/Series/DataFrame machinery into a scalar calculation repeated thousands of times.

## Why this syntax also facilitates native C

The helper calls define a small semantic ABI that a compiler can lower directly:

| source helper | Python execution | native lowering |
|---|---|---|
| `exact1..exact4` | prepared dict lookup | encoded/dense array or typed hash lookup |
| `step1` | `bisect_right` over sorted immutable axis | inline binary search over typed C arrays |
| `grouped_step1/2` | group lookup + step lookup | encoded group -> offset/range + inline binary search |
| `column_value` | sequence indexing | direct typed column pointer/array indexing |

The native compiler should recognize these calls as intrinsics.  It should prepare/encode categorical keys once, keep boundary semantics from the prepared provider, and emit no pandas/Python object access in the numeric closure.

`helpers/native_lookup_helpers.pxd` contains small `noexcept nogil` predecessor-search primitives suitable for generated Cython after normalization.

## Recommended restrictions for the native fast path

These are fast-path requirements, not restrictions on modelx as a whole. Unsupported Cells fall back to the normal runtime.

- Hot lookup arguments should resolve to primitive numeric/boolean/categorical scalar values.
- Lookup semantics should be explicit: exact, predecessor/step, or grouped predecessor/step.
- Boundary behavior should be fixed during preparation rather than inferred dynamically.
- Avoid constructing DataFrames, Series, lists of filtered rows, or other Python containers inside hot numeric Cells.
- Keep lookup helpers pure/read-only during a prepared valuation.
- Source-level numeric reductions may remain ordinary Python expressions; a native backend can lower them to C loops while keeping Cell recursion intact.

## Long-term modelx direction

Manual helper syntax is useful immediately and gives generated/native code a stable target.  Longer term, `model.export()` / `model.prepare()` can recognize supported pandas lookup patterns and rewrite them to the same internal helper ABI automatically, retaining the original DataFrames as the public/source-of-truth representation.
