import insert_code
import importlib
import sample_module
import my_module

importlib.reload(insert_code)

get_meta = True

def some_other_func(a):
    x = a + 3
    return x

def pls_dont_insert(g):
    f = g+4
    return f

def do_stuff():
    print('boop')
    result = some_other_func(7)
    another_result = pls_dont_insert(8)
    bop = sample_module.inner(3)
    return another_result

def use_output(result):

    # all top-level functions to use output needs to start with this
    if result is None: return

    for item in result:
        print(item)

if get_meta:
    result = insert_code.insert_code([my_module.A_func, do_stuff], do_stuff)
    use_output(result)
else:
    some_result = do_stuff()
# this will then 
pass