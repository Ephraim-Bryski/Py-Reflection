import insert_code
get_meta = True

def some_other_func(a):
    __INSERTIONS__ = []
    x = a + 3
    __INSERTIONS__.append({'source_code': 'x = a + 3', 'values': {'x': x, 'a': a}})
    if __INSERTION_FUNCTIONS__ is None:
        return x
    else:
        return [x, __INSERTIONS__]

def do_stuff():
    __INSERTIONS__ = []
    print('boop')
    if __INSERTION_FUNCTIONS__ is not None and some_other_func in __INSERTION_FUNCTIONS__:
        [result, __META_OUTPUT__] = some_other_func(7)
        __INSERTIONS__.append({'function': 'some_other_func', 'content': __META_OUTPUT__})
    else:
        result = some_other_func(7)
    __INSERTIONS__.append({'source_code': 'result = some_other_func(7)', 'values': {'result': result}})
    if __INSERTION_FUNCTIONS__ is None:
        return result
    else:
        return [result, __INSERTIONS__]
if get_meta:
    result = insert_code.insert_code([some_other_func, do_stuff], do_stuff)
else:
    some_result = do_stuff()

__INSERTION_FUNCTIONS__ = [some_other_func,do_stuff]

__END_RESULT__ = do_stuff()[-1]
import json
with open("Modified Code/__END_RESULT__.json","w") as f:
    f.write(json.dumps(__END_RESULT__,indent = 4))
