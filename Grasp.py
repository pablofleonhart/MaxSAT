from random import *
import copy
import os
import sys
import time

class GreedyA:
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

		#print self.dicClauses

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
			#print variable, value

			if self.attempt[ab] >= 0:
				hasValidValue = True

		#print clause, self.attempt, clauseValue > 0
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

	def countClauses( self, clauses ):
		sat = 0
		unsat = 0
		for clause in clauses:
			if self.isSatisfiedClause( clause ):
				sat += 1
			else:
				unsat += 1

		return sat, unsat

	def rankingPairs( self, pair ):
		#print 'pair', pair
		variable = pair[0]
		value = pair[1]
		clausesToEvaluate = self.dicClauses[variable]

		unsBefore = self.countUnsatisfiedClauses( clausesToEvaluate )
		#print 'u', unsBefore
		#print self.countClauses( clausesToEvaluate )
		originalValue = self.attempt[variable]
		self.attempt[variable] = value
		unsAfter = self.countUnsatisfiedClauses( clausesToEvaluate )
		#print 'u2', unsAfter
		#brokenClauses = self.countClauses( clausesToEvaluate )
		#self.attempt[variable] = self.invertValue( self.attempt[variable] )
		#brokenClausesFlipped = self.countUnsatisfiedClauses( clausesToEvaluate )
		#self.attempt[variable] = self.invertValue( self.attempt[variable] )
		self.attempt[variable] = originalValue
		#broken = brokenClausesFlipped - brokenClauses
		#print pair, broken, brokenClausesFlipped, brokenClauses
		#print brokenClauses
		self.improves.append( ( variable + ( self.n * value ), unsBefore - unsAfter ) )

	def getVariable( self, remainingVars ):
		self.improves = []
		for i in remainingVars:
			for j in xrange( 0, 2 ):
				self.rankingPairs( ( i, j ) )
		
		self.improves = self.sort( self.improves )
		#print self.improves

		#select variable according with alpha parameter
		#print self.n * self.alpha
		limiar = int( round( self.n * self.alpha * self.k ) )
		if limiar == 0:
			limiar = 1
		#print choice( self.improves[:limiar] )
		variable = choice( self.improves[:limiar] )[0]
		value = 0

		if variable > self.n:
			variable -= self.n
			value = 1

		#print variable, value
		return variable, value

	def countGains( self, variable ):
		#print self.dicClauses[variable]

		clausesToEvaluate = self.dicClauses[variable]
		brokenClauses = self.countUnsatisfiedClauses( clausesToEvaluate )
		self.attempt[variable] = self.invertValue( self.attempt[variable] )
		brokenClausesFlipped = self.countUnsatisfiedClauses( clausesToEvaluate )
		self.attempt[variable] = self.invertValue( self.attempt[variable] )
		gain = brokenClauses - brokenClausesFlipped

		#print gain
		return gain

	def localSearch( self ):
		gain = 1		
		while gain > 0:
			gains = []
			gain -= 1
			for x in xrange( 1, self.n + 1 ):
				gains.append( ( x, self.countGains( x ) ) )

			gains = self.sort( gains )
			gain = gains[0][1]
			print self.attempt
			self.attempt[gains[0][0]] = self.invertValue( self.attempt[gains[0][0]] )
			print 'g', gains, gain
			print self.attempt

	def run( self, k ):
		self.k = k
		seed( time.time() )
		self.unsatisfiedClauses = copy.deepcopy( self.clauses )
		self.attempt = [-1 for x in xrange( self.n + 1 )]
		var = []
		for i in xrange( 1, self.n + 1 ):
			var.append( i )

		while len( var ) > 0:
			#print '################################################################'
			'''for i in var:
				for j in xrange( 0, 2 ):
					self.rankingPairs( ( i, j ) )

			print self.improves
			self.improves = self.sort( self.improves )
			variable = self.improves[0][0]
			value = 0

			if variable > self.n:
				variable -= self.n
				value = 1'''

			pair = self.getVariable( var )
			#print pair
			x = pair[0]
			v = pair[1]
			#x = choice( var )
			#v = randint( 0, 1 )
			var.remove( x )
			self.attempt[x] = v
			#print 'v', self.countSatisfiedClauses( self.clauses )
			#print 'remove', self.improves[0][0]
			#self.rankingPairs( ( x, v ) )
			#print x, v
		#print var
		#print self.attempt
		res = self.countSatisfiedClauses( self.clauses )
		'''file = open( "results/" + self.name + "_" + str( self.alpha * k ) + ".dat", "a" )
		file.write( str( res ) + "\n" )
		print 'v', res
		file.close()'''
		#print 'v', res
		self.localSearch()
		return res

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
k = [5]
solutions = 1000

ga = GreedyA( filename )
name = ( filename.split( '.' )[0] ).split( '/' )[-1]

for v in k:
	total = 0
	contentResults = ''
	start = time.time()

	for i in xrange( solutions ):
		result = ga.run( v )
		#ga.localSearch()
		contentResults += str( result ) + '\n'
		total += result

	end = time.time() - start
	print v
	print 'time', end, end/(solutions*1.0)
	file = open( "results/" + name + "_" + str( 0.2 * v ) + ".dat", "w" )
	file.write( contentResults )
	file.close()
	print 'avg', total, total/solutions

	ga.generateHistogram( name, v )