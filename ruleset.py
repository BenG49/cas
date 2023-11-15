from expr import Expr
from parse import parse

class RuleSet:
	Rules = [
		parse('_x-_x -> 0'),
		parse('_x/_x -> 1'),
		
		parse('_x+0 -> _x'),
		parse('_x*0 -> 0'),
		parse('_x*1 -> _x'),

		parse('_x^_n*_x^_m -> _x^(_n+_m)'),
		parse('_x^_n*_x    -> _x^(_n+1)'),
		
		parse('0/_x -> 0'),
		parse('_x^_n/_x^_m -> _x^(_n-_m)'),
		parse('_x^_n/_x    -> _x^(_n-1)'),

		parse('_x^1 -> _x'),
		parse('_x^0 -> 1'),

		# distributive property
		parse('(_x*_n)+(_x*_m) -> _x*(_n+_m)'),
		parse('(_x*_n)+_x      -> _x*(_n+1)')
	]

	def apply(expr: Expr) -> Expr:
		for r in RuleSet.Rules:
			expr = r.apply(expr)
		
		return expr

	def repeat_apply(expr: Expr) -> Expr:
		prev = None
		while prev is None or prev != expr:
			prev = expr
			expr = RuleSet.apply(expr).simplify_constexprs()

		return expr

if __name__ == '__main__':
	r = RuleSet.Rules[-1]

	print(r.apply(parse('(x*3)+(x*2)')))
