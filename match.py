from expr import Expr, Pattern

class MatchData:
	def __init__(self):
		self.data = dict()

	def __getitem__(self, key: [Pattern, str]) -> Expr:
		if isinstance(key, Pattern):
			return self.data[str(key)]
		else:
			return self.data[key]

	def register(self, pattern: Pattern, expr: [Expr, tuple[Expr]]):
		if str(pattern) in self.data:# and self[pattern] != expr:
			print('EXISTS')
			return
		
		self.data[str(pattern)] = expr

		return self
	
	# modifies self and other
	# returns None if cannot combine
	def combine(self, other):
		if isinstance(other, MatchData):
			for key in set(self.keys()).intersection(set(other.keys())):
				# resolve differing exprs bound to same pattern
				if type(self[key]) != type(other[key]) or self[key] != other[key]:
					self_options = self[key]
					if type(self[key]) is not tuple:
						self_options = (self[key])
					
					other_options = other[key]
					if type(other[key]) is not tuple:
						other_options = (other[key])

					common_expr = set(self_options).intersection(set(other_options))

					if len(common_expr) == 0:
						return None
					elif len(common_expr) > 1:
						continue
					else:
						common_expr = list(common_expr)[0]

					self.data[key] = common_expr
					other.data[key] = common_expr

					self.collapse(self_options, [k for k in self_options if k != common_expr][0])
					other.collapse(other_options, [k for k in other_options if k != common_expr][0])
			else:
				self.data = self.data | other.data
			
		elif type(other) is dict:
			self.data = self.data | other

		return self
	
	def collapse(self, target: tuple = None, output: Expr = None):
		if target is None or output is None:
			for k in self.keys():
				if type(self[k]) is tuple:
					self.data[k] = self[k][0]
			
			return self
		
		for key, val in self.items():
			if val == target:
				self.data[key] = output

		return self

	def items(self):
		return self.data.items()

	def keys(self):
		return self.data.keys()

	def __len__(self) -> int:
		return len(self.data)

	def __str__(self) -> str:
		return str(self.data)

	def __repr__(self) -> str:
		return self.__str__()
