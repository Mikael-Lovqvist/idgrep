import query_set
from collections import deque


def parse_query(text):

	def tokenize():
		pending_identifier = ''

		def possible_identifier():
			nonlocal pending_identifier
			if pending_identifier:
				assert pending_identifier.isidentifier()
				yield pending_identifier
			pending_identifier = ''


		for c in text:
			if c.isalnum():
				pending_identifier += c
			elif c.isspace():
				yield from possible_identifier()
			elif c in '()!~|&^':
				yield from possible_identifier()
				yield c
		yield from possible_identifier()


	stack = deque((deque(),))

	for token in tokenize():
		if token == '(':
			stack.append(deque())
		elif token == ')':
			[sub_expression] = stack.pop()
			stack[-1].append(sub_expression)
		elif token in '!~':
			stack[-1].append(query_set.logical_not)
		elif token == '|':
			stack[-1].append(query_set.logical_or)
		elif token == '&':
			stack[-1].append(query_set.logical_and)
		elif token == '^':
			stack[-1].append(query_set.logical_xor)
		else:	#identifier
			stack[-1].append(query_set.contains_element(token))

		#Check stack

		lse = stack[-1]
		mutation = True
		while mutation:
			mutation = False

			if len(lse) >= 3 and isinstance(lse[-3], query_set.base_query) and isinstance(lse[-2], type) and isinstance(lse[-1], query_set.base_query) and issubclass(lse[-2], query_set.binary_operation):
				right, op, left = lse.pop(), lse.pop(), lse.pop()
				lse.append(op(left, right))
				mutation = True

			if len(lse) >= 2 and isinstance(lse[-2], type) and isinstance(lse[-1], query_set.base_query) and issubclass(lse[-2], query_set.unary_operation):
				ref, op = lse.pop(), lse.pop()
				#Get rid of double logical not
				if op is query_set.logical_not and type(ref) is query_set.logical_not:
					lse.append(ref.reference)
				else:
					lse.append(op(ref))
				mutation = True

	assert len(stack) == 1
	[[result]] = stack

	return result


