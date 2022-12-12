#!/bin/env python3
from pathlib import Path
import re, argparse, os, sys
from collections import defaultdict
from query_parser import parse_query

#note for myself regarding implement tabcompletion at some point:
#	function _idgrep_complete { IFS=$'\n' COMPREPLY=( $(idgrep --complete $*) ); }; complete -r idgrep; complete -F _idgrep_complete idgrep;

#Known limitations
#	Overlapping directories are processed twice although the files themselves are not


class suffix_value:
	def __init__(self, value):
		value, suffix = re.compile(r'(\d+)(.*)').match(value).groups()

		if suffix:
			try:
				self.value = int(value) * self.suffix_table[suffix.lower()]
			except KeyError as ke:
				raise Exception(f'The suffix `{suffix}´ is not recognized by the type `{self.__class__.__name__}´. Valid suffixes: {", ".join(sorted(self.suffix_table))}')

		else:
			self.value = int(value)

	def __int__(self):
		return self.value

class file_size(suffix_value):
	suffix_table = dict(
		k = 2 << 10,
		m = 2 << 20,
		g = 2 << 30,
		t = 2 << 40,
	)

class cardinal(suffix_value):
	suffix_table = dict(
		k = 10 ** 3,
		m = 10 ** 6,
	)


class search_result:
	def __init__(self, search, result, operation, *arguments):
		self.search = search
		self.result = result
		self.operation = operation
		self.arguments = arguments


class search:
	id_pattern = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')

	def __init__(self, max_size, max_identifiers):
		self.max_size = max_size
		self.max_identifiers = max_identifiers


		self.by_id = defaultdict(set)
		self.by_file = dict()


	def process_directory(self, path, glob):
		for file in Path(path).glob(glob):

			#Idea here is that later we will have a timed event so if we have been doing something for a while we start outputting some stats about the process - this is still just a concept
			#  f'Processing file {file}'

			if file in self.by_file:
				#Already done this one
				continue

			if file.is_file():

				if file.stat().st_size > self.max_size:
					#todo - optionally log
					continue

				try:
					found_ids = set(m.group() for m in self.id_pattern.finditer(file.read_text()))
				except Exception:
					#todo - optionally log
					found_ids = None


				if found_ids:
					if len(found_ids) > self.max_identifiers:
						#todo - optionally log
						continue

					self.by_file[file] = found_ids
					for id in found_ids:
						self.by_id[id].add(file)

	def find_intersection(self, ids_to_match):
		result = None
		for id in ids_to_match:
			f = self.by_id.get(id)
			if f is not None:
				if result is None:
					result = set(f)
				else:
					result &= f

		return search_result(self, result, 'find_intersection', ids_to_match)

	def find_union(self, ids_to_match):
		result = set()
		for id in ids_to_match:
			if f := self.by_id.get(id):
				result |= f

		return search_result(self, result, 'find_union', ids_to_match)

	def get_complement(self, matched):
		result = set(self.by_file) - matched.result
		return search_result(self, result, 'get_complement', matched)


	def id_by_re(self, pattern):
		return set(filter(re.compile(pattern).match, self.by_id))

	def id_by_glob(self, pattern):
		if not '*' in pattern:
			return {pattern}
		re_pattern = re.escape(pattern).replace(r'\*', r'.*')
		return set(filter(re.compile(re_pattern).match, self.by_id))


	def print_sorted_list(self, collection):
		for index, item in enumerate(sorted(collection), 1):
			print(f'{index}\t{item}')



if len(sys.argv) >= 2 and sys.argv[1] == '--complete':
	print(f'args: {sys.argv[2:]}')
	exit()



parser = argparse.ArgumentParser(add_help=False)

parser.add_argument('paths', nargs='*', type=Path)

parser.add_argument('-p', '--file-pattern', default='**/*')
parser.add_argument('-l', '--limit-size', type=file_size, default='1M')
parser.add_argument('-i', '--limit-identifiers', type=cardinal, default='1k')



action = parser.add_mutually_exclusive_group()
action.add_argument('--help', action='store_const', const='help', dest='action', default='query')
action.add_argument('--file-id-count', action='store_const', const='file_id_count', dest='action')

presentation = parser.add_mutually_exclusive_group()
presentation.add_argument('--group-by-id', action='store_const', const='group_by_id', dest='presentation', default='files_and_optional')

sorting = parser.add_mutually_exclusive_group()
sorting.add_argument('--sort-by-name', action='store_true')
sorting.add_argument('--sort-by-count', action='store_true')
sorting.add_argument('--sort-by-size', action='store_true')

sorting_order = parser.add_mutually_exclusive_group()
sorting_order.add_argument('--ascending', '--asc', action='store_false', dest='reversed_sort', default=False)		#When action is store_false, default is automatically True
sorting_order.add_argument('--descending', '--desc', action='store_true', dest='reversed_sort')


def sorted_collection(collection, reverse, key):
	return sorted(collection, key=key, reverse=reverse)


try:
	qp = sys.argv.index('--')
	pending_args = sys.argv[1:qp]
	query = sys.argv[qp+1:]
except ValueError:
	query = ()
	pending_args = sys.argv[1:]


args = parser.parse_args(pending_args)


s = search(
	max_size = int(args.limit_size),
	max_identifiers = int(args.limit_identifiers),
)


def process_paths():
	for path in args.paths or (os.getcwd(),):
		s.process_directory(path, args.file_pattern)


if args.action == 'file_id_count':

	process_paths()

	entries = s.by_file.items()

	if args.sort_by_name:
		result = sorted_collection(entries, args.reversed_sort, lambda i: i[0])
	elif args.sort_by_count:
		result = sorted_collection(entries, args.reversed_sort, lambda i: len(i[1]))
	else:
		result = entries

	for file, fids in result:
		print(file, len(fids))


elif args.action == 'query':
	if query:
		q = parse_query(' '.join(query))


		process_paths()

		result = list()

		for file, ids in s.by_file.items():

			if m := q.query(ids):
				result.append((file, m.match))

		if args.presentation == 'files_and_optional':
			for file, match in result:
				print(file, match)

		elif args.presentation == 'group_by_id':

			match_by_id = defaultdict(set)
			for file, match in result:
				for id in match:
					match_by_id[id].add(file)

			for id, files in sorted(match_by_id.items()):
				print(id)
				for file in files:
					print(f'\t{file}')

		else:
			raise Exception(args.presentation)

	else:
		parser.print_help()

elif args.action == 'help':
	parser.print_help()
else:
	raise Exception()

