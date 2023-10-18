import itertools
from abc import ABC, abstractmethod
from enum import Enum

MAX_ROUNDS = 5
NUM_ARGS = 2

DeadEndProgramException = Exception

class Type(Enum):
    Number = 0
    String = 1

type Example = tuple[dict[str, Expression], Expression]

# An output is a tuple the size of NUM_ARGS, where each value represents the value of an expression on each one of the examples.
type Outputs = tuple

class Expression:
    def __init__(self, string: str, values: Outputs, myType: Type):
        if len(values) != NUM_ARGS:
            raise Exception("Wrong number of arguments")
        self.string = string
        self.values: Outputs = values
        self.type = myType

    def __str__(self):
        return str(self.string)

    def __hash__(self):
      return hash(tuple(self.values))

    def __eq__(self, other):
        return self.values == other.values

class Argument(Expression):
    def __init__(self, name, myType, examples):
        super().__init__(name, [input[name] for input, _ in examples], myType)

class NumArgument(Argument):
    def __init__(self, name, examples):
        super().__init__(name, Type.Number, examples)

class StringArgument(Argument):
    def __init__(self, name, examples):
        super().__init__(name, Type.String, examples)

class Constant(Expression):
    def __init__(self, value, myType):
        super().__init__(value, [value for _ in range(NUM_ARGS)], myType)

class NumConstant(Constant):
    def __init__(self, value):
        super().__init__(value, Type.Number)

class StringConstant(Constant):
    def __init__(self, value):
        super().__init__(value, Type.String)

class Operator(ABC):
    @abstractmethod
    # String representation of the operation on args
    def string(self, args) -> str:
        pass
    
    @abstractmethod
    # Value of the operation on args
    def evaluate(self, args):
        pass
    
    @abstractmethod
    # List of types of the arguments (length encodes parity)
    def args(self) -> list[Type]:
        pass
    
    @abstractmethod
    # Type of the return value
    def return_type(self) -> Type:
        pass

class BinaryNumberOperator(Operator):
    @abstractmethod
    def string(self, args):
        pass
    @abstractmethod
    def evaluate(self, args):
        pass
    def args(self):
        return [Type.Number, Type.Number]
    def return_type(self):
        return Type.Number

class Add(BinaryNumberOperator):
    def string(self, args):
        return f"add({args[0]}, {args[1]})"
    def evaluate(self, args):
        return eval(f"{args[0]} + {args[1]}")

class Subtract(BinaryNumberOperator):
    def string(self, args):
        return f"subtract({args[0]}, {args[1]})"
    def evaluate(self, args):
        return eval(f"{args[0]} - {args[1]}")
    
class Multiply(BinaryNumberOperator):
    def string(self, args):
        return f"multiply({args[0]}, {args[1]})"
    def evaluate(self, args):
        return eval(f"{args[0]} * {args[1]}")
    
class Divide(BinaryNumberOperator):
    def string(self, args):
        return f"divide({args[0]}, {args[1]})"
    def evaluate(self, args):
        try:
          return eval(f"{args[0]} // {args[1]}")
        except ZeroDivisionError:
            raise DeadEndProgramException()

class Concat(Operator):
    def string(self, args):
        return f"concat({args[0]}, {args[1]})"
    def evaluate(self, args):
        return f"{args[0]}{args[1]}"
    def args(self):
        return [Type.String, Type.String]
    def return_type(self):
        return Type.String
    
class Left(Operator):
    def string(self, args):
        return f"left({args[0]}, {args[1]})"
    def evaluate(self, args):
        return args[0][:args[1]]
    def args(self):
        return [Type.String, Type.Number]
    def return_type(self):
        return Type.String

class Right(Operator):
    def string(self, args):
        return f"right({args[0]}, {args[1]})"
    def evaluate(self, args):
        return args[0][-args[1]:]
    def args(self):
        return [Type.String, Type.Number]
    def return_type(self):
        return Type.String
    
SPACE = StringConstant(" ")
ONE = NumConstant(1)
TWO = NumConstant(2)

type ProgramBank = set[Expression]

def synthesize(
        primitives: ProgramBank,
        production_rules: list[Operator],
        examples: list[Example]) -> str:
    bank: ProgramBank = primitives
    target: Outputs = tuple(output.values[0] for _, output in examples)

    for i in range(MAX_ROUNDS):
      # Generate expressions with production rules
      for rule in production_rules:
          parity = len(rule.args())
          # 2D list where each row represents the candidates for a given argument
          args: list[list[Expression]] = []
          for arg_index in range(parity):
              arg_type = rule.args()[arg_index]
              candidates_for_this_index = [e for e in bank if e.type == arg_type]
              args.append(candidates_for_this_index)
          # Generate all possible combinations of arguments using a cartesian product of the candidates
          for args_tuple in itertools.product(*args):
              # Create a new expression
              try:
                # determine the value of the new expression on each example
                values = []
                for i in range(len(examples)):
                    arg_values_on_example = [arg.values[i] for arg in args_tuple]
                    val = rule.evaluate(arg_values_on_example)
                    values.append(val)
                new_expr = Expression(
                    rule.string([arg.string for arg in args_tuple]),
                    tuple(values),
                    rule.return_type()
                )
                # Check if this expression is the solution
                if new_expr.values == target:
                    return new_expr.string
                # Add the program to the bank, which automatically prunes equivalent programs
                bank.add(new_expr)
              except DeadEndProgramException:
                pass

# ARITHMETIC LANGUAGE
examples: list[Example] = [
    ({"x": NumConstant(1), "y": NumConstant(2)}, NumConstant(6)),
    ({"x": NumConstant(2), "y": NumConstant(3)}, NumConstant(9)),
]

arg_x = NumArgument('x', examples)
arg_y = NumArgument('y', examples)

# Define the primitives and production rules
primitives: ProgramBank = set([arg_x, arg_y])
production_rules: list[Operator] = {Add(), Subtract(), Multiply(), Divide()}

print("solution:", synthesize(primitives, production_rules, examples))

# STRING MANIPULATION LANGUAGE
examples: list[Example] = [
    ({"x": StringConstant("hello"), "y": StringConstant("world")}, StringConstant("hello world")),
    ({"x": StringConstant("world"), "y": StringConstant("domination")}, StringConstant("world domination")),
]

arg_x = StringArgument('x', examples)
arg_y = StringArgument('y', examples)

# Define the primitives and production rules
primitives: ProgramBank = set([arg_x, arg_y, SPACE, ONE, TWO])
production_rules: list[Operator] = {Concat(), Left(), Right()}

print("solution:", synthesize(primitives, production_rules, examples))