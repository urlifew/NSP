import random
import math
import time
import copy

import validator
from roster_parser import ParseRoster

class SolutionInstance:
	'''
	schedule = {staffId: list(shiftId)}
	'''
	def __init__(self):
		self.horizon = 0
		self.score = 0
		self.hardViolations = 0
		self.schedule = dict()

	def ShallowCopy(self):
		result = SolutionInstance()
		result.horizon = self.horizon
		result.score = self.score
		result.schedule = {x: y for x, y in self.schedule.items()}
		return result

	def PrintDebug(self):
		for staff, schedule in self.schedule.items():
			print('solution.schedule[\'{}\'] ='.format(staff), schedule)

	def Show(self):
		for schedule in self.schedule.values():
			print('\t'.join(schedule).replace(' ', ''))

def CreateEmptySolution(problem):
	result = SolutionInstance()
	result.horizon = problem.horizon

	for staffId in problem.staff.keys():
		result.schedule[staffId] = [' '] * horizon

	return result

instance1_optimal_solution = SolutionInstance()
instance1_optimal_solution.horizon = 14
instance1_optimal_solution.score = 607
instance1_optimal_solution.hardViolations = 0
instance1_optimal_solution.schedule['A'] = [' ', 'D', 'D', 'D', 'D', ' ', ' ', 'D', 'D', ' ', ' ', 'D', 'D', 'D']
instance1_optimal_solution.schedule['B'] = ['D', 'D', 'D', 'D', 'D', ' ', ' ', 'D', 'D', ' ', ' ', 'D', 'D', ' ']
instance1_optimal_solution.schedule['C'] = ['D', 'D', 'D', ' ', ' ', 'D', 'D', ' ', ' ', 'D', 'D', ' ', ' ', ' ']
instance1_optimal_solution.schedule['D'] = ['D', 'D', ' ', ' ', ' ', 'D', 'D', 'D', 'D', 'D', ' ', ' ', ' ', ' ']
instance1_optimal_solution.schedule['E'] = [' ', 'D', 'D', 'D', 'D', ' ', ' ', 'D', 'D', ' ', ' ', 'D', 'D', 'D']
instance1_optimal_solution.schedule['F'] = ['D', 'D', 'D', ' ', ' ', ' ', ' ', 'D', 'D', 'D', ' ', ' ', 'D', 'D']
instance1_optimal_solution.schedule['G'] = [' ', ' ', 'D', 'D', 'D', ' ', ' ', 'D', 'D', ' ', ' ', 'D', 'D', 'D']
instance1_optimal_solution.schedule['H'] = ['D', 'D', ' ', ' ', 'D', 'D', ' ', ' ', 'D', 'D', 'D', 'D', ' ', ' ']

instance1_solution = SolutionInstance()
instance1_solution.horizon = 14
instance1_solution.score = 708
instance1_solution.hardViolations = 0
instance1_solution.schedule['A'] = [' ', 'D', 'D', 'D', 'D', ' ', ' ', 'D', 'D', ' ', ' ', 'D', 'D', 'D']
instance1_solution.schedule['B'] = ['D', 'D', 'D', 'D', 'D', ' ', ' ', 'D', 'D', ' ', ' ', 'D', 'D', ' ']
instance1_solution.schedule['C'] = ['D', 'D', 'D', ' ', ' ', 'D', 'D', ' ', ' ', 'D', 'D', 'D', ' ', ' ']
instance1_solution.schedule['D'] = ['D', 'D', ' ', ' ', ' ', 'D', 'D', 'D', 'D', 'D', ' ', ' ', ' ', ' ']
instance1_solution.schedule['E'] = [' ', 'D', 'D', 'D', 'D', ' ', ' ', 'D', 'D', ' ', ' ', 'D', 'D', 'D']
instance1_solution.schedule['F'] = ['D', 'D', 'D', 'D', 'D', ' ', ' ', 'D', 'D', ' ', ' ', ' ', 'D', 'D']
instance1_solution.schedule['G'] = [' ', ' ', 'D', 'D', 'D', ' ', ' ', 'D', 'D', ' ', ' ', 'D', 'D', 'D']
instance1_solution.schedule['H'] = ['D', 'D', ' ', ' ', ' ', ' ', ' ', ' ', 'D', 'D', 'D', 'D', 'D', ' ']

