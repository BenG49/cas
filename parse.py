from rule import Rule
from expr import Expr, Pattern
from op import Op

'''
statement -> product (('+' product)|('-' product))*
product -> factor (('*' factor)|('/' factor))*
factor -> power | term
power -> term '^' factor
~term -> group | variable | pattern | number | function
~group -> '(' statement ')'

'''

def parse(s: str) -> Expr: 
	pos = 0
	s = s.replace(' ', '').lower()

	# rule
	if '=>' in s:
		s = s.split('=>')
		return Rule(parse(s[0]), parse(s[1]))
	
	def error(e: str, check: bool = False):
		if not check:
			print('Error:', e, 'at index', pos)
			exit(-1)

	def idx(i: int=0, count: int=1) -> str:
		try:
			return s[i:i+count]
		except IndexError:
			return ''

	def eat_n(n: int):
		nonlocal s, pos

		out = s[:n]
		s = s[n:]
		pos += n
		
		return out

	def eat(expected: str):
		nonlocal s, pos

		n = len(expected)
		
		out = s[:n]
		s = s[n:]

		if expected is not None:
			error(f'Expected \'{expected}\', found \'{out}\'', out == expected)

		pos += n
		
		return out
	
	def parse_var() -> Expr:
		error(f'Expected variable, found \'{idx()}\'', idx().isalpha())
		return Expr(Op.LEAF, eat_n(1))

	def parse_num() -> Expr:
		error(f'Expected digit or \'-\', found \'{idx()}\'', idx().isdigit() or idx() == '-')
		i = 1
		while idx(i).isdigit():
			i += 1
		return Expr.num(int(eat_n(i)))

	def parse_term() -> Expr:
		if idx() == '(':
			eat_n(1)
			out = parse_statement()
			eat(')')
			return out

		# parse function
		for o in Op.func_strings():
			if s.startswith(o):
				op = Op(Op.strings().index(eat_n(len(o))))
				eat('(')
				inside = parse_statement()
				eat(')')
				return Expr(op, inside)
		
		# pattern
		if idx() == '_':
			eat_n(1)
			error(f'Expected pattern variable, found \'{idx()}\'', idx().isalpha())
			return Pattern(eat_n(1))
		# derivative
		elif idx(count=3) == 'd/d':
			eat_n(3)
			var = parse_var()
			eat('(')
			out = Expr(Op.DERIV, var, parse_statement())
			eat(')')
			return out
		# variable
		elif idx().isalpha():
			return parse_var()
		# number
		elif idx().isdigit() or idx() == '-':
			return parse_num()

		error(f'Expected term or function, found \'{idx()}\'')

	def parse_factor() -> Expr:
		expr = parse_term()

		if idx() == '^':
			eat_n(1)
			return Expr(Op.POW, expr, parse_factor())
		
		return expr

	def parse_product() -> Expr:
		expr = parse_factor()

		while idx() in ['*', '/']:
			op = eat_n(1)
			expr = Expr(Op(Op.strings().index(op)), expr, parse_factor())
		
		return expr

	def parse_statement() -> Expr:
		expr = parse_product()

		while idx() in ['+', '-']:
			op = eat_n(1)
			expr = Expr(Op(Op.strings().index(op)), expr, parse_product())
		
		return expr

	return parse_statement()

if __name__ == '__main__':
	print(parse('d/dx(1+x)'))
