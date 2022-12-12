#These tests are for use with https://github.com/efforting-tech/python-test-framework
from query_set import *
from query_parser import *
test1 = {'hello', 'earth'}

class simple_queries(Test):
	assert contains_element('hello').query(test1).match == {'hello'}

class compound_queries(Test):
	assert (contains_element('hello') & contains_element('earth')).query(test1).match == test1
	assert (contains_element('hello') | contains_element('stuff')).query(test1).match == {'hello'}
	assert (~contains_element('hello')).query(test1) is None

	assert (contains_element('hello') ^ contains_element('stuff')).query(test1).match == {'hello'}
	assert (contains_element('hello') ^ contains_element('earth')).query(test1) is None


class parser(Test):

	to_test = (
		('hello ^ world', 				'(hello) ^ (world)'),
		('hello & (world | stuff)', 	'(hello) & ((world) | (stuff))'),
		('hello & world | stuff', 		'((hello) & (world)) | (stuff)'),
		('(hello & world) | stuff', 	'((hello) & (world)) | (stuff)'),
	)

	for query, representation in to_test:
		class sub_test(Test, index=query):
			assert repr(parse_query(query)) == representation, repr(parse_query(query))

