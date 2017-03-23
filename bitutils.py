#
#  Programmer - David Whipple
# 
#  These were some general bit manipulation routines that I found basic versions of online and 
#  modified for my purposes of creating a simulator for the EDSAC.
#
#
#

import array

def makeBitArray(bitSize, fill = 0):
  intSize = bitSize >> 5                   # number of 32 bit integers
  if (bitSize & 31):                      # if bitSize != (32 * n) add
      intSize += 1                        #    a record for stragglers
  if fill == 1:
      fill = 4294967295                                 # all bits set
  else:
      fill = 0                                      # all bits cleared

  bitArray = array.array('I')          # 'I' = unsigned 32-bit integer

  bitArray.extend((fill,) * intSize)

  return(bitArray)

# testBit() returns a nonzero result, 2**offset, if the bit at 'bit_num' is set to 1.
def testBit(array_name, bit_num):
  # Added to correct offset - dwhipple
  bit_num = bit_num + 1
  # End
  record = bit_num >> 5
  offset = bit_num & 31
  mask = 1 << offset
  # This calculates actual bit value, for example, 2, 4, 8, 16, etc.
  value = array_name[record] & mask
  if (value > 0):
     value = 1
  return(value)

# setBit() returns an integer with the bit at 'bit_num' set to 1.
def setBit(array_name, bit_num):
  # Added to correct offset - dwhipple
  bit_num = bit_num + 1
  # End
  record = bit_num >> 5
  offset = bit_num & 31
  mask = 1 << offset
  array_name[record] |= mask
  return(array_name[record])

# clearBit() returns an integer with the bit at 'bit_num' cleared.
def clearBit(array_name, bit_num):
  # Added to correct offset - dwhipple
  bit_num = bit_num + 1
  # End
  record = bit_num >> 5
  offset = bit_num & 31
  mask = ~(1 << offset)
  array_name[record] &= mask
  return(array_name[record])

