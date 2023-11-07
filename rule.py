from expr import Expr, Pattern
from copy import deepcopy

'''
Rewrite rules
'''

class Rule:
	# returns pattern dict or nothing
	def get_pattern_matches(rule_tree: [Expr, Pattern], expr_tree: Expr) -> [dict, None]:
		def patterns_end(tree: Expr) -> list[Expr]:
			return [c for c in rule_tree if not c.is_pattern()] + [c for c in rule_tree if c.is_pattern()]

		
		# pattern
		if isinstance(rule_tree, Pattern):
			return { rule_tree[0]: expr_tree }

		# no patterns found
		elif rule_tree == expr_tree:
			return dict()
		
		if expr_tree.is_leaf():
			return None

		if rule_tree.op == expr_tree.op:
			if expr_tree.op.is_associative() and len(expr_tree) > len(rule_tree):
				# prevents matching multiple rule children to one expr child
				indicies = []
				out_dict = dict()

				for r in patterns_end(rule_tree):
					for i in range(len(expr_tree)):
						if i not in indicies:
							val = Rule.get_pattern_matches(r, expr_tree[i])
							if val is not None:
								out_dict |= val
								indicies.append(i)
								break
					else:
						# break if match wasn't found
						break
				else:
					# if match was found for every rule child
					return out_dict

			elif len(rule_tree) == len(expr_tree) and not rule_tree.is_leaf():
				rule_children = rule_tree.children
				expr_children = expr_tree.children

				if expr_tree.op.is_associative():
					rule_children = sorted(rule_tree.children)
					expr_children = sorted(expr_tree.children)

				out_dict = dict()

				for r, e in zip(rule_children, expr_children):
					val = Rule.get_pattern_matches(r, e)

					if val is None:
						break

					out_dict |= val
				else:
					return out_dict

		# check children
		# NOTE: for multiple matches might not work
		for child in expr_tree:
			matches = Rule.get_pattern_matches(rule_tree, child)
			if matches:
				return matches

	def __init__(self, input: [Pattern, Expr], output: [Pattern, Expr]):
		self.input = input
		self.output = output

	def apply(self, expr: Expr) -> Expr:
		# get pattern/tree pairs
		matches = Rule.get_pattern_matches(self.input, expr)
		
		# no match
		if matches is None:
			return expr

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
