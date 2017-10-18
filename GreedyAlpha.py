from random import *
import os
import sys

class GreedyA:
	m = 0	# variables
	n = 0	# clauses
	clauses = set()	# set of clauses
	dicClauses = {}
	attempt = []
	unsatisfiedClauses = set()

	def __init__( self, filename ):
		file = open( filename, "r" )
		finish = False
		read = False
		
		clause = []

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

		print self.dicClauses

	def invValue( self, v ):
		if v == 0:
			return 1
		else:
			return 0

	def isSatisfiedClause( self, clause ):
		clauseValue = 0
		for variable in clause:
			ab = abs( int( variable ) )
			if int( variable ) < 0:
				value = self.invValue( self.attempt[ab] )
			else:
				value = self.attempt[ab]

			clauseValue += value

		return clauseValue > 0

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

	def run( self ):
		res = []
		var = []
		for i in xrange( 1, self.n + 1 ):
			var.append( i )

		while len( var ) > 0:

			for i in var:
				for j in xrange( 0, 2 ):
					f = i+j

			x = choice( var )
			v = randint( 0, 1 )
			var.remove( x )
			#print x, v
		#print var

param = sys.argv[1:]
filename = param[0]

ga = GreedyA( filename )
ga.run()