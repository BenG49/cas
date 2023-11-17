from expr import Expr, Pattern
from collections import Counter

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

						self.remove_options(self_options, common_expr)
						other.remove_options(self_options, common_expr)
					else:
						# attempting to combine different exprs that aren't options
						return None
			else:
				self.data = self.data | other.data
			
		elif type(other) is dict:
			self.data = self.data | other

		return self

	def remove_options(self, target: tuple, remove: list[Expr]):
		if type(remove) is Expr:
			remove = [remove]

		for pattern in self.keys():
			if type(self[pattern]) is tuple and target == self[pattern]:
				self.data[pattern] = [x for x in self[pattern] if x not in remove]
				
				if len(self[pattern]) == 1:
					self.data[pattern] = self[pattern][0]
				else:
					self.data[pattern] = tuple(self[pattern])

	def collapse(self, target: tuple = None, output: Expr = None):
		# don't do this if just looking to replace
		if target is None and output is None:
			# remove some options by logical elimination
			for options, count in Counter(self.data.values()).items():
				if type(options) is tuple and len(options) == count:
					# remove these options from all other options
					for key, value in self.items():
						if type(value) is tuple and options != value and set(options).issubset(set(value)):
							self.data[key] = tuple(v for v in value if v not in options)

		for pattern, expr in self.items():
			if expr == target:
				self.data[pattern] = output
			elif type(expr) is tuple:
				out = expr[0]
				self.remove_options(self[pattern], expr[0])
				self.data[pattern] = out

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
