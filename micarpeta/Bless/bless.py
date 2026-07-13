import pandas as pd
import numpy as np
import math
from collections import Counter
import matplotlib.pyplot as plt
import plotly.express as px

bolsa=[1,0,0,-1,-1,-1,-1,-1,-2,-2,-2,-2,-3,-4]
n=len(bolsa)
def V(x_query,bolsaaa):
    counts = Counter(bolsaaa)
    
    # 1. Sort ascending so we build the area from left to right
    values = sorted(counts.keys())   # [-4, -3, -2, -1, 0, 1, 2]
    
    total = 0.0
    
    for v in values:
        lower_edge = v - 1
        
        # 2. If the query is completely past this bin, add the full bin count
        if x_query >= v:
            total += counts[v]
            
        # 3. If the query falls inside this bin, add the fraction and stop
        elif lower_edge < x_query < v:
            fraction = x_query - lower_edge
            total += fraction * counts[v]
            break
            
        # 4. If the query is completely below this bin, we are done
        else:
            break
            
    return total
def G(x,bolsa):
    return (V(3,bolsa)+1-V(-x-1,bolsa))/(V(3,bolsa)+2)#2 because +1 in denominator for immediate succes and +1 for immediate failure.
def F(x,y,bolsa):
    if y<=0:
        return 1
    else:
        return G(x-y,bolsa)  
x = [-3,-2, -1, 0, 1, 2, 3, 4, 5]
y1=[]
for i in x:
    y1.append(G(i,bolsa))

x_as=math.sqrt((G(2,bolsa)+2*G(3,bolsa)+G(4,bolsa))/(G(-2,bolsa)+2*G(-1,bolsa)+G(0,bolsa)))
x_c=G(0,bolsa)+2*G(1,bolsa)+G(2,bolsa)

#+2 is mostly the answer
from functools import cache

@cache
def CDF(x, b, c):
    # 1. Base Case: Stop recursion if there are no special tokens left
    if b == 0 and c == 0:
        return G(x, bolsa)
        
    a = G(x, bolsa)
    
    # 2. Bless Path: Only calculate if Bless tokens actually exist
    if b > 0:
        aa = CDF(x + 2, b - 1, c)
    else:
        aa = 0
        
    # 3. Curse Path: Only calculate if Curse tokens actually exist
    if c > 0:
        aaa = CDF(x - 2, b, c - 1)
    else:
        aaa = 0
        
    # 4. Final Probability Calculation
    total_tokens = n + b + c
    return a * (n / total_tokens) + aa * (b / total_tokens) + aaa * (c / total_tokens)



b_values = [0, 3, 7]
c_values = [0, 3, 7]

# plt.subplots(rows, columns) creates a 3x3 grid
# figsize=(width, height) makes the window large enough to read easily
fig, axes = plt.subplots(3, 3, figsize=(15, 12))

# Loop through the rows (b values) and columns (c values)
for row, b in enumerate(b_values):
    for col, c in enumerate(c_values):
        
        # Calculate your y values for the current combination of b and c
        
        y = []
        for val in x:
            y.append(CDF(val, b, c))
        inte=2*CDF(1, b, c)+CDF(2, b, c)+CDF(0, b, c)
        # Select the specific subplot in the 3x3 grid using the row/col index
        ax = axes[row, col]
        inte=2*(math.log(inte)-math.log(x_c))/math.log(x_as)
        # Plot the data on this specific subplot
        ax.plot(x, y)
        ax.plot(x,y1)
        ax.grid(True)
        ax.set_title(f"Bless {b} Curse {c} Add {inte:.2f}")
        
        # Only add labels to the outer edges to keep the grid clean
        if row == 2:
            ax.set_xlabel("Test Modifier (x)")
        if col == 0:
            ax.set_ylabel("Probability")

# tight_layout() automatically adjusts the spacing so labels and titles don't overlap
plt.tight_layout()

# Display all 9 graphs simultaneously
plt.show()




def TCDF( b):
    # 1. Base Case: Stop recursion if there are no special tokens left
    if b == 0:
        return 0
    
    # 2. Bless Path: Only calculate if Bless tokens actually exist
    if b > 0:
        aa = TCDF( b - 1)
    else:
        aa = 0
        
    # 4. Final Probability Calculation 
    return aa + (n)/b


x = [0,1, 2, 3, 4,5,6,7,8,9,10,11,12,13,14,15,16]
y=[]
for i in x:
    y.append(TCDF(i))

plt.plot(x, y)
plt.grid(True)
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.title("Line Plot with Grid")
plt.show()
#Add agrees with b-c*2/turns, except when c>b when it dominates it gets between 1.5 and double the negative add than expected.
