class match:
	def __init__(self, query, match):
		self.query = query
		self.match = match

class base_query:
	def __invert__(self):
		return logical_not(self)

	def __or__(self, other):
		return logical_or(self, other)

	def __and__(self, other):
		return logical_and(self, other)

	def __xor__(self, other):
		return logical_xor(self, other)


class contains_element(base_query):
	def __init__(self, element):
		self.element = element

	def query(self, collection):
		if self.element in collection:
			return match(self, {self.element})

	def __repr__(self):
		return f'{self.element}'

class unary_operation(base_query):
	def __init__(self, reference):
		self.reference = reference


class binary_operation(base_query):
	def __init__(self, left, right):
		self.left = left
		self.right = right





class logical_not(unary_operation):
	def __invert__(self):
		return self.reference

	def query(self, collection):
		if not self.reference.query(collection):
			return match(self, set())

	def __repr__(self):
		return f'~({self.reference})'

class logical_or(binary_operation):
	def query(self, collection):
		result = set()
		if left := self.left.query(collection):
			result |= left.match

		if right := self.right.query(collection):
			result |= right.match

		if left or right:
			return match(self, result)

	def __repr__(self):
		return f'({self.left}) | ({self.right})'

class logical_xor(binary_operation):
	def query(self, collection):
		result = set()
		if left := self.left.query(collection):
			result |= left.match

		if right := self.right.query(collection):
			result |= right.match

		if left and right:
			return

		elif left or right:
			return match(self, result)

	def __repr__(self):
		return f'({self.left}) ^ ({self.right})'

class logical_and(binary_operation):
	def query(self, collection):
		if (left := self.left.query(collection)) is None:
			return
		if (right := self.right.query(collection)) is None:
			return

		return match(self, left.match | right.match)

	def __repr__(self):
		return f'({self.left}) & ({self.right})'
