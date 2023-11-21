from expr import Expr, Pattern
from match import MatchData

'''
Rewrite rules
'''

class Rule:
	def __init__(self, input: [Pattern, Expr], output: [Pattern, Expr]):
		self.input = input
		self.output = output

	def apply(self, expr: Expr) -> Expr:
		copy = expr.deepcopy()

		# get pattern/tree pairs
		matches = MatchData()

		# no match
		if not matches.populate_matches(copy, self.input):
			return copy

		matches.collapse()

		# no pattern vars
		if len(matches) == 0:
			return copy.replace(self.input, self.output)

		# put patterns in place in original expression
		for p, output in matches.items():
			for i in output:
				copy = copy.replace_by_id(i, Pattern(p))

		# make rule substitution
		copy = copy.replace(self.input, self.output)

		# substitute original expressions for new patterns
		for p, output in matches.items():
			copy = copy.replace(Pattern(p), output.expr)

		return copy

	def repeat_apply(self, expr: Expr) -> Expr:
		prev = None
		while prev is None or prev != expr:
			prev = expr
			expr = self.apply(expr).simplify()

		return expr
	
	def __str__(self) -> str:
		return f'{self.input} -> {self.output}'
