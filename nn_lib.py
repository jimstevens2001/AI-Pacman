def cont2bin(cont, cnt, hi, low):
	# Convert all inputs to floating point to make the calculations more exact.
	cont = float(cont)
	hi = float(hi)
	low = float(low)

	# Deal with the cases in which the continuous value is higher or
	# lower than the maximum or minimum thresholds.
	if cont >= hi:
		return [1.0]*cnt
	elif cont <= low:
		return [-1.0]*cnt

	val = 2.0 * ((cont - low) / (hi - low)) - 1
	bin = [val]

	return [float(i) for i in bin]

def bin2cont(bin, cnt, hi, low):
	# Convert all inputs to floating point to make the calculations more exact.
	bin = [float(i) for i in bin]
	hi = float(hi)
	low = float(low)

	val = (bin[0]+1)/2 * (hi - low) + low

	return val

#BITS = 4
#HIGH = 32
#LOW  = 0

#print "\ncont2bin()"
#cont = []
#for i in range(2 ** BITS):
#	num = 2*i
#	cont.append( cont2bin( num, BITS, HIGH, LOW ) )
#	print num, cont[i]

#print "\nbin2cont()"
#bin = []
#for i in range(2 ** BITS):
#	bin.append( bin2cont(cont[i], BITS, HIGH, LOW) )
#	print i, bin[i]
