import sys

def mean( data ):
	    n = len( data )
	    if n < 1:
	        return 0.00

	    return sum( data ) / n

def _ss( data ):
    c = mean( data )
    ss = sum( ( x - c ) ** 2 for x in data )
    return ss

def pstdev( data ):
    n = len( data )
    if n < 2:
        return 0.00

    ss = _ss( data )
    pvar = ss / n
    return pvar ** 0.5

param = sys.argv[1:]
filename = param[0]

file = open( filename, "r" )

finish = False
read = False
inst = 'aa'
tms = {}
its = {}
vls = {}
fmed = 0
fit = 0

durations = ['25', '50', '100', '200']

while not finish:
	line = file.readline()

	if not line:
		finish = True

	else:
		line = line.split()
		#print line
		#print inst, line[0] + line[1]
		if inst != line[0] + line[1]:
			#print len( tms )
			if len( tms ) > 0:
				print ''
				print inst
				for d in durations:					
					print d, str( '{0:,.2f}'.format( mean( tms[d] ) ) ), str( '{0:,.2f}'.format( pstdev( tms[d] ) ) )
					print d, str( '{0:,.2f}'.format( mean( vls[d] ) ) ), str( '{0:,.2f}'.format( pstdev( vls[d] ) ) )
					print d, str( '{0:,.2f}'.format( mean( its[d] ) ) ), str( '{0:,.2f}'.format( pstdev( its[d] ) ) )

			tms = {}
			its = {}
			vls = {}

			inst = ''
			inst = ( line[0] + line[1] )
			#print 'here', inst

		#print tms, line[2], tms.get( line[2] )

		if tms.get( line[2] ) is None:
			tms[line[2]] = []
			vls[line[2]] = []
			its[line[2]] = []

		tms[line[2]].append( float( line[6] ) )
		vls[line[2]].append( int( line[4] ) )
		its[line[2]].append( int( line[5] ) )		

file.close()

print ''
print inst
for d in durations:					
	print d, str( '{0:,.2f}'.format( mean( tms[d] ) ) ), str( '{0:,.2f}'.format( pstdev( tms[d] ) ) )
	print d, str( '{0:,.2f}'.format( mean( vls[d] ) ) ), str( '{0:,.2f}'.format( pstdev( vls[d] ) ) )
	print d, str( '{0:,.2f}'.format( mean( its[d] ) ) ), str( '{0:,.2f}'.format( pstdev( its[d] ) ) )