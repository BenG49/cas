from op import Op

class Expr:
	def x():
		return Expr(Op.LEAF, 'x')
	
	def num(n):
		return Expr(Op.LEAF, n)

	def __init__(self, op, *children):
		self.op = op

		# TODO: make this a rule
		if self.op.is_associative():
			# combine associative trees
			self.children = []

			for child in children:
				if child.op and op == child.op:
					for grandchild in child:
						self.children.append(grandchild)
				else:
					self.children.append(child)

			self.children.sort(reverse=True)
		else:
			if self.op == Op.DERIV and not children[0].is_var():
				print('Invalid argument to derivative: first child must be independent variable')
				exit()

			self.children = list(children)

	### LIST FUNCTIONS ###

	def __getitem__(self, i):
		return self.children[i]

	def __len__(self) -> int:
		return len(self.children)

	def __iter__(self):
		return self.children.__iter__()

	### ATTRIBUTES ###

	def is_pattern(self) -> bool:
		return False

	def is_leaf(self) -> bool:
		return self.op == Op.LEAF

	def is_var(self) -> bool:
		return self.is_leaf() and type(self[0]) is str and not self[0].isnumeric()

	def is_const(self) -> bool:
		return self.is_leaf() and (isinstance(self[0], int) or isinstance(self[0], float))

	# TODO: check if this works with derivatives
	def is_constexpr(self) -> bool:
		if self.is_var():
			return False
		elif self.is_const():
			return True
		elif self.op.is_function():
			return self[0].is_constexpr()
		else:
			return self[0].is_constexpr() and self[1].is_constexpr()

	# return "real" child nodes
	def get_child_nodes(self) -> bool:
		if self.op in [Op.PLUS, Op.MINUS, Op.MUL, Op.DIV, Op.POW, Op.SIN, Op.COS]:
			return self.children
		elif self.op == Op.DERIV:
			return [self.children[1]]
		# leaf
		else:
			return []

	### EXPONENT ###

	def exponent(self):
		return self[1] if self.op == Op.POW else Expr.num(1)

	def base(self):
		return self[0] if self.op == Op.POW else self

	### FACTORS ###

	def has_factor(self, eq) -> bool:
		if self == eq:
			return True

		if self.is_const() and eq.is_const():
			return self[0] % eq[0] == 0
		elif self.op == Op.DIV and self[0].has_factor(eq):
			return True
		elif self.op == Op.POW and self[0].has_factor(eq):
			return True
		elif self.op == Op.MUL:
			for e in self:
				if e.has_factor(eq):
					return True

		return False
	
	### EVAL AND SIMPLIFICATION ###

	def simplify_constexprs(self):
		def eq(*x):
			return Expr(*x).simplify()

		if self.is_constexpr():
			try:
				return Expr.num(self())
			except ZeroDivisionError:
				...

		# separate constexprs and exprs
		elif self.op.is_associative() and len(self) > 2:
			constexprs = [e for e in self if e.is_constexpr()]
			exprs = [e for e in self if not e.is_constexpr()]

			if len(constexprs) and len(exprs):
				return Expr(
					self.op,
					eq(self.op, *exprs) if len(exprs) > 1 else exprs[0],
					eq(self.op, *constexprs) if len(constexprs) > 1 else constexprs[0]
				)
		
		if len(self.get_child_nodes()):
			return Expr(self.op, *[e.simplify() for e in self])
		else:
			return self


	def simplify(self):
		def eq(*x):
			return Expr(*x).simplify()

		# evauluate constant expression
		if self.is_constexpr():
			try:
				return Expr.num(self())
			except ZeroDivisionError:
				...
		# separate constexprs and exprs
		elif self.op.is_associative() and len(self) > 2:
			constexprs = [e for e in self if e.is_constexpr()]
			exprs = [e for e in self if not e.is_constexpr()]

			if len(constexprs) and len(exprs):
				return Expr(
					self.op,
					eq(self.op, *exprs) if len(exprs) > 1 else exprs[0],
					eq(self.op, *constexprs) if len(constexprs) > 1 else constexprs[0]
				)

		# distributive property
		# elif self.op == Op.PLUS:
		# 	exprs = [e for e in self if not e.is_constexpr()]

			'''
        +
    /   |   \ 
  *     *      *
 / \   / \   / | \ 
 y 2   x 2   y 3 x
			'''

			
		# elif self.op == Op.DERIV:
		# 	return deriv_simplify(self)

		# factoring (2x^n+3x^n -> 5x^n)
		# elif self.op.is_additive() and get_x_to_n_factor(self[0]) and get_x_to_n_factor(self[1]):
		# 	a1, n1 = get_x_to_n_factor(self[0])
		# 	a2, n2 = get_x_to_n_factor(self[1])

		# 	if n1() == n2():
		# 		if n1() == 1:
		# 			return Expr(Op.MUL,
		# 				eq(Op.PLUS, a1, a2),
		# 				Expr.x())
		# 		else:
		# 			return Expr(Op.MUL,
		# 				eq(Op.PLUS, a1, a2),
		# 				Expr(Op.POW, Expr.x(), n1))

		if len(self.get_child_nodes()):
			return Expr(self.op, *[e.simplify() for e in self])
		else:
			return self

	# eval given variable values
	def __call__(self, **vars: dict[str, int]) -> [int, float]:
		if self.is_var():
			return vars[self[0]]
		elif self.is_const():
			return self[0]
		elif self.op == Op.DERIV:
			return self.simplify()(**vars)
		
		return self.op.func()(*[c(**vars) for c in self])

	### COMPARISON OPERATORS ###

	def __eq__(self, other) -> bool:
		if len(self) == len(other) and self.op == other.op:
			if all([self[n] == other[n] for n in range(len(self))]):
				return True
			
			if self.op.is_associative():
				sort_self = sorted(self.children)
				sort_other = sorted(other.children)
				if all([sort_self[n] == sort_other[n] for n in range(len(self))]):
					return True
		
		return False

	def __hash__(self) -> int:
		if self.is_leaf():
			return hash(self[0])
		h = self.op.value * 31
		for c in self:
			h = h * 31 + hash(c)
		return h

	def __lt__(self, other) -> bool:
		if self.op == other.op:
			if self.op == Op.LEAF:
				# 1 < 2
				if self.is_const() and other.is_const():
					return self() < other()
				# z < a
				elif self.is_var() and other.is_var():
					return self[0] > other[0]
				# const < var
				else:
					return self.is_const()
			
			else:
				if len(self) != len(other):
					return len(self) < len(other)

				#    self     other
				#   /   \     /   \
				#  1     x   2     3
				# idk how else this should be sorted, need to look at children

		return self.op < other.op

	### TREE MODIFICATION ###

	# in-place modification, but have to read return value of function due to edge case
	def replace(self, match, replacement):
		if self == match:
			return replacement
		
		# don't go through children
		if self.is_leaf():
			return self

		# if self associative and >2 children, look for match and split tree
		if self.op == match.op and self.op.is_associative() and len(self) > len(match):
			indicies = []

			for m in match:
				for i in range(len(self)):
					if self[i] == m and i not in indicies:
						indicies.append(i)
						break
				else:
					# break if match wasnt found
					break
			# if there was match found for every match
			else:
				# split tree so that match will be found and replaced
				self.split_tree(indicies)

		# check for matches in children
		for i, child in enumerate(self):
			if child == match:
				self.children[i] = replacement
			else:
				self.children[i] = child.replace(match, replacement)

		return self

	# split associative tree (>2 children) into multi-level tree
	def split_tree(self, grandchild_indicies: list[int]):
		if not self.op.is_associative():
			return
		
		grandchild_indicies.sort()

		child_tree = Expr(
			self.op,
			*[self.children[i] for i in grandchild_indicies])

		for i in reversed(grandchild_indicies):
			del self.children[i]
		
		self.children.append(child_tree)

	### STRING REPRESENTATION ###

	def __str__(self) -> str:
		PREFIX_NOTATION = False

		if PREFIX_NOTATION:
			if self.op == Op.LEAF:
				return str(self[0])
			else:
				return f'({self.op} {" ".join(map(str, self))})'
		else:
			if self.op == Op.POW:
				return f'({self[0]})^{self[1]}'
			elif self.op.is_function():
				return f'{self.op}({self[0]})'
			elif self.op == Op.LEAF:
				return str(self[0])
			elif self.op == Op.DERIV:
				return f'{str(self.op)}{self[0]}[{self[1]}]'
			
			inner = str(self.op).join(map(str, self))
			
			if False: #self.op.is_associative():
				return inner
			else:
				return '(' + inner + ')'

	def __repr__(self) -> str:
		return self.__str__()

