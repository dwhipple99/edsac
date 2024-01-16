#
# Programmer - David Whipple
# 
# These routines are used to simulate the tape reader.
# Tape's will be simulated with files.
#
# 
# I am simulating the first version of the Initial Orders 1 devised by David Wheeler
# Further work to simulate later versions should be done.
# 
# In the first version, the initial orders resided in memory locations 0 to 30,
# and a loaded program tape into locations 31 upwards.
#
#
# Order bit pattern Loc Order Meaning Comment
#
from bitutils import makeBitArray
from bitutils import testBit
from bitutils import setBit
from bitutils import clearBit

def load_initial_orders(object):
   initialOrders = {
#                         OP   
                     0:'00101 0 0000000000 0',
                     1:'10101 0 0000000010 0', 
                     2:'00101 0 0000000000 0',
                     3:'00011 0 0000000110 0',
                     4:'00000 0 0000000001 0',
                     5:'00000 0 0000000101 0',
                     6:'00101 0 0000000000 0',
                     7:'01000 0 0000000000 0',
                     8:'11100 0 0000000000 0',
                     9:'00100 0 0000010000 0',
                    10:'00101 0 0000000000 1',
                    11:'01000 0 0000000010 0',
                    12:'11100 0 0000000010 0',
                    13:'01100 0 0000000101 0',
                    14:'00011 0 0000010101 0',
                    15:'00101 0 0000000011 0',
                    16:'11111 0 0000000001 0',
                    17:'11001 0 0000001000 0',
                    18:'11100 0 0000000010 0',
                    19:'00101 0 0000000001 0',
                    20:'00011 0 0000001011 0',
                    21:'00100 0 0000000100 0',
                    22:'11100 0 0000000001 0',
                    23:'11001 0 0000000000 1',
                    24:'11100 0 0000000000 0',
                    25:'00101 0 0000011111 0',
                    26:'11100 0 0000011001 0', 
                    27:'11100 0 0000000100 0', 
                    28:'00111 0 0000011001 0',
                    29:'01100 0 0000011111 0',
                    30:'11011 0 0000000110 0' 
                   }
   print("Loading initial orders in locations 0 to 30.")

   memoryBitLocation = 0
   for orderNumber, order in initialOrders.items():
       #print("Adding order ", order," to memory location ", orderNumber)
       for bit in order:
          if (bit != " "):
             if (bit == "1"):
                #print("Setting ", memoryBitLocation," to 1")
                setBit(object.memory, memoryBitLocation)
             else:
                #print("Setting ", memoryBitLocation," to 0")
                clearBit(object.memory, memoryBitLocation)
#
             memoryBitLocation = memoryBitLocation + 1
             #i = raw_input("Press enter to continue.")

   return
