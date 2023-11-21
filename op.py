from enum import Enum
from math import sin, cos

class Op(Enum):
	LEAF = 0
	PLUS = 1
	MINUS = 2
	MUL = 3
	DIV = 4
	POW = 5
	SIN = 6
	COS = 7
	DERIV = 8

	def is_additive(self) -> bool:
		return self in [Op.PLUS, Op.MINUS]

	def is_function(self) -> bool:
		return self in [Op.POW, Op.SIN, Op.COS]
	
	### PROPERTIES ###

	def is_associative(self) -> bool:
		return self in [Op.PLUS, Op.MUL]

	### EVAULUATION ###

	def func(self):
		def prod(*args):
			p = 1
			for a in args:
				p *= a
			return p

		return [
			lambda x: x,
			lambda *args: sum(args),
			lambda x, y: x - y,
			prod,
			lambda x, y: x / y,
			lambda x, y: x ** y,
			lambda x: sin(x),
			lambda x: cos(x),
		][self.value]

	def __lt__(self, other) -> bool:
		order = [Op.POW, Op.MUL, Op.DIV, Op.PLUS, Op.MINUS, Op.LEAF, Op.SIN, Op.COS, Op.DERIV]

		return order.index(other) < order.index(self)

	### STRINGS ###

	def strings() -> list[str]:
		return ['', '+', '-', '*', '/', '^', 'sin', 'cos', 'd/d']

	def binop_strings():
		return Op.strings()[1:6]

	def func_strings() -> list[str]:
		return Op.strings()[Op.SIN.value : Op.COS.value + 1]

	def __str__(self) -> str:
		return Op.strings()[self.value]
