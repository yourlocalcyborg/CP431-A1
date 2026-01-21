#!/usr/bin/env python3

import mpi4py as m
import timeit as t
from math import sqrt, floor
from sys import argv

def sieve(n):
    A = [True for i in range(2, n+1)]
    for i in range(2, floor(sqrt(n))):
        if A[i-2]:
            j = i**2
            while j <= n:
                A[j-2] = False 
                j += i
    
    for i in range(len(A)):
        if A[i]:
            yield i+2
    
def findgaps(primes):
    gap = (0, 0, 0)
    for i in range(len(primes)-1):
        newgap = primes[i+1] - primes[i]
        if  newgap > gap[0]:
            gap = (newgap, primes[i], primes[i+1])

    return gap

def main(n):
    gen = sieve(n)
    results = list(gen)
    return findgaps(results)


print(t.timeit(stmt=lambda: print(main(int(argv[1]))), number=1))
