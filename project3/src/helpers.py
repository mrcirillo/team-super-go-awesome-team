import os
import inspect
import numpy
from itertools import takewhile
import random

# helper to write files with relative locations
thisFileLocation = os.path.dirname(inspect.stack()[0][1])


def fileRelativeToHere(relativePath):
	return os.path.abspath(os.path.join(thisFileLocation, relativePath))


# parse in a dataset from the data folder by name
# argStart index is where to start slicing a line to capture all args
# argEnd index is were to stop slicing args
# class is the index where the class label is located
# example for zoo dataset
# x, y = helpers.readDatasetFromFile('zoo.data', 1, -1, -1)
# zoo dataset has a non-feature in the first position so start looking at 
# index 1. features continue until the last index, which is the class label
# output is a tuple (x, y) where x is a matrix of input vectors, y is a matrix of output vectors
def readDatasetFromFile(filename, argStartIndex, argEndIndex, classIndex):
	x = []
	y = []
	outs = {}
	outCount = 0
	with open('../data/' + filename, 'r') as f:
		for line in f:
			linearr = line.split(',')
			arg = numpy.fromiter(map(float, linearr[argStartIndex : argEndIndex]), numpy.float64)
			
			output = linearr[classIndex]
			if output not in outs:
				outs[output] = outCount
				outCount += 1

			x.append(arg)
			y.append(output)
			
	possibleYs = len(outs)
	ytransformed = []
	for it in y:
		zeros = [0] * possibleYs
		zeros[outs[it]] = 1
		ytransformed.append(numpy.array(zeros))

	return (numpy.array(x), numpy.array(ytransformed))

def readZooData():
	return readDatasetFromFile('zoo.data', 1, 17, -1) # need shape [16 .. 7]

def readLeafData():
	return readDatasetFromFile('leaf.csv', 2, 16, 0) # need shape [14 ... 30]

def readPokerData():
	return readDatasetFromFile('poker-hand-training-true.data', 0, 10, 10) # need shape [10 ... 10]

def readGlassData():
	return readDatasetFromFile('glass.data', 1, 10, 10) # need shape [9 ... 7]

def readWineData():
	return readDatasetFromFile('wine.data', 1, 14, 0) # need shape [13 ... 3]

# CV helpers
def get2Fold(x, y):
	zipped = list(zip(x,y))
	return get_mini_batches(zipped, int(len(x) / 2) + 1)
	
# given a dataset, return minibatches using a random sampling with replacement mechanism
def get_mini_batches(dataset, batch_size):
	random_idxs = numpy.random.choice(len(dataset), len(dataset), replace=False)
	X_shuffled = list(map(lambda i: dataset[i], random_idxs))
	mini_batches = [X_shuffled[i:i+batch_size] for i in range(0, len(dataset), batch_size)]
	return mini_batches

def rankBasedSelection(pop, sortFit, numParents):
	parents = []
	n = len(pop)
	#expected number of offspring generated by the best individual
	lam1 = 1.99
	#expected number of offspring generated by the best individual
	lam2 = 2-lam1

	Pxi = []
	wheel = []

	#assign probability of selection
	#calculate cumulative fitness and make roulette wheel
	for i in range(len(pop)):
		#normalizer
		Pxi.append((lam2 + (i/(n-1)) * (lam1 - lam2)) / n)
		wheel.append(sum(Pxi))

	parents = random.choices(sortFit, cum_weights=wheel, k=numParents)
	return parents

def percentCorrect(networkOut, actualY):
	corrects = [hi.argmax() == yi.argmax() for hi, yi in zip(networkOut, actualY)]
	it = (numpy.sum(corrects) / len(actualY)) * 100
	return it

def crossValid(creationFunction, n, x, y, maxGen):
	#create n instances of 2 fold cross validation
	pops=[]
	allTrainErr = []
	allValErr = []
	minVals = []
	minTrains = []

	for i in range(n):
		#get ya folds
		train, val = get2Fold(x, y)
		trainX, trainY = zip(*train)
		trainX = numpy.array(trainX)
		trainY = numpy.array(trainY)

		valX, valY = zip(*val)
		valX = numpy.array(valX)
		valY = numpy.array(valY)
		#build ya pops
		pops.append(creationFunction()) #

	#train pops, capture stat info
	for pop in pops:
		pop.train(trainX,trainY, valX, valY, maxGen)

		allTrainErr.append(pop.trainingErrors)
		minTrains.append(pop.trainingErrors[-1])
		allValErr.append(pop.validationErrors)
		minVals.append(numpy.min(pop.validationErrors))
		

	#gather means to REEEEEEEEEEEport
	avgTrainErr = numpy.mean(minTrains)
	avgValErr = numpy.mean(minVals)

	return(avgTrainErr, avgValErr, allTrainErr, allValErr)

