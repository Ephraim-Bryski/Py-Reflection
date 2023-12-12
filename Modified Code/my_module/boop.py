
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import pint
u = pint.UnitRegistry()

def A_func(__INSERTION_FUNCTIONS__=None):
    __INSERTIONS__ = []
    g = 2 * u.feet
    __INSERTIONS__.append({'source_code': 'g = 2 * u.feet', 'values': {'g': str(g)}})
    __LOOP_ASSIGN__ = []
    __INSERTIONS__.append(dict(iterator='i', values=list(range(5)), items=__LOOP_ASSIGN__))
    for i in range(5):
        boop = []
        __LOOP_ASSIGN__.append(boop)
        b = g * i
        boop.append({'source_code': 'b = g * i', 'values': {'g': str(g), 'i': str(i), 'b': str(b)}})
    if __INSERTION_FUNCTIONS__ is None:
        return b
    else:
        return [b, __INSERTIONS__]


__END_RESULT__ = A_func(__INSERTION_FUNCTIONS__ = [A_func])[-1]
import json
with open("Modified Code/__END_RESULT__.json","w") as f:
    f.write(json.dumps(__END_RESULT__,indent = 4))