class Pattern(Expr):
	def __init__(self, id):
		self.op = Op.LEAF
		self.id = id

	def is_pattern(self) -> bool:
		return True
	
	def __getitem__(self, i):
		return self.id if i == 0 else None

	def __len__(self) -> int:
		return 1

	def __eq__(self, other) -> bool:
		return self.op == other.op and hasattr(other, 'id') and self.id == other.id

	def __hash__(self) -> int:
		return hash(self.id) * 31

	def __lt__(self, other) -> bool:
		return False

	def __str__(self) -> str:
		return f'_{self.id}'

### DERIVATIVE SIMPLIFICATION ###
def deriv_simplify(e: Expr):
	def eq(*x):
		return Expr(*x).simplify()

	ind = e[0]
	equ = e[1]

	if equ.is_constexpr():
		return Expr.num(0)
	elif equ.is_var():
		if equ == ind:
			return Expr.num(1)
		else:
			return e
	elif equ.op.is_additive():
		return eq(
			equ.op,
			*[eq(Op.DERIV, ind, e) for e in equ])
	elif equ.op == Op.MUL:
		return eq(
			Op.PLUS,
			*[eq(
				Op.MUL,
				eq(Op.DERIV, ind, e),
				*[f for j, f in enumerate(equ) if j != i]
			) for i, e in enumerate(equ)])
	elif equ.op == Op.DIV:
		return eq(Op.DIV,
			eq(
				Op.MINUS,
				eq(Op.MUL, equ[1], eq(Op.DERIV, ind, equ[0])),
				eq(Op.MUL, equ[0], eq(Op.DERIV, ind, equ[1]))),
			eq(Op.POW, equ[1], Expr.num(2)))
	elif equ.op == Op.POW:
		return eq(
			Op.MUL,
			equ[1],
			eq(
				Op.POW,
				equ[0],
				eq(Op.MINUS, equ[1], Expr.num(1))),
			eq(Op.DERIV, ind, equ[0]))
	elif equ.op.is_function():
		inside = equ[0]

		if equ.op == Op.POW:
			left = eq(
				Op.MUL,
				equ[1],
				eq(
					Op.POW,
					inside,
					eq(Op.MINUS, equ[1], Expr.num(1))))
		elif equ.op == Op.SIN:
			left = eq(Op.COS, equ[0])
		elif equ.op == Op.COS:
			left = eq(Op.MUL, Expr.num(-1), eq(Op.SIN, equ[0]))

		return eq(
			Op.MUL,
			left,
			eq(Op.DERIV, ind, inside))
