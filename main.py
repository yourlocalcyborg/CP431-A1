#!/usr/bin/env python3
from mpi4py import MPI
from math import sqrt, floor
from sys import argv
from array import array
import time

def get_small_primes(limit):
    """Generates base primes up to sqrt(N) for all processes."""
    if limit < 2: return []
    # Use 'B' for unsigned char to minimize memory footprint
    is_prime = array('B', [1]) * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for p in range(2, int(sqrt(limit)) + 1):
        if is_prime[p]:
            for i in range(p * p, limit + 1, p):
                is_prime[i] = 0
    return [p for p in range(limit + 1) if is_prime[p]]

def main():
    # 1. MPI Environment Setup
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    
    if len(argv) < 2:
        if rank == 0: print("Usage: mpiexec -n <cores> python script.py <N>")
        return
    
    N = int(argv[1])
    
    # 2. Start Timer (only on Rank 0)
    if rank == 0:
        start_time = time.time()
    
    # Generate base primes up to sqrt(N)
    limit = int(sqrt(N))
    small_primes = get_small_primes(limit)
    
    # 3. Domain Decomposition
    # Divide 1 to N into chunks for each processor
    chunk_size = N // size
    local_start = rank * chunk_size + 1
    local_end = (rank + 1) * chunk_size if rank != size - 1 else N
    
    # 4. Segmented Sieve Logic
    segment_size = 10**6 # Fits in L2/L3 cache
    max_gap = 0
    p1, p2 = 0, 0
    first_prime_found = 0
    last_prime_found = 0
    prev_prime = 0

    for low in range(local_start, local_end + 1, segment_size):
        high = min(low + segment_size - 1, local_end)
        S = array('B', [1]) * (high - low + 1)
        
        for p in small_primes:
            # Find the first multiple of p >= low
            start = max(p * p, (low + p - 1) // p * p)
            for j in range(start, high + 1, p):
                S[j - low] = 0
        
        for i in range(len(S)):
            if S[i]:
                curr = i + low
                if curr <= 1: continue
                
                if first_prime_found == 0:
                    first_prime_found = curr
                
                if prev_prime != 0:
                    gap = curr - prev_prime
                    if gap > max_gap:
                        max_gap, p1, p2 = gap, prev_prime, curr
                
                prev_prime = curr
                last_prime_found = curr

    # 5. Collective Communication
    # Gather (max_gap, p1, p2, first_prime, last_prime) from all ranks
    local_summary = (max_gap, p1, p2, first_prime_found, last_prime_found)
    all_summaries = comm.gather(local_summary, root=0)

    # 6. Final Reduction and Boundary Check (Rank 0 only)
    if rank == 0:
        global_max_gap = 0
        final_p1, final_p2 = 0, 0
        
        for i in range(len(all_summaries)):
            res = all_summaries[i]
            # Check internal gaps
            if res[0] > global_max_gap:
                global_max_gap, final_p1, final_p2 = res[0], res[1], res[2]
            
            # Check gaps between the end of one rank and start of the next
            if i < len(all_summaries) - 1:
                p_end = res[4]
                p_start_next = all_summaries[i+1][3]
                if p_end != 0 and p_start_next != 0:
                    boundary_gap = p_start_next - p_end
                    if boundary_gap > global_max_gap:
                        global_max_gap, final_p1, final_p2 = boundary_gap, p_end, p_start_next

        end_time = time.time()
        
        # Output results for Assignment
        print("-" * 30)
        print(f"Total Range: 1 to {N}")
        print(f"Processors Used: {size}")
        print(f"Largest Gap Found: {global_max_gap}")
        print(f"Between Primes: {final_p1} and {final_p2}")
        print(f"Time Elapsed: {end_time - start_time:.4f} seconds")
        print("-" * 30)

if __name__ == "__main__":
    main()
