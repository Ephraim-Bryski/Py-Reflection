
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import py_reflection
import importlib
import sample_module
import my_module
import pint
import docx
import create_with_meta
u = pint.UnitRegistry()
importlib.reload(py_reflection)
get_meta = True

def do_stuff(__INSERTION_FUNCTIONS__=None):
    __INSERTIONS__ = []
    g = 2 * u.feet
    __INSERTIONS__.append({'source_code': 'g = 2 * u.feet', 'values': {'g': str(g)}})
    __LOOP_ASSIGN__ = []
    __INSERTIONS__.append(dict(iterator='i', values=list(range(5)), items=__LOOP_ASSIGN__))
    for i in range(5):
        boop = []
        __LOOP_ASSIGN__.append(boop)
        b = g * i
        boop.append({'source_code': 'b = g * i', 'values': {'i': str(i), 'b': str(b), 'g': str(g)}})
    if __INSERTION_FUNCTIONS__ is None:
        return b
    else:
        return [b, __INSERTIONS__]

def use_output(result):
    if result is None:
        return
    doc = docx.Document()
    for item in result:
        is_loop = list(item.keys()) == ['iterator', 'values', 'items']
        if is_loop:
            iterator = item['iterator']
            iteration_values = item['values']
            for idx, iteration in enumerate(item['items']):
                iteration_value = iteration_values[idx]
                iteration_header = f'{iterator}={iteration_value}:'
                create_with_meta.add_line_to_word(doc, iteration_header, False)
                for line_meta in iteration:
                    latex_line = create_with_meta.construct_line(line_meta)
                    create_with_meta.add_line_to_word(doc, latex_line, True)
        else:
            latex_line = create_with_meta.construct_line(item)
            create_with_meta.add_line_to_word(doc, latex_line, True)
    doc.save('test.docx')
if get_meta:
    result = py_reflection.insert_meta([do_stuff], do_stuff)
    use_output(result)
else:
    some_result = do_stuff()
pass


__END_RESULT__ = do_stuff(__INSERTION_FUNCTIONS__ = [do_stuff])[-1]
import json
with open("Modified Code/__END_RESULT__.json","w") as f:
    f.write(json.dumps(__END_RESULT__,indent = 4))
