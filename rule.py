from expr import Expr, Pattern
from copy import deepcopy
from match import MatchData

'''
Rewrite rules
'''

class Rule:
	def __init__(self, input: [Pattern, Expr], output: [Pattern, Expr]):
		self.input = input
		self.output = output
	
	def get_pattern_matches(expr: Expr, match: Expr, match_data: MatchData):
		# MATCH IS PATTERN
		if isinstance(match, Pattern):
			return match_data.register(match, expr)
		
		# ROOTS COMPELTELY EQUAL
		elif match == expr:
			return match_data
	
		# LEAF
		elif expr.is_leaf():
			return None
		
		# CHECK THROUGH CHILDREN
		elif match.op != expr.op or len(match) > len(expr):
			# TODO: finds first match
			for child in expr:
				child_match_data = Rule.get_pattern_matches(match, child, MatchData())
				if child_match_data:
					return match_data.combine(child_match_data)
			
			return None
		
		# MATCH ROOTS WITH NON-ASSOCIATIVE OPERATORS
		elif not match.op.is_associative():
			if len(match) != len(expr):
				return None

			local_matches = MatchData()
			for i in range(len(match)):
				check = Rule.get_pattern_matches(expr[i], match[i], MatchData())

				if check is None:
					return None

				if local_matches.combine(check) is None:
					return None

			return match_data.combine(local_matches)

		# MATCH ROOTS WITH ASSOCIATIVE OPERATORS
		marked_indicies = []

		def get_matches_children(match_list: list[Expr]) -> [MatchData, None]:
			local_matches = MatchData()
			for match_expr in match_list:
				for i, child in enumerate(expr):
					if i not in marked_indicies:
						check = Rule.get_pattern_matches(child, match_expr, MatchData())
						if check is not None:
							local_matches.combine(check)
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

		local_match = get_matches_children(match_exprs)
		if local_match is None:
			return None

		if len(match_patterns) > 1:
			expr_remaining = [expr[i] for i in range(len(expr)) if i not in marked_indicies]

			if len(match_patterns) != len(expr_remaining):
				return None
			
			for pattern in match_patterns:
				local_match.register(pattern, tuple(expr_remaining))
		else:
			local_match.combine(get_matches_children(match_patterns))

		return match_data.combine(local_match)

	def apply(self, expr: Expr) -> Expr:
		# get pattern/tree pairs
		matches = Rule.get_pattern_matches(expr, self.input, MatchData())

		# no match
		if matches is None:
			return expr

		matches.collapse()

		copy = deepcopy(expr)

		# no pattern vars
		if len(matches) == 0:
			return copy.replace(self.input, self.output)

		# put patterns in place in original expression
		for p, output in matches.items():
			copy = copy.replace(output, Pattern(p))

		# make rule substitution
		copy = copy.replace(self.input, self.output)

		# substitute original expressions for new patterns
		for p, output in matches.items():
			copy = copy.replace(Pattern(p), output)

		return copy

	def repeat_apply(self, expr: Expr) -> Expr:
		prev = None
		while prev is None or prev != expr:
			prev = expr
			expr = self.apply(expr).simplify_constexprs()

		return expr
	
	def __str__(self) -> str:
		return f'{self.input} -> {self.output}'
