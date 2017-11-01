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

	def run( self, k ):
		self.k = k
		seed( time.time() )
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

		return self.countSatisfiedClauses( self.clauses )

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
		file.write( "d<-read.table( 'results/greedy/" + name + "_" + str( self.alpha * value ) + ".dat' )\n" )
		file.write( "png( 'results/greedy/" + name + "_" + str( self.alpha * value ) + ".png' )\n" )
		file.write( "hist( d$V1, main = 'alpha = " + str( self.alpha * value ) + "', xlab = 'Satisfied clauses' )\n" )
		file.write( "dev.off()\n" )
		file.write( "q()" )
		file.close()

		os.system( "Rscript histogram.r" )

param = sys.argv[1:]
filename = param[0]
k = [0, 1, 2, 3, 4, 5]
solutions = 1000

ga = GreedyA( filename )
name = ( filename.split( '.' )[0] ).split( '/' )[-1]
f = filename.split( "/" )[1]
nfile = f.replace( ".cnf", '' )
pattern = "{:9s}{:14s}{:3s}{:7s}{:10s}"
file = open( "resultsGreedy" + nfile + ".txt", 'a' )
file.write( pattern.format( "alg", "instance", "k", "rep", 'v' ) + '\n' )
file.close()
pattern = "{:9s}{:14s}{:<3d}{:<7d}{:<10d}"

for v in k:
	totalS = 0
	totalT = 0
	contentResults = ''
	contentTime = ''

	for i in xrange( 1, solutions + 1 ):
		start = time.time()
		result = ga.run( v )
		end = time.time() - start		
		contentResults += str( result ) + '\n'
		contentTime += str( end ) + '\n'
		totalS += result
		totalT += end

		file = open( "resultsGreedy" + nfile + ".txt", 'a' )
		file.write( pattern.format( "C", nfile, v, i, result ) + '\n' )
		file.close()

	print v
	print 'time', totalT, totalT/( solutions * 1.0 )
	print 'sol', totalS, totalS/solutions

	file = open( "results/greedy/time_" + name + "_" + str( 0.2 * v ) + ".dat", "w" )
	file.write( contentTime )
	file.close()
	file = open( "results/greedy/" + name + "_" + str( 0.2 * v ) + ".dat", "w" )
	file.write( contentResults )
	file.close()	

	ga.generateHistogram( name, v )