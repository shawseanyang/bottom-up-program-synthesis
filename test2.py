class MyClass:
  def __init__(self, value):
    self.value = value

  # hash
  def __hash__(self):
    return hash(self.value)

  def __eq__(self, other):
    if isinstance(other, MyClass):
      return self.value == other.value
    return False

my_set = {MyClass(1), MyClass(2), MyClass(3)}

other_set = {MyClass(1)}

my_set.update(other_set)

print([s.value for s in my_set])