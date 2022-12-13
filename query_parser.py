import query_set
from collections import deque


#todo: make sure [] is balanced in fnmatch pattern

def parse_query(text, ignore_case=False):

	def tokenize():
		pending_pattern = ''

		def possible_pattern():
			nonlocal pending_pattern
			if pending_pattern:
				#We skip testing for identifier here since it gets complicated with the fnmatch stuff - we can possibly do something later on
				#	since it is nice to be able to inform the user when problems are detected.
				yield pending_pattern
			pending_pattern = ''


		for c in text:
			if c.isalnum() or c in '*?[]':
				pending_pattern += c
			elif c.isspace():
				yield from possible_pattern()
			elif c in '()!~|&^':
				yield from possible_pattern()
				yield c
		yield from possible_pattern()


	stack = deque((deque(),))

	for token in tokenize():
		if token == '(':
			stack.append(deque())
		elif token == ')':
			[sub_expression] = stack.pop()	#todo: make sure that an empty stack raises a parserexception (to be defined)
			stack[-1].append(sub_expression)
		elif token in '!~':
			stack[-1].append(query_set.logical_not)
		elif token == '|':
			stack[-1].append(query_set.logical_or)
		elif token == '&':
			stack[-1].append(query_set.logical_and)
		elif token == '^':
			stack[-1].append(query_set.logical_xor)
		else:	#pattern
			stack[-1].append(query_set.contains_element(token, ignore_case=ignore_case))

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


