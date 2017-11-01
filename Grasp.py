from random import *
import copy
import os
import sys
import time

class Grasp:
	m = 0	# variables
	n = 0	# clauses
	clauses = set()	# set of clauses
	dicClauses = {}
	attempt = []
	unsatisfiedClauses = set()
	improves = []
	alpha = 0.2
	k = 0
	name = ''
	prob = 0.5

	def __init__( self, filename ):
		file = open( filename, "r" )
		finish = False
		read = False
		clause = []		
		self.name = ( filename.split( '.' )[0] ).split( '/' )[-1]

		while not finish:
		    line = file.readline()

		    if not line:
		        finish = True

		    else:
		        line = line.split()
		        
		        if len( line ) > 0:
		            if line[0] == 'p':
		                self.n = int( line[2] )
		                self.m = int( line[3] )
		                read = True

		            elif read:
		            	for i in xrange( len( line ) ):
		            		if line[i] == '0':
		            			self.clauses.add( tuple( clause ) )
		            			clause = []
		            		else:
		            			clause.append( line[i] )

		if len( self.clauses ) < self.m:
			self.clauses.add( tuple( clause ) )

		file.close()

		for clause in self.clauses:
			for literal in clause:
				literal = abs( int( literal ) )
				if literal not in self.dicClauses:
					self.dicClauses[literal] = set()
				self.dicClauses[literal].add( tuple( clause ) )

	def invertValue( self, value ):
		if value == 0:
			return 1
		else:
			return 0

	def isSatisfiedClause( self, clause ):		
		hasValidValue = False
		clauseValue = 0
		for variable in clause:
			ab = abs( int( variable ) )
			if int( variable ) < 0:
				value = self.invertValue( self.attempt[ab] )
			else:
				if self.attempt[ab] < 0:
					value = 0
				else:
					value = self.attempt[ab]

			clauseValue += value

			if self.attempt[ab] >= 0:
				hasValidValue = True

		return clauseValue > 0 and hasValidValue

	def satisfies( self, variable ):
		if variable:
			if variable in self.dicClauses:
				for clause in self.dicClauses[variable]:
					if self.isSatisfiedClause( clause ):
						if clause in self.unsatisfiedClauses:
							self.unsatisfiedClauses.remove( clause )
					else:
						if clause not in self.unsatisfiedClauses:
							self.unsatisfiedClauses.add( clause )
		else:
			self.unsatisfiedClauses.clear()
			for clause in self.clauses:
				if not self.isSatisfiedClause( clause ):
					self.unsatisfiedClauses.add( clause )

		return len( self.unsatisfiedClauses ) == 0

	def countSatisfiedClauses( self, clauses ):
		sat = 0
		for clause in clauses:
			if self.isSatisfiedClause( clause ):
				sat += 1

		return sat

	def countUnsatisfiedClauses( self, clauses ):
		count = 0
		for clause in clauses:
			if not self.isSatisfiedClause( clause ):
				count += 1

		return count

	def rankingPairs( self, pair ):
		variable = pair[0]
		value = pair[1]
		clausesToEvaluate = self.dicClauses[variable]

		unsBefore = self.countUnsatisfiedClauses( clausesToEvaluate )
		originalValue = self.attempt[variable]
		self.attempt[variable] = value
		unsAfter = self.countUnsatisfiedClauses( clausesToEvaluate )
		self.attempt[variable] = originalValue
		self.improves.append( ( variable + ( self.n * value ), unsBefore - unsAfter ) )

	def getLimiar( self ):
		value = self.improves[0][1]
		count = 0
		for v in self.improves:
			if v[1] != value:
				break
			else:
				value = v[1]
				count += 1

		return count

	def getVariable( self, remainingVars ):
		self.improves = []
		for i in remainingVars:
			for j in xrange( 0, 2 ):
				self.rankingPairs( ( i, j ) )
		
		self.improves = self.sort( self.improves )
		limiar = int( round( self.n * self.alpha * self.k ) )
		if limiar == 0:
			limiar = self.getLimiar()

		variable = choice( self.improves[:limiar] )[0]
		value = 0

		if variable > self.n:
			variable -= self.n
			value = 1

		return variable, value

	def countGains( self, variable ):
		clausesToEvaluate = self.dicClauses[variable]
		brokenClauses = self.countUnsatisfiedClauses( clausesToEvaluate )
		self.attempt[variable] = self.invertValue( self.attempt[variable] )
		brokenClausesFlipped = self.countUnsatisfiedClauses( clausesToEvaluate )
		self.attempt[variable] = self.invertValue( self.attempt[variable] )
		gain = brokenClauses - brokenClausesFlipped

		return gain

	def localSearch( self ):
		gain = 1
		iterations = 0
		while gain > 0:
			gains = []
			for x in xrange( 1, self.n + 1 ):
				gains.append( ( x, self.countGains( x ) ) )

			gains = self.sort( gains )
			gain = gains[0][1]

			if gain > 0:
				self.attempt[gains[0][0]] = self.invertValue( self.attempt[gains[0][0]] )
			iterations += 1

		return iterations

	def walkSatLocalSearch( self ):
		iterations = 0
		self.satisfies( None )
		start = time.time()

		while self.unsatisfiedClauses and time.time() - start < 10:
			bestVariable = None
			b = len( self.clauses ) + 1

			if self.unsatisfiedClauses:
				unsatisfiedClause = sample( self.unsatisfiedClauses, 1 )[0]

				for variable in unsatisfiedClause:
					variable = abs( int( variable ) )
					clausesToEvaluate = self.dicClauses[variable]
					brokenClauses = self.countUnsatisfiedClauses( clausesToEvaluate )
					self.attempt[variable] = self.invertValue( self.attempt[variable] )
					brokenClausesFlipped = self.countUnsatisfiedClauses( clausesToEvaluate )
					self.attempt[variable] = self.invertValue( self.attempt[variable] )
					broken = brokenClausesFlipped - brokenClauses

					if broken < b:
						b = broken
						bestVariable = variable

			if b > 0 and random() < self.prob:
				randomVar = randint( 1, self.n )
				self.attempt[randomVar] = self.invertValue( self.attempt[randomVar] )
				variable = randomVar
			else:
				self.attempt[bestVariable] = self.invertValue( self.attempt[bestVariable] )
				variable = bestVariable

			self.satisfies( variable )
			iterations += 1

		return iterations

	def run( self, k, alg ):
		iterations = 0
		self.k = k
		seed( time.time() )
		self.unsatisfiedClauses = copy.deepcopy( self.clauses )
		self.attempt = [-1 for x in xrange( self.n + 1 )]
		var = []
		for i in xrange( 1, self.n + 1 ):
			var.append( i )

		while len( var ) > 0:
			pair = self.getVariable( var )
			x = pair[0]
			v = pair[1]
			var.remove( x )
			self.attempt[x] = v
			iterations += 1

		if alg == 'gsat':
			iterations += self.localSearch()
		elif alg == 'walksat':
			iterations += self.walkSatLocalSearch()

		return self.countSatisfiedClauses( self.clauses ), iterations

	def sort( self, array ):
		less = []
		equal = []
		greater = []

		if len( array ) > 1:
			pivot = array[0][1]
			for x, y in array:
				if y < pivot:
					less.append( ( x, y ) )
				if y == pivot:
					equal.append( ( x, y ) )
				if y > pivot:
					greater.append( ( x, y ) )
			return self.sort( greater ) + equal + self.sort( less )
		else:
			return array

	def generateHistogram( self, name, value ):
		file = open( "histogram.r", "w" )
		file.write( "d<-read.table( 'results/" + name + "_" + str( self.alpha * value ) + ".dat' )\n" )
		file.write( "png( 'results/" + name + "_" + str( self.alpha * value ) + ".png' )\n" )
		file.write( "hist( d$V1, main = 'alpha = " + str( self.alpha * value ) + "', xlab = 'Satisfied clauses' )\n" )
		file.write( "dev.off()\n" )
		file.write( "q()" )
		file.close()

		os.system( "Rscript histogram.r" )

