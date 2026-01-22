#!/usr/bin/env python3

from mpi4py import MPI
import timeit as t
from math import sqrt, floor
from sys import argv

def sieve_once(i, n):
    j = i**2
    composites = []
    while j <= n:
        composites.append(j)
        j += i

    return composites

def sieve(n):
    A = [True for i in range(2, n+1)]

    for i in range(2, floor(sqrt(n))):
        if A[i-2]:
            composites = sieve_once(i, n)
            for i in composites:
                A[i-2] = False

    primes = []
    for i in range(len(A)):
        if A[i]:
            primes.append(i+2)

    return primes
    
def findgaps(primes):
    gap = (0, 0, 0)
    for i in range(len(primes)-1):
        newgap = primes[i+1] - primes[i]
        if  newgap > gap[0]:
            gap = (newgap, primes[i], primes[i+1])

    return gap


com = MPI.COMM_WORLD
rank = com.Get_rank()

results = sieve(int(argv[1]))
#print(results)
print(findgaps(results))
