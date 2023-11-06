
to do
    for loops <-- need to use code i wrote before
        maybe for now just get first iteration
    
    need meta on what was returned
    
    if statements could be nice
        could display the conditions



limitations
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
    still need to figure out how to initially pass the insertion functions to the top level function


insertions will done at function level (not blocks like loops)
    probably how you would naturally think about how to display things
    allows insertions to just be sent as additional output
        (optional additional input argument to include this additional output)
        this allows the resulting insertions to be structured and not just a long list of equations
    later could optionally add tags (just strings above blocks) that either say what to do, or are labels to reference when saying what to do
        don't show block/line
        for a loop only show one/show all etc.

don't insert code to create the final result (e.g. stings that can be latexifyed)
    gets too complicated when you want to do more complex things
        for example with expressions with units
    instead just return a data structure with the line of code and the value of each variable in that line following execution
        with this structure, you can do whatever you want without writing code to write code, you can just do the thing


nice things about this
    very easy to construct things like expressions with units using a data structure rather than doing it with constructed code
    data structures have maximum information
    can do something else without change the inserted code
    constructed code is pretty easy to generate now
    nested data structure with function calls allows me to easily construct something (like a document with it)
        don't just get a long list of equations

issues
    what if a function calls the same function multiple times (would overwrite the field)
        make it a list instead?
            if doing that, you need some awful if statement asking whether it's a field, if no, create the field before appending
                not too terrible (just have a file with a template for it, see NOTE at bottom)
    what if the output is already a list, i don't think python allows nested list outputs
        NEVER MIND, python DOES allow it :D





implementation
    identical first two lines for all function
    if statement on every top level return (not a return in an inner function)
    for every expression in the code directly, just follow that same data structure format (should be pretty simple)
        could be done either with string construction or tree construction
    for function calls
        check if it's in the list of functions to do insertions <-- remember this is NOT happening in the function's scope, it's happening at top-level
        if no, just don't modify
        if yes:
            add "INCLUDE_INSERTION = True" to its input arguments
            change the output argument to include the second INSERTION output --> "a ="  to "[a, INSERTION] = "
                probably do this with tree manipulation, not string
            would append the output to a field with the key's name being the function's name <-- for modules probably need the full path


still not sure about
    specifying insertions for loops
        for now, just gonna default to the first iteration
        any way to make it know that the inserted code came from the loop (e.g. that it's only one iteration of something repeated)
            if i want to do excel i would anyway need to make an array
        could make an array for each iteration (maybe even ALWAYS do this, and then just get the first outside)
            if there's a label on the loop, that label would be included in the data structure (otherwise just None)
        not sure EXACTLY how to do it, but i think something like this works
    do return values matter (like do they have a special field)
        probably not, could be added if needed
    not sure how to deal with if statements
        could have another layer for the if and else, but then would also need the actual resulting content
        not sure how to structure that
    need to figure out about importing libraries
        would definitely need to save the modified file, and then import the modified file instead 

issue: doesn't say the order the inner func was called relative to the top stuff

```python

def inner_func():
    pass

def some_func():
    c = a + 2
    inner_func()



```


ok this one is MUCH better:
    (didn't like it initially cause the type of it (line or function call) is inferred based on the keys, but who cares, it's constructed code anyway so ik it's perfect :D )
why better
    no more requirement for the if statement on creating array first
    much more importantly, you know the order everything happened in
    also no more need for that weird __TOP__ thing
    just much more condensed and straightforward
    also i have to do the thing with using different keys for loops, so now everything's nice and consistent and simple

```python
{
    "function": some_func,
    "content": [
        {"assignment": "c=a+2", "values": {"c": c, "a": a}}
        {"assignment": "bop = some_module.inner_func()", "values": {"bop": 10}, "function": inner_func, "content": [

        ]}
        {"loop_label": None, "iterator_values":range(5),"loop_expressions": [
            [{"assignment": "", "values": [{},{},{},{},{},{}]}
            {"assignment": "", "values":  [{},{},{},{},{},{}]}] # values is a list for each iteration
        ]}
        # probably not the best/easiest way to do it for loops, but i'll figure that out later
    ]
}
    
``` 

issue is that values 





```python 
# could call it function_name instead of name so it's more explicit
def do_stuff(a, b, INCLUDE_INSERTION = False):
    
    INSERTIONS = {"function_name": "do_stuff", "content": []}
    # INSERTIONS["__TOP__"] = []

    # doing some stuff
    some_output_value = a + b
    INSERTIONS["content"].append({"expression": "some_output_value = a + b", "values": {"a": a, "b": b}})
    
    if INCLUDE_INSERTION:
        return [some_output_value, INSERTIONS]
    else:
        return some_output_value


def outer_doing(f, g, INCLUDE_INSERTION = False):
    
    INSERTIONS = {"function_name": "outer_doing", "content": []}
    # INSERTIONS["__TOP__"] = []

    something_else = f * g

    # INSERTION["__TOP__"].append({"expression": "something_else = f * g", "values": {"f": f, "g": g}})
    INSERTIONS["content"].append({"expression": "something_else = f * g", "values": {"f": f, "g": g}})

    # would have to check (at "compile/insertion time") whether this function (do_stuff) is one of the functions to include insertions
        # if no, just ignore the line (no modifications)
        # if yes, do this stuff

    [my_result, SUB_INSERTION] = do_stuff(3, 4, INCLUDE_INSERTION = True)

    INSERTIONS["content"].append(SUB_INSERTION)


    # NOTE below
    """if "do_stuff" not in INSERTIONS.keys():
        INSERTIONS["do_stuff"] = []
    INSERTIONS["do_stuff"].append(INSERTION)"""

    if INCLUDE_INSERTION:
        return [something_else, INSERTIONS]
    else:
        return something_else

# then you can use the data to do whatever you want

```

NOTE: for doing this easiest way might be:
    have a file with this code (with "FUNCTION_INSERTION" instead of "do_stuff")
    replace "FUNCTION_INSERTION" with the function name (just string replace)
    parse the code to get the tree
    insert this tree

    basically, this makes it so i don't have to build this tree up, which could be pretty annoying



i need to know if a function in a module is one of the functions to do insertions for

issue is that i can't check if two functions are the same by comparing strings
    for example something could be assigned to another functions
    even ignoring that, it would get messy cause of namespaces

INSTEAD, i want to just insert code that checks if the two functions are the same

problem is i need the module to know what functions to insert, can't just insert the names of the functions

so that means i need the module to have access to the functions to insert

i can't pass the functions in due to circular imports

so instead i could pass the functions to insert as an input argument