param = sys.argv[1:]
filename = param[0]
alg = param[1]
k = [5]
solutions = 1000

ga = Grasp( filename )
name = ( filename.split( '.' )[0] ).split( '/' )[-1]
f = filename.split( "/" )[1]
nfile = f.replace( ".cnf", '' )
pattern = "{:9s}{:14s}{:3s}{:7s}{:10s}"
file = open( "results" + alg + " " + nfile + ".txt", 'a' )
file.write( pattern.format( "alg", "instance", "k", "rep", 'v' ) + '\n' )
file.close()
pattern = "{:9s}{:14s}{:<3d}{:<7d}{:<10d}"

for v in k:
	totalS = 0
	totalI = 0
	totalT = 0
	contentResults = ''
	contentIt = ''
	contentTime = ''

	for i in xrange( 1, solutions + 1 ):
		start = time.time()
		results = ga.run( v, alg )
		end = time.time() - start		
		sat = results[0]
		it = results[1]
		contentResults += str( sat ) + '\n'
		contentIt += str( it ) + '\n'
		contentTime += str( end ) + '\n'
		totalS += sat
		totalI += it
		totalT += end
		#print results

		file = open( "results" + alg + "_" + str( v ) + nfile + ".txt", 'a' )
		file.write( pattern.format( "G", nfile, v, i, sat ) + '\n' )
		file.close()

		if i%100 == 0:
			file = open( "results/" + alg + "/time_" + name + "_" + str( 0.2 * v ) + ".dat", "a" )
			file.write( contentTime )
			file.close()
			file = open( "results/" + alg + "/it_" + name + "_" + str( 0.2 * v ) + ".dat", "a" )
			file.write( contentIt )
			file.close()
			file = open( "results/" + alg + "/" + name + "_" + str( 0.2 * v ) + ".dat", "a" )
			file.write( contentResults )
			file.close()
			contentResults = ''
			contentIt = ''
			contentTime = ''
			print 'writing...'

	print v
	print 'time', totalT, totalT/( solutions * 1.0 )
	print 'sol', totalS, totalS/solutions
	print 'it', totalI, totalI/solutions

	'''file = open( "results/" + alg + "/time_" + name + "_" + str( 0.2 * v ) + ".dat", "w" )
	file.write( contentTime )
	file.close()
	file = open( "results/" + alg + "/it_" + name + "_" + str( 0.2 * v ) + ".dat", "w" )
	file.write( contentIt )
	file.close()
	file = open( "results/" + alg + "/" + name + "_" + str( 0.2 * v ) + ".dat", "w" )
	file.write( contentResults )
	file.close()'''

	ga.generateHistogram( alg + "/" + name, v )