fullSchedule = SolutionInstance()
fullSchedule.horizon = 14
fullSchedule.score = -1
fullSchedule.hardViolations = -1
fullSchedule.schedule['A'] = ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D']
fullSchedule.schedule['B'] = ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D']
fullSchedule.schedule['C'] = ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D']
fullSchedule.schedule['D'] = ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D']
fullSchedule.schedule['E'] = ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D']
fullSchedule.schedule['F'] = ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D']
fullSchedule.schedule['G'] = ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D']
fullSchedule.schedule['H'] = ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D']

'''
Simulated Annealing has 4 major parts:
	1. A valid start configuration
	2. A random rearrangement scheme
	3. An objective function
	4. An annealing schedule
'''

#print (list(exact_solution.schedule.keys()))
#print (random.choice(list(exact_solution.schedule.keys())))

def NeighbourMove_TotalReorder(solution, **kw):
	staffId = random.choice(list(solution.schedule.keys()))
	schedule = solution.schedule[staffId]
	startIndex = [0]

	prevShift = schedule[0]
	currShift = ''

	# Find all bounds between different shifts
	for idx in range(1, solution.horizon):
		currShift = schedule[idx]
		if currShift != prevShift:
			startIndex.append(idx)
		prevShift = currShift

	reorderIndex = random.choice(startIndex)
	solution.schedule[staffId] = schedule[reorderIndex:] + schedule[:reorderIndex]

def NeighbourMove_PartialReorder(solution, **kw):
	staffId = random.choice(list(solution.schedule.keys()))
	schedule = solution.schedule[staffId]
	startIndex = [0]

	prevShift = schedule[0]
	currShift = ''

	# Find all bounds between different shifts
	for idx in range(1, solution.horizon):
		currShift = schedule[idx]
		if currShift != prevShift:
			startIndex.append(idx)
		prevShift = currShift

	# Edge case: whole schedule is only one shift
	if len(startIndex) == 1:
		return

	seq1, seq2 = 0, 0
	while seq1 == seq2:
		seq1 = random.randint(0, len(startIndex) - 1)
		seq2 = random.randint(0, len(startIndex) - 1)

	if seq1 > seq2:
		seq1, seq2 = seq2, seq1

	startIndex.append(solution.horizon)

	start1 = startIndex[seq1]
	end1 = startIndex[seq1 + 1]
	start2 = startIndex[seq2]
	end2 = startIndex[seq2 + 1]

	# [0, 1, 5, 7, 9, 11]
	# 4 1 => [1, 5), [9, 11)
	#
	# solution.schedule['A'] = [' ', <'D', 'D', 'D', 'D'>, ' ', ' ', 'D', 'D', <' ', ' '>, 'D', 'D', 'D']
	# solution.result  ['A'] = [' ', <' ', ' '>, ' ', ' ', 'D', 'D', <'D', 'D', 'D', 'D'>, 'D', 'D', 'D']

	solution.schedule[staffId] = \
		schedule[:start1] + \
		schedule[start2:end2] + \
		schedule[end1:start2] + \
		schedule[start1:end1] + \
		schedule[end2:]

def NeighbourMove_SegmentShift(solution, annealCoeff = 0.25, **kw):
	staffId = random.choice(list(solution.schedule.keys()))
	schedule = solution.schedule[staffId]

	segmentLength = max(int(len(schedule) * annealCoeff), 1)
	segmentStart = random.randint(0, len(schedule) - segmentLength)

	shiftDist = 0
	while shiftDist == 0:
		shiftDist = random.randint(-segmentStart, len(schedule) - segmentStart + segmentLength)

	if shiftDist < 0:
		solution.schedule[staffId] = \
			schedule[: segmentStart + shiftDist] + \
			schedule[segmentStart : segmentStart + segmentLength] + \
			schedule[segmentStart + shiftDist : segmentStart] + \
			schedule[segmentStart + segmentLength:]
	else:
		solution.schedule[staffId] = \
			schedule[: segmentStart] + \
			schedule[segmentStart + segmentLength : segmentStart + segmentLength + shiftDist] + \
			schedule[segmentStart : segmentStart + segmentLength] + \
			schedule[segmentStart + segmentLength + shiftDist :]

