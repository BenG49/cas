from expr import Expr, Pattern

class MatchData:
	def __init__(self):
		self.data = dict()

	def __getitem__(self, key: [Pattern, str]) -> Expr:
		return self.data[str(key) if isinstance(key, Pattern) else key]

	def register(self, pattern: Pattern, expr: [Expr, tuple[Expr]]):
		if str(pattern) in self.data:
			print('EXISTS')
			return
		
		self.data[str(pattern)] = expr

		return self
	
	# modifies self and other
	# returns None if cannot combine
	def combine(self, other):
		if isinstance(other, MatchData):
			for key in set(self.keys()).intersection(set(other.keys())):
				# resolve different exprs bound to same pattern
				if type(self[key]) != type(other[key]) or self[key] != other[key]:
					# collapse different options
					if type(self[key]) is tuple or type(other[key]) is tuple:
						self_options = self[key] if type(self[key]) is tuple else tuple([self[key]])
						other_options = other[key] if type(other[key]) is tuple else tuple([other[key]])

						common_expr = set(self_options).intersection(set(other_options))

						# no common expressions
						if len(common_expr) == 0:
							return None
						# too many common expressions
						elif len(common_expr) > 1:
							continue
						else:
							common_expr = list(common_expr)[0]

						self.data[key] = common_expr
						other.data[key] = common_expr

						if len(self_options) > 1:
							self.collapse(self_options, [k for k in self_options if k != common_expr][0])
						if len(other_options) > 1:
							other.collapse(other_options, [k for k in other_options if k != common_expr][0])
					else:
						# attempting to combine different exprs that aren't options
						return None
			else:
				self.data = self.data | other.data
			
		elif type(other) is dict:
			self.data = self.data | other

		return self
	
	def collapse(self, target: tuple = None, output: Expr = None):
		for pattern, expr in self.items():
			if expr == target:
				self.data[pattern] = output
			elif type(expr) is tuple:
				self.data[pattern] = expr[0]

		return self

	def items(self):
		return self.data.items()

	def keys(self):
		return self.data.keys()

	def values(self):
		return self.data.values()

	def __len__(self) -> int:
		return len(self.data)

	def __str__(self) -> str:
		return str(self.data)

	def __repr__(self) -> str:
		return self.__str__()
