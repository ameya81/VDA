# Simulated Annealing Algorithm for Circuit/Graph Partitioning
# Authors: Samarth Bonthala, Tarun Mittal
  
import random
import math
import os
from Netlist_Matrix_Conv import netlist_to_adj_mat

# Function to check if n is a power of 2 or not
def isPowerOfTwo(n): 
    if (n == 0): 
        return False
    while (n != 1): 
            if (n % 2 != 0): 
                return False
            n = n // 2
              
    return True
    
# Input Function
def input_func(filename):

	f = open(filename,'r')

	data = f.readlines()
	adj_matrix = []

	for i in data:
		temp = i.split()
		temp = [int(j) for j in temp]
		adj_matrix.append(temp)
  	
  	return adj_matrix;
  	
# Calculate imbalance factor dynamically according to no of nodes
def imbalance_calc(no_of_nodes):
	a = -0.00003
	b = 0.05
	c = 1.3

	cost_func_factor = 1/(a*(no_of_nodes*no_of_nodes) + b*(no_of_nodes) + c)

	return cost_func_factor

# Computing the cost function
# f = C + lambda*(Imbalance)
# C = cutsize (sum of edge weights of all the crossover edges from A to B)
# Imbalance = (no_of_nodes_A - no_of_nodes_B)^2
# Returns cost and cutsize
	
def cost_func(A, B, adj_matrix, cost_func_factor):

	cutsize = 0

	for i in A:
		for j in B:
			cutsize = cutsize + adj_matrix[i][j]

	lenA = len(A)
	lenB = len(B)

	imbalance_fact = (lenA - lenB)**2

	cost = cutsize + cost_func_factor*imbalance_fact

	return cost,cutsize

# Function for Simulated Annealing Algorithm
# Heuristic Algorithm for Partitioning
# Inputs: adj_matrix and number of partitions needed, n

def Sim_Ann(adj_matrix):
	
	# Spl[it into two equal partitions randomly
	A = []
	B = []
	
	no_of_nodes = len(adj_matrix[0])
	
	for i in range(no_of_nodes):
		if (i < no_of_nodes/2):
			A.append(i)
		else:
			B.append(i)
		
	# Portion of code for initial temperature calculation
	# Idea: Run the algorithm for 4 times and compute difference in cutsize between the consecutive iterations
	# Compute average and back calculate and obtain the initial temperature
	
	temp_part_A = A[:]
	temp_part_B = B[:]
	loop = 0
	init_temp_arr = []

	cost_func_factor = imbalance_calc(no_of_nodes)
	
	while(loop < 4):
		x1 = random.randint(0, no_of_nodes-1)
		if x1 in temp_part_A:
			temp_part_A.remove(x1)
			temp_part_B.append(x1)
		else:
			temp_part_B.remove(x1)
			temp_part_A.append(x1)

		cst, init_cutsize = cost_func(temp_part_A, temp_part_B, adj_matrix, cost_func_factor)
		init_temp_arr.append(cst)
		loop = loop + 1
		
	i = 0
	sum = 0
	while(i<3):
		sum = sum + abs(init_temp_arr[i+1] - init_temp_arr[i])
		i = i+1
		
	avg_cost = sum/3
	initial_temperature = -avg_cost/math.log(0.9)
		
	print "Initial Temperature calculated:",initial_temperature
		
	tempfact = 0.85 # r value in (r^i)*T
	temperature = 1 # T value
	temp_iteration = 1 # iteration number
	
	A_temp = A
	B_temp = B
	
	A_res = A_temp
	B_res = B_temp

	cost, cutsize = cost_func(A, B, adj_matrix, cost_func_factor)
	cost_temp = 0
	cutsize_temp = 0

	reject = 0
	temp_reject = 0
	
	# Keeping track of the best solution obtained so far - Global minima
	best_part_A = A[:]
	best_part_B = B[:]
	best_cost = cost
	
	# Starting the iterations
	
	while(temp_reject<5):

		x = random.randint(0, no_of_nodes-1)
		
		if x in A:
			A_temp.remove(x)
			B_temp.append(x)
		else:
			B_temp.remove(x)
			A_temp.append(x)

		cost_temp, cutsize_temp = cost_func(A_temp, B_temp, adj_matrix, cost_func_factor)
		# If solution is accepted and cost has decreased, choose the best option
		if(cost < best_cost):
			best_cost = cost
			best_part_A = A_temp[:]
			best_part_B = B_temp[:]
			
		delta_cost = cost_temp - cost

		#print "Delta_cost" + str(delta_cost)
		#print "Cutsize" + str(cutsize_temp)

		if(delta_cost <= 0): # Accept the soltuion when the cost decreases from previous iteration
			A = A_temp[:]
			B = B_temp[:]
			A_res = A
			B_res = B
			cost = cost_temp
			cutsize = cutsize_temp
			reject = 0
			temp_reject = 0
		elif ( math.exp(-(delta_cost/temperature)) > random.uniform(0,1)): # Accept the solution with a probability
			#print "tp" + str (math.exp(-(delta_cost/temperature))) + str(random.uniform(0,1))
			A = A_temp[:]
			B = B_temp[:]
			A_res = A
			B_res = B
			cost = cost_temp
			cutsize = cutsize_temp
			reject = 0
			temp_reject = 0
		else: # Increment reject counter and keep track of number of rejections 
			reject = reject + 1
			#print "Rejected Iteration" + str(reject)
			A_temp = A[:]
			B_temp = B[:]
			if(reject >= 5): # If number of rejections for a particular temperature is greater than 5, go to next temperature
				temp_reject = temp_reject + 1
				temperature = temperature*math.pow(tempfact,temp_iteration) 
				temp_iteration = temp_iteration + 1 # Update the temperature iteration
				if(temp_iteration>5): # Terminate the algorithm once 5 temperatures have been rejected
					temp_reject = 10
				#print "Rejected_Temperature: " + str(temp_reject)


	return best_part_A,best_part_B,best_cost
	
	
def main():

	print ("Enter the name of the file containing the required netlist")
	filename = raw_input("\n")
	
	# Converting the netlist to adjacency matrix
	netlist_to_adj_mat(filename)
	
	# Take input from the text file containing the adjacency matrix of unpartitioned graph
	adj_matrix = input_func("inp_adj_mat.txt")
	
	A,B,cost = Sim_Ann(adj_matrix)
	print "\nBest Partition obtained through Simulated Annealing is as follows:"
	print "Partition A:", A
	print "Partition B:", B
	print "Least cost:",cost
		 
main()

