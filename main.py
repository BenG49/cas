from expr import Expr
from ruleset import RuleSet
from op import Op
from parse import parse

def num(n): return Expr.num(n)
def x(): return Expr.x()

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

def deriv_test():
	e = Expr(Op.DERIV,
		x(),
		parse('x*x'))

	e = Expr(Op.DERIV,
		x(),
		parse('(3x)/x^2'))

	e = Expr(Op.DERIV,
		x(),
		parse('3*x^2+x'))

	print(e, '=', e.simplify())

def factor_test():
	e = num(4)

	print(e.has_factor(num(2)))

	e = parse('x*3*10*y')

	print(e.has_factor(num(5)))

	e = parse('x^2/2')

	print(e.has_factor(x()))

def simplify_test():
	e = parse('2*x^2+x^2/2')
	e = parse('x^2/x')
	e = parse('2*x^3*x')

	# (2*x*y)+(4*3*z*y)+(x*z*1*2)+x = (2*x*y)+(12*y*z)+(2*x*z) = 2x(y+z)+12yz = 2(x(y+z)+6yz)
	e = parse('(2*x*y)+(4*3*z*y)+(x*z*1*2)+x')
	
	print(e, '=', e.simplify())

def distributive_test():
	e = parse('(3*x)^2')

	e = parse('(2*x)+(3*x)')

	print(e, '=', e.simplify())

def rule_test():
	e = parse('x+x+0')
	print(e, '->', RuleSet.repeat_apply(e))

	e = parse('x*(x+0)')
	print(e, '->', RuleSet.repeat_apply(e))

	e = parse('(3*y^2)+0')
	print(e, '->', RuleSet.repeat_apply(e))

	e = parse('x+0+0')
	print(e, '->', RuleSet.repeat_apply(e))

	e = parse('1*(x+0)')
	print(e, '->', RuleSet.repeat_apply(e))

	e = parse('x^1*x^2')
	print(e, '->', RuleSet.repeat_apply(e))

def simplify_rule_test():
	def test(e, expected):
		a = RuleSet.repeat_apply(e)
		print(e, '->', a, a == expected)
	
	e = parse('x^2*2+x^2/2')
	test(e, parse('x^2*2+x^2/2'))

	e = parse('x^2/x')
	test(e, parse('x'))

	e = parse('2*x^3*x')
	test(e, parse('2*x^4'))

	e = parse('(2*x*y)+(4*3*z*y)+(x*z*1*2)+x')
	test(e, parse('((y*z*12)+(x*z*2)+(x*y*2)+x)'))

	e = parse('(x*3)+(x*2)')
	test(e, parse('x*5'))

	e = parse('x-x-1')
	test(e, parse('-1'))

	e = parse('3+x/x')
	test(e, parse('4'))

	e = parse('3*x+2*x+1*x')
	test(e, parse('6*x'))

if __name__ == '__main__':
	simplify_rule_test()
