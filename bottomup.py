import itertools

MAX_DEPTH = 100

def synthesize(primitives, production_rules, examples):
    expressions = starting_expressions(primitives, examples)
    target = tuple(output for _, output in examples)

    for i in range(MAX_DEPTH):
       new_expressions = generate_expressions(expressions, production_rules)
       print(new_expressions)
       found, pruned, solution = prune(target, expressions, new_expressions, examples)
       if found:
            return solution
       else:
        expressions.update(pruned)

       print(f"{i}: {len(expressions)}")
           
# Return a dict mapping each primitive to a tuple of the value of the primitive evaluated on each of the examples. Since the primitives just evaluate to their input values, this is just the examples themselves. Non-arguments (constants) evaluate to themselves on all examples.
# Example: {'{x}': (1, 2, 3), '{y}': (2, 3, 4)}
def starting_expressions(primitives, examples):
    value = lambda input, primitive: input[primitive] if primitive in input else primitive
    return {primitive: tuple(value(input, primitive) for input, _ in examples) for primitive in primitives}

def generate_expressions(expressions, production_rules):
    new_expressions = set()

    # Generate expressions with production rules
    for expr1, expr2 in itertools.product(expressions.keys(), repeat=2):
       for rule in production_rules:
          try:
            new_expressions.add(rule(expr1, expr2))
          except:
             pass

    return new_expressions

def evaluate(expression, input):
    return eval(expression.format(**input))
       

# Returns a 3-tuple with the following parts:
# (1) whether the solution was found while pruning
# (2) the pruned expressions
# (3) the solution expression
# The (1) term will always be populated, but (2) and (3) are conditionally populated depending on whether the solution was found while pruning.
# Pruning is performed by finding all the `new` expressions that evaluate equivalently to an `existing` or `pruned` expression on the `examples`.
def prune(target, existing, new, examples):
    pruned = {}

    for expr in new:
        try:
            # a tuple of the values of the new expression evaluated on each of the examples
            outputs = tuple(evaluate(expr, input) for input, _ in examples)
            if outputs == target:
                return (True, None, expr)
            if outputs not in existing.values() and outputs not in pruned.values():
                pruned[expr] = outputs
        except:
            pass
    
    return (False, pruned, None)

# ARITHMETIC LANGUAGE

# Define the rules
def add(x, y): return f"({x} + {y})"

def subtract(x, y): return f"({x} - {y})"

def multiply(x, y): return f"({x} * {y})"

def divide(x, y): return f"({x} // {y})"

# Define the primitives and production rules
primitives = {'{x}', '{y}', '{z}'}
production_rules = {add, subtract, multiply, divide}

# Define the examples
examples = [
    ({'x': 1, 'y': 2, 'z': 3}, 10),
    ({'x': 2, 'y': 3, 'z': 5}, 42),
]

# Run the algorithm
#print(f"\n\nResult: {synthesize(primitives, production_rules, examples)}")

# STRING MANIPULATION LANGUAGE

# Define the rules

# Merge two strings
def concat(x: str, y: str) -> str:
  return f"{x}{y}"

# Get the left-most n characters of a string
def left(x: str, n: int) -> str:
  return f"{x[:n]}"

# Get the right-most n characters of a string
def right(x: str, n:int) -> str:
  return f"{x[-n:]}"

def space() -> str:
  return " "

# Define the primitives and production rules
CONSTANTS = {"space()", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"}
ARGS = {'{x}', '{y}'}
primitives = ARGS
production_rules = {concat}

# Define the examples
examples = [
   ({'x': "hello", 'y': "world"}, "helloworld"),
   ({'x': "world", 'y': "domination"}, "worlddomination"),
]

# Run the algorithm
print(f"\n\nResult: {synthesize(primitives, production_rules, examples)}")