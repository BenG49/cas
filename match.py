from expr import Expr, Pattern
from collections import Counter

class Match:
	def __init__(self, expr: Expr):
		self.expr = expr
		self.ids = [id(expr)]

	def merge(self, other):
		if isinstance(other, Match) and self.expr == other.expr:
			for i in other.ids:
				if i not in self.ids:
					self.ids.append(i)
			for i in self.ids:
				if i not in other.ids:
					other.ids.append(i)
	
	# NOTE: this is here just for Counter in collapse()
	def __hash__(self) -> int:
		return self.expr.__hash__()

	def __iter__(self):
		return self.ids.__iter__()

	def __eq__(self, other) -> bool:
		if isinstance(other, Expr):
			return self.expr == other
		elif isinstance(other, Match):
			return self.expr == other.expr
		return False

	def deep_eq(self, other) -> bool:
		return isinstance(other, Match) and self.expr == other.expr and sorted(self.ids) == sorted(other.ids)

	def __lt__(self, other) -> bool:
		if isinstance(other, Match):
			return self.expr < other.expr
		elif isinstance(other, Expr):
			return self.expr < other

	def __str__(self) -> str:
		return f'{self.expr}[{", ".join(map(hex, self.ids))}]'

	def __repr__(self) -> str:
		return self.__str__()

class MatchData:
	def make_pair(pattern: Pattern, expr: [Expr, tuple[Expr]]):
		val = tuple(Match(e) for e in expr) if type(expr) is tuple else Match(expr)
		return MatchData({str(pattern): val})

	def __init__(self, init: dict[str, Match]=dict()):
		self.data = init

	def __getitem__(self, key: [Pattern, str]) -> Expr:
		return self.data[str(key) if isinstance(key, Pattern) else key]
	
	def __setitem__(self, key: [Pattern, str], m: Match):
		self.data[str(key) if isinstance(key, Pattern) else key] = m

	# returns: successful match
	def populate_matches(self, expr: Expr, match: Expr) -> bool:
		# MATCH IS PATTERN
		if isinstance(match, Pattern) and match.matches(expr):
			return self.add(MatchData.make_pair(match, expr))
		
		# ROOTS COMPELTELY EQUAL
		elif match == expr:
			return True
	
		# LEAF
		elif expr.is_leaf() or match.op != expr.op or len(match) > len(expr):
			return False
		
		# MATCH ROOTS WITH NON-ASSOCIATIVE OPERATORS
		# CHECK CORRESPONDING CHILDREN
		elif not match.op.is_associative():
			if len(match) != len(expr):
				return False

			local_matches = MatchData()
			for i in range(len(match)):
				check = MatchData()
				if not check.populate_matches(expr[i], match[i]) or not local_matches.add(check):
					break
			else:
				return self.add(local_matches)
			
			# CHECK THROUGH CHILDREN
			for child in expr:
				child_match_data = MatchData()
				if child_match_data.populate_matches(child, match) and self.add(child_match_data):
					return True
			
			return False

		# MATCH ROOTS WITH ASSOCIATIVE OPERATORS
		marked_indicies = []

		def get_matches_children(match_list: list[Expr]) -> [MatchData, None]:
			local_matches = MatchData()
			for match_expr in match_list:
				for i, child in enumerate(expr):
					if i not in marked_indicies:
						check = MatchData()
						if check.populate_matches(child, match_expr) and local_matches.add(check):
							marked_indicies.append(i)
							break
				else:
					# if match wasn't found
					break
			else:
				# match was found for every expr
				return local_matches

		match_exprs = [c for c in match if not c.is_pattern()]
		match_patterns = [c for c in match if c.is_pattern()]

		local_matches = get_matches_children(match_exprs)
		if local_matches is None:
			return False

		if len(match_patterns) > 1:
			# first check if any patterns have only one possibility due to match restrictions
			for pattern in match_patterns:
				pattern_possible = [expr[i] for i in range(len(expr)) if not i in marked_indicies and pattern.matches(expr[i])]
				if len(pattern_possible) == 1:
					e = pattern_possible[0]
					self.add(MatchData.make_pair(pattern, e))
					marked_indicies.append(expr.children.index(e))

					match_patterns.remove(pattern)

			# register options to matchdata
			expr_remaining = [expr[i] for i in range(len(expr)) if i not in marked_indicies]

			if len(match_patterns) != len(expr_remaining):
				return False
			
			for pattern in match_patterns:
				remaining = tuple(expr[i] for i in range(len(expr)) if not i in marked_indicies and pattern.matches(expr[i]))
				if not local_matches.add(MatchData.make_pair(pattern, remaining)):
					print('WOMP WOMP', 'couldnt register options', remaining, 'for pattern', pattern)

		elif not local_matches.add(get_matches_children(match_patterns)):
			return False

		return self.add(local_matches)
	
	# modifies self and other
	# returns: successful combine
	def add(self, other) -> bool:
		if not isinstance(other, MatchData):
			return False

		for key in set(self.keys()).intersection(set(other.keys())):
			if self[key] == other[key]:
				if type(self[key]) is tuple:
					# same pattern with same options: add both ids to both patterns
					if len(self[key]) == 2:
						merged = self[key][0]
						merged.merge(self[key][1])

						self[key] = merged
						other[key] = merged
				else:
					# combine same expr but different ids
					self[key].merge(other[key])

			# resolve different exprs bound to same pattern
			else:
				# collapse different options
				if type(self[key]) is tuple or type(other[key]) is tuple:
					self_options = self[key] if type(self[key]) is tuple else tuple([self[key]])
					other_options = other[key] if type(other[key]) is tuple else tuple([other[key]])

					common_expr = set(self_options).intersection(set(other_options))

					# no common expressions
					if len(common_expr) == 0:
						return False
					# too many common expressions
					elif len(common_expr) > 1:
						continue
					else:
						common_expr = list(common_expr)[0]

					# get IDs from both options
					common_expr.merge(next(o for o in self_options if o == common_expr))
					common_expr.merge(next(o for o in other_options if o == common_expr))
					
					self[key] = common_expr
					other[key] = common_expr

					self.remove_option(self_options, common_expr)
					other.remove_option(other_options, common_expr)
				else:
					# attempting to combine different exprs that aren't options
					return False

		self.data = self.data | other.data
		
		return True

	def remove_option(self, target: tuple[Match], remove: Match):
		for pattern in self.keys():
			if type(self[pattern]) is tuple and target == self[pattern]:
				self.data[pattern] = tuple(x for x in self[pattern] if x != remove)
				
				if len(self[pattern]) == 1:
					self[pattern] = self[pattern][0]

	def collapse(self):
		# remove some options by logical elimination
		for options, count in Counter(self.values()).items():
			if type(options) is tuple and len(options) == count:
				# remove these options from all other options
				for key, value in self.items():
					if type(value) is tuple and options != value and set(options).issubset(set(value)):
						self[key] = tuple(v for v in value if v not in options)

		# choose first option for all remaining options
		for pattern, match in self.items():
			if type(match) is tuple:
				out = match[0]
				self.remove_option(match, match[0])
				self[pattern] = out

		return self

	def items(self):
		return self.data.items()

	def keys(self):
		return self.data.keys()

	def values(self):
		return self.data.values()

	def __len__(self) -> int:
		return len(self.data)

	def __str__(self) -> str:
		return str(self.data)

	def __repr__(self) -> str:
		return self.__str__()
