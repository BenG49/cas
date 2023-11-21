from expr import Expr
from parse import parse

class RuleSet:
	Rules = [
		parse('_x-_x => 0'),
		parse('_x/_x => 1'),
		
		parse('_x+0  => _x'),
		parse('_x*0  => 0'),
		parse('_x*1  => _x'),
		parse('_x*_x => _x^2'),

		parse('_x^_n*_x^_m => _x^(_n+_m)'),
		parse('_x^_n*_x    => _x^(_n+1)'),
		
		parse('0/_x => 0'),
		parse('_x^_n/_x^_m => _x^(_n-_m)'),
		parse('_x^_n/_x    => _x^(_n-1)'),

		parse('_x^1 => _x'),
		parse('_x^0 => 1'),

		parse('_x--_y  => _x+-1*_y'),
		parse('_x-(_x+_y) => -1*_y'), # TODO: find more elegant way to fix this
		parse('(_a/_b)/(_c/_d) => (_a*_d)/(_b*_c)'),

		# distributive property
		parse('(_x*_n)+(_x*_m) => _x*(_n+_m)'),
		parse('(_x*_n)+_x      => _x*(_n+1)'),
		parse('_x+_x           => _x*2'),

		### DERIVATIVE RULES ###
		
		parse('d/d_x(_x) => 1'), # constant rule

		parse('d/d_x(_n+_m) => d/d_x(_n)+d/d_x(_m)'), # sum rule
		parse('d/d_x(_n-_m) => d/d_x(_n)-d/d_x(_m)'), # difference rule

		parse('d/d_x(_m^_n) => _n*_m^(_n-1)*d/d_x(_m)'), # power rule

		parse('d/d_x(_m*_n) => d/d_x(_m)*_n+_m*d/d_x(_n)'), # product rule

		parse('d/d_x(_m/_n) => (_n*d/d_x(_m)-_m*d/d_x(_n))/_n^2'), # quotient rule

		# chain rule
		parse('d/d_x(sin(_y)) =>    cos(_y)*d/d_x(_y)'),
		parse('d/d_x(cos(_y)) => -1*cos(_y)*d/d_x(_y)'),
	]

	def apply(expr: Expr) -> Expr:
		for r in RuleSet.Rules:
			expr = r.apply(expr)
		
		return expr

	def repeat_apply(expr: Expr) -> Expr:
		prev = None
		while prev is None or prev != expr:
			prev = expr
			expr = RuleSet.apply(expr).simplify()

		return expr

if __name__ == '__main__':
	r = RuleSet.Rules[-1]

	print(r.apply(parse('(x*3)+(x*2)')))
