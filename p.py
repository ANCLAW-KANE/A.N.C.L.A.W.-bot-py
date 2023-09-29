
"""
cl = []
for i in range(0, 256): 
    cl.append(f'\x1b[38;5;{i}m')
for _ in range(0,101):
    for z in cl:
        print(f"■{z}",end='')
"""

"""
import timeit

set1 = set(range(10000))

set2 = set(range(5000, 15000))


time_intersection = timeit.timeit(lambda: set1.intersection(set2), number=10000)

time_and = timeit.timeit(lambda: set1 & set2, number=10000)


print("Время выполнения intersection():", time_intersection)

print("Время выполнения &: ", time_and)
        """


