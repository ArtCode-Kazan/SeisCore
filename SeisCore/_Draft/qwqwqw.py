from sympy import *


x=symbols('x')

z=diff(x**2,x)

print(z.subs(x,5))