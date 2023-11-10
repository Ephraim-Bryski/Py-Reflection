import insert_code

get_meta = True

def some_other_func(a):
    x = a + 3
    return x

def do_stuff():
    print('boop')
    result = some_other_func(7)
    return result



if get_meta:
    result = insert_code.insert_code([some_other_func,do_stuff], do_stuff)
else:
    some_result = do_stuff()
# this will then 