#!/usr/bin/env python3

from math import sqrt, floor
from sys import argv
from array import array

# Single sieve (find all composites up to range for single starting prime)
def sieve_once(i, n):
    j = i**2
    composites = []
    while j <= n:
        composites.append(j)
        j += i

    return composites

def sieve(n):
    # https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes
    # Same algorithm as shown in pseudocode here, 

    # Initialize boolean array to True for all elements in range
    A = array('B', [1 for i in range(2, n+1)])

    # Prime sieve
    for i in range(2, floor(sqrt(n))):
        if A[i-2]:
            composites = sieve_once(i, n)
            for i in composites:
                A[i-2] = False

    # Turn boolean list into list of which elements are True (prime)
    primes = []
    for i in range(len(A)):
        if A[i]:
            primes.append(i+2)

    return primes
    
# Traverse list of prime numbers and find largest gap between consecutive elements
# Returns size of largest gap, prime at the start of the gap, and the prime at the end of the gap
def findgaps(primes):
    gap = (0, 0, 0)
    for i in range(len(primes)-1):
        newgap = primes[i+1] - primes[i]
        if  newgap > gap[0]:
            gap = (newgap, primes[i], primes[i+1])

    return gap

#TODO: write segmented sieve for scaling to 1 trillion

# Get largest gap between primes result
results = sieve(int(argv[1]))
print(findgaps(results))
