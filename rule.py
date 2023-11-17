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
		if isinstance(match, Pattern) and match.matches(expr):
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
				child_match_data = Rule.get_pattern_matches(child, match, MatchData())
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
					break

				if local_matches.combine(check) is None:
					break
			else:
				return match_data.combine(local_matches)
			
			# CHECK THROUGH CHILDREN
			for child in expr:
				child_match_data = Rule.get_pattern_matches(child, match, MatchData())
				if child_match_data:
					return match_data.combine(child_match_data)
			
			return None

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
			# first check if any patterns have only one possibility due to match restrictions
			for pattern in match_patterns:
				pattern_possible = [expr[i] for i in range(len(expr)) if not i in marked_indicies and pattern.matches(expr[i])]
				if len(pattern_possible) == 1:
					e = pattern_possible[0]
					match_data.register(pattern, e)
					marked_indicies.append(expr.children.index(e))

					match_patterns.remove(pattern)

			expr_remaining = [expr[i] for i in range(len(expr)) if i not in marked_indicies]

			if len(match_patterns) != len(expr_remaining):
				return None
			
			for pattern in match_patterns:
				remaining = [expr[i] for i in range(len(expr)) if not i in marked_indicies and pattern.matches(expr[i])]
				local_match.register(pattern, tuple(remaining))

			local_match.collapse()
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
			expr = self.apply(expr).simplify()

		return expr
	
	def __str__(self) -> str:
		return f'{self.input} -> {self.output}'

from op import Op

if __name__ == '__main__':
	rule = Rule(Expr(Op.PLUS, Pattern.Const('n'), Pattern('x'), Pattern.Const('m')), Pattern('x'))
	expr = Expr(Op.PLUS, Expr.num(1), Expr.x(), Expr.num(2))
	print(rule, expr, rule.apply(expr))