def NeighbourMove_SwitchShift(solution, **kw):
	staffId = random.choice(list(solution.schedule.keys()))
	newShift = random.choice(kw['shiftTypes'])
	day = random.randint(0, solution.horizon - 1)
	solution.schedule[staffId][day] = newShift

# Moves with their relative weight
neighbourMoves = [
	[NeighbourMove_TotalReorder, 1],
	[NeighbourMove_PartialReorder, 1],
	[NeighbourMove_SegmentShift, 1],
	[NeighbourMove_SwitchShift, 1]
]

def MakeAccum(moves):
	totalWeight = sum([x[1] for x in neighbourMoves])
	accum = 0.0
	for idx, x in enumerate(neighbourMoves):
		accum += x[1] / totalWeight
		moves[idx][1] = accum
	moves[-1][1] = 1.0

def ChooseMove(moves):
	p = random.random()
	idx = 0
	while moves[idx][1] < p:
		idx += 1
	return moves[idx][0]

def FixDaysOff(solution, problem):
	for staffId, staffMember in problem.staff.items():
		schedule = solution.schedule[staffId]
		for idx in staffMember.daysOff:
			if schedule[idx] != ' ':
				otherIdx = idx
				while otherIdx in staffMember.daysOff:
					otherIdx = random.randint(0, problem.horizon - 1)
				schedule[idx], schedule[otherIdx] = schedule[otherIdx], schedule[idx]

def FixSolution(solution, problem):
	FixDaysOff(solution, problem)

def Anneal(problem, maxTime = float('inf'), runs = 1):
	'''
	Try to solve the given problem while not exceeding 'maxTime'.
	'runs' is the number of tries to solve the problem. Each try should start from
	a different random configuration.
	'''
	# Solution variables
	timePerInstance = maxTime / runs
	bestSolution = fullSchedule
	bestValidSolution = None
	validator.CalculatePenalty(bestSolution, problem)

	# Annealing variables
	mu = -2.0

	# Initialization
	MakeAccum(neighbourMoves)
	allShiftTypes = list(problem.shifts.keys())
	allShiftTypes.append(' ')
	
	validator.CalculatePenalty(fullSchedule, problem)

	for r in range(runs):
		# solution = GenerateRandomSolution(problem)
		solution = fullSchedule
		validator.CalculatePenalty(solution, problem)

		print ('Starting run<{}> with score {}'.format(r, solution.score))

		endTime = time.time() + timePerInstance

		while True:
			now = time.time()
			if (time.time() > endTime):
				break

			newSolution = copy.deepcopy(solution)

			ChooseMove(neighbourMoves)(newSolution, shiftTypes=allShiftTypes)
			
			FixSolution(newSolution, problem)

			validator.CalculatePenalty(newSolution, problem)

			#
			if newSolution.score < solution.score or \
				random.random() < math.exp(mu * (newSolution.score - solution.score)):
				if newSolution.score > solution.score:
					print('delta E =', (newSolution.score - solution.score))
					print('Chance for move is', math.exp(mu * (newSolution.score - solution.score)))
				solution = newSolution
				if solution.hardViolations == 0 and bestValidSolution.score > solution.score:
					bestValidSolution = solution
					print('Found better valid solution:', bestValidSolution.score)

				if bestSolution.score > solution.score:
					bestSolution = solution
					print('Found better solution:', bestSolution.score)

	if bestValidSolution is None:
		return bestSolution
	else:
		return bestValidSolution