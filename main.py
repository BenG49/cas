from ruleset import RuleSet
from parse import parse

def test(e, expected):
	a = RuleSet.repeat_apply(e)
	print(a == expected, e, '->', a)

def test_rule(e, expected, rule):
	a = rule.apply(e)
	print(a == expected, e, '->', a)

def equality_test():
	a = parse('x+2')
	b = parse('2+x')

	print(a, '=', b, '?', a == b)

def canonicalization_test():
	e = parse('(2+3)+1+x+y+a+b')

	print(e, len(e))

	e = parse('(1*2)+(2^3+sin(x))')
	f = parse('2^3+(sin(x)+(1*2))')

	print(e, e == f)

def rule_test():
	test(parse('x+x+0'), parse('2*x'))
	test(parse('(3*y^2)+0'), parse('3*y^2'))
	test(parse('x+0+0'), parse('x'))
	test(parse('1*(x+0)'), parse('x'))
	test(parse('x^1*x^2'), parse('x^3'))
	test(parse('x^2*2+x^2/2'), 	parse('x^2*2+x^2/2'))
	test(parse('x^2/x'), 		parse('x'))
	test(parse('2*x^3*x'), 		parse('2*x^4'))
	test(parse('(2*x*y)+(4*3*z*y)+(x*z*1*2)+x'), parse('((y*z*12)+(x*z*2)+(x*y*2)+x)'))
	test(parse('(y*x)+(y*z)'), 	parse('y*(x+z)'))
	test(parse('x-x-1'), 		parse('-1'))
	test(parse('3+x/x'), 		parse('4'))
	test(parse('3*x+2*x+1*x'), 	parse('6*x'))
	test(parse('x-(x+2)'), 		parse('-2'))
	test(parse('x/2/(1/x)'),    parse('x^2/2'))

def deriv_rules_test():
	test(parse('d/dx(x+2)'), 	parse('1'))
	test(parse('d/dx(3-x)'), 	parse('-1'))
	test(parse('d/dx(y*x)'), 	parse('x*d/dx(y)+y'))
	test(parse('d/dx((2+x)/x)'),	parse('-2/x^2'))
	test(parse('d/dx(6*x^3-9*x+4)'),parse('18*x^2-9'))
	test(parse('d/dx(4*x^7-3*x^-7+9*x)'), parse('28*x^6--21*x^-8+9'))
	test(parse('d/dx((x-4)*(2*x+x^2))'), parse('3*x^2-4*x-8')) # technically this is right
	test(parse('d/dx(y^3+sin(y))'),	parse('3*y^2*d/dx(y)+cos(y)*d/dx(y)'))

if __name__ == '__main__':
	deriv_rules_test()
