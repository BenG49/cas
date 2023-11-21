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
	test(parse('x+x+0'), 		parse('2x'))
	test(parse('(3y^2)+0'), 	parse('3y^2'))
	test(parse('x+0+0'), 		parse('x'))
	test(parse('1(x+0)'), 		parse('x'))
	test(parse('x^1*x^2'), 		parse('x^3'))
	test(parse('2x^2+x^2/2'),	parse('2x^2+x^2/2'))
	test(parse('x^2/x'), 		parse('x'))
	test(parse('2x^3*x'), 		parse('2x^4'))
	test(parse('(2xy)+4(3zy)+xz(1)(2)+x'), parse('(12yz)+(2xz)+(2xy)+x'))
	test(parse('xy+yz'), 		parse('y(x+z)'))
	test(parse('x-x-1'), 		parse('-1'))
	test(parse('3+x/x'), 		parse('4'))
	test(parse('3x+2x+1x'), 	parse('6x'))
	test(parse('x-(x+2)'), 		parse('-2'))
	test(parse('x/2/(1/x)'),	parse('x^2/2'))

def deriv_rules_test():
	test(parse('d/dx(x+2)'), 	parse('1'))
	test(parse('d/dx(3-x)'), 	parse('-1'))
	test(parse('d/dx(xy)'), 	parse('xd/dx(y)+y'))
	test(parse('d/dx((2+x)/x)'),	parse('-2/x^2'))
	test(parse('d/dx(6x^3-9x+4)'),parse('18x^2-9'))
	test(parse('d/dx(4x^7-3x^-7+9x)'), parse('28x^6--21x^-8+9'))
	test(parse('d/dx((x-4)(2x+x^2))'), parse('3x^2-4x-8')) # technically this is right
	test(parse('d/dx(y^3+sin(y))'),	parse('3y^2d/dx(y)+cos(y)d/dx(y)'))

if __name__ == '__main__':
	rule_test()
	deriv_rules_test()
