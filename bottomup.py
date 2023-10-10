import itertools

def synthesize(primitives, production_rules, examples):
    expressions = starting_expressions(primitives, examples)
    target = tuple(output for _, output in examples)

    for i in range(100):
       new_expressions = generate_expressions(expressions, production_rules)
       found, pruned, solution = prune(target, expressions, new_expressions, examples)
       if found:
            return solution
       else:
        expressions.update(pruned)

       print(f"{i}: {len(expressions)}")
           
# Return a dict mapping each primitive to a tuple of the value of the primitive evaluated on each of the examples. Since the primitives just evaluate to their input values, this is just the examples themselves.
# Example: {'{x}': (1, 2, 3), '{y}': (2, 3, 4)}
def starting_expressions(primitives, examples):
    return {primitive: tuple(input[primitive[1:-1]] for input, _ in examples) for primitive in primitives}

def generate_expressions(expressions, production_rules):
    new_expressions = set()

    # Generate expressions with production rules
    for expr1, expr2 in itertools.product(expressions.keys(), repeat=2):
       for rule in production_rules:
          new_expressions.add(rule(expr1, expr2))

    return new_expressions

def evaluate(expression, input):
    return eval(expression.format(**input))

# Returns a 3-tuple with the following parts:
# (1) whether the solution was found while pruning
# (2) the pruned expressions
# (3) the solution expression
# The (1) term will always be populated, but (2) and (3) are conditionally populated depending on whether the solution was found while pruning.
# Pruning is performed by finding all the `new` expressions that evaluate equivalently to an `existing` expression on the `examples`.
def prune(target, existing, new, examples):
    pruned = {}

    for expr in new:
        try:
            # a tuple of the values of the new expression evaluated on each of the examples
            outputs = tuple(evaluate(expr, input) for input, _ in examples)
            if outputs == target:
                return (True, None, expr)
            if outputs not in existing.values():
                pruned[expr] = outputs
        except:
            pass
    
    return (False, pruned, None)

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
    ({'x': 2, 'y': 3, 'z': 8}, 42),
]

# Run the algorithm
print(f"\n\nResult: {synthesize(primitives, production_rules, examples)}")