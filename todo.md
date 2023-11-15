


limitations

    nothing for if statements

    no nesting (e.g. nested loops)

    doesn't get data from multiple assignment like: a=b=3
    doesn't get data from function calls that's part of a larger expression:
        a=do_stuff() --> OK
        a=do_stuff()+3 --> NOT OK
        still gets value data, but doesn't get do_stuff data, even if it's one of the functions to get stuff from
    doesn't consider nested functions
    won't get the values of an attribute
        a=some_object.some_attribute+8 --> {'a':a}, but NOTHING for some_object.some_attribute
            which is kind of fine, it just won't sub that in
    kind of minor but... say boop() has not outputs
        a = boop() --> a is just None
        BUT after insertion:
        [a, OPTIONAL_OUTPUT] = boop() --> error cause None can't be expanded
        so basically you can't assign an output to something that didn't return anything to the added output parameter


