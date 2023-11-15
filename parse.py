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
	if '->' in s:
		s = s.split('->')
		return Rule(parse(s[0]), parse(s[1]))
	
	def error(e: str):
		print('Error:', e, 'at position', pos)
		exit(-1)

	def idx(i: int=0) -> str:
		try:
			return s[i]
		except IndexError:
			return ''

	def eat(n: int):
		nonlocal s, pos
		
		out = s[:n]
		s = s[n:]
		pos += n
		
		return out
	
	def parse_term() -> Expr:
		if idx() == '(':
			eat(1)
			out = parse_statement()
			eat(1)
			return out

		# parse function
		for o in Op.func_strings():
			if s.startswith(o):
				op = Op(Op.strings().index(eat(len(o))))

				eat(1) # (
				
				inside = parse_statement()

				eat(1) # )

				return Expr(op, inside)
		
		# pattern
		if idx() == '_':
			return Pattern(eat(2)[1])
		# variable
		elif idx().isalpha():
			return Expr(Op.LEAF, eat(1))
		# number
		elif idx().isdigit() or idx() == '-':
			i = 1
			while idx(i).isdigit():
				i += 1
			return Expr.num(int(eat(i)))

		error(f'Expected term or function, found \'{idx()}\'')

	def parse_factor() -> Expr:
		children = [parse_term()]

		while idx() == '^':
			eat(1)
			children.append(parse_factor())

		if len(children) == 1:
			return children[0]
		else:
			return Expr(Op.POW, *children)

	def parse_product() -> Expr:
		expr = parse_factor()

		while idx() in ['*', '/']:
			op = eat(1)
			expr = Expr(Op(Op.strings().index(op)), expr, parse_factor())
		
		return expr

	def parse_statement() -> Expr:
		expr = parse_product()

		while idx() in ['+', '-']:
			op = eat(1)
			expr = Expr(Op(Op.strings().index(op)), expr, parse_product())
		
		return expr

	return parse_statement()

if __name__ == '__main__':
	print(parse('1*1/-1'))
