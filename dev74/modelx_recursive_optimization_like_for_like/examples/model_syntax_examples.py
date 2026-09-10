"""Illustrative source patterns only; these are not complete modelx models."""
from helpers.modelx_fast_lookup import exact4, grouped_step2, column_value

# Prepared references, built once outside hot Cell evaluation:
# mort_table_fast = build_exact4(...)
# return_scenario_fast = build_grouped_step2(...)
# age_at_entry_col = (...)

# Hot Cell examples:
def mort_rate_fast(mort_table_fast, basis, sex, smoker, age):
    return exact4(mort_table_fast, basis, sex, smoker, age)


def gross_return_fast(return_scenario_fast, scenario_id, subaccount_id, month):
    return grouped_step2(return_scenario_fast, scenario_id, subaccount_id, month)


def age_at_entry_fast(age_at_entry_col, point_index):
    return column_value(age_at_entry_col, point_index)
