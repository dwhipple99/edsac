#!/usr/bin/env python
#
# Programmer - David Whipple
#
# Date - 03/15/2017
#
# This is an EDSAC simulator written for a graduate course @ Drexel - CS680 - Evolution of Computing
#
# This was one of if not the first Von Neumann architecture machine.
#
# Instructor Brian Stuart
#
#

from time import localtime
import os
import sys
import array
from bitutils import makeBitArray
from bitutils import testBit
from bitutils import setBit
from bitutils import clearBit
from tape import load_initial_orders

# Global Variables
version="0.1"

# This may not be the most eloguent way to simulate a machine, but I 
# like some of the attributes of it.  I've chosen to use objects to represent
# individual instances of a machine.  So to create a new instance of an EDSAC, 
# I just instantiante a new machine as an object.
#
# In theory, this will allow me to run several instances of EDSAC at the same time
# or ultimately, represent other machines with yet to be defined new object types, 
# using the same parser of course.
#
#

# The following class defines the EDSAC architecture
#
# Instruction format
# 
#  18 bit word length, but 1st bit is unusable
#              111111111
#     123456789012345678
#    **********************
#    *  5  |1|    10    |1*
#    **********************
#     op    sp  address length
#
#
# Opcode: The character code value for the letter representing the instruction.
#
# Address: Location of one of the 1024 words of memory.
# 
# Length: Whether the instruction operates on a short (F) or a long (D).
# 
# Typical instructions are A 43 F (Add the short at location 43 into the accumulator)
# and S 192 D (Subtract the long at 192 from the accumulator). Note that for address 
# zero the number is omitted, e.g. T F means store the short in the accumulator at location 0.
#
#  The following defines the instruction set of the EDSAC
#
#     A n  - Add the number in stroage location n into the accumulator
#     S n  - Subtract the number in storage location n from the accumulator
#     H n  - Copy the number in storage location n into the multuplier register
#     V n  - Multiply the number in storage location n by the number in the multipler register and add the product into the accumulator
#     N n  - Multiply the number in storage location n by the number in the multiplier register and subtract the product from the accumlator
#     T n  - Transfer the contents of the accumulator to storage location n and clear the accumulator
#     U n  - Transfer the contents of the accumulator to storage location n and do not clear the accumulator
#     C n  - Collate [logical and] the number in storage location n and do not clear the accumulator
#     R 2^(n-2) - Shift the number in the accumulator n places to the right
#     L 2^(n-2) - Shift the number in the accumulator n places to the left
#     E n  - If the sign of the accumulator is positive, jump to location n;, otherwise proceed serially
#     G n -  if the sign of the accumulator is negative, jump to location n;otherwise proceed serially
#     I n -  Read the next character from paper tape, and store it as the least signficant 5 bits of location n
#     O n -  Print the character represented by the most signficant 5 bits of storage location n
#     F n -  Read the last character output for verification 
#     X   -  NOP
#     Y   -  Round the number in the accumulator to 34 bits
#     Z   -  Stop the machine and ring the warning bell

class EDSAC():
   def __init__(self, name):
     self.name = name
     print "Creating new EDSAC machine with name", name,"\n"
     # This is only used to paginate during memory dumps
     self.pageSize = 24

     # define the memory of the machine
     #self.words = 512
     #self.wordSize = 35
     self.words = 1024
     self.wordOpcode = {}
     self.wordHasAddress = {}
     self.wordAddress = {}
     self.wordOperandType = {}
     self.wordSize = 17
     self.bits = self.words * self.wordSize + 1
     self.memory = makeBitArray(self.bits,0)
     self.programLoaded = False
     self.programCounter = 31
     self.executing = False
     self.stepMode = False
     self.debugMode = False

     # The Control and ALU (together make the CPU complex contain the following 5 registers)
     # Sequence Control Register, Order Tank, Accumulator, Multiplier, and Multiplicand

     # define the Order Tank
     self.otSize = 17
     self.ot = makeBitArray(self.otSize+1,0)

     # define the Sequence Control Register
     self.scrSize = 10
     self.scr = makeBitArray(self.scrSize+1,0)

     # define the accumulator
     self.accSize = 71
     self.acc = makeBitArray(self.accSize+1,0)

     # define the Multiplier
     self.multiplierSize = 35
     self.multiplier = makeBitArray(self.multiplierSize+1,0)

     # define the Multiplicand
     self.multiplicandSize = 35
     self.multiplicand = makeBitArray(self.multiplicandSize+1,0)
 
     # If you look at this history of the machine the Initial Orders (a mini boot OS) came in May, 1949  as Version 1
     #
     # This function loads exactly those initial orders as they were hardwired into memory locations 0 to 30, execution starts @ location 31
     load_initial_orders(self)


# This function starts the command line interface.
#
def cli(object):
   # This is the command line parser, it accepts an EDSAC machine as a 
   # machine to execute commands on.

   prompt="("+object.name+")->"

   updatedSCR = str(bin(object.programCounter)[2:].zfill(10))

   for bit in range(0, (object.scrSize)):
      if (updatedSCR[bit] == '1'):
          # print "Setting bit", bit, "to 1"
          setBit(object.scr, bit)
      else:
          clearBit(object.scr, bit)
          # print "Setting bit", bit, "to 0"
      # scr()

#  The following character codes are used
#  This is prior to ASCII or UNICODE being defined, so they defined their own charcater coding.
#
   io = {
         'P':'00000',
         'Q':'00001',
         'W':'00010',
         'E':'00011',
         'R':'00100',
         'T':'00101',
         'Y':'00110',
         'U':'00111',
         'I':'01000',
         'O':'01001',
         'J':'01010',
         'Pi':'01011',
         'S':'01100',
         'Z':'01101',
         'K':'01110',
         'Erase(1)':'01111',
         'BT(2)':'10000',
         'F':'10001',
         'Theta':'10010',
         'D':'10011',
         'Phi':'10100',
         'H':'10101',
         'N':'10110',
         'M':'10111',
         'Delta':'11000',
         'L':'11001',
         'X':'11010',
         'G':'11011',
         'A':'11100',
         'B':'11101',
         'C':'11110',
         'V':'11111' }

   opcodes = {
       'A': '11100',  # Add
       'D': '10011',  #
       'E': '00011',  # Conditional branch
       'G': '11011',  # Conditional branch
       'H': '10101',  # Copy
       'I': '01000',  # Read
       'L': '11001',  # Shift
       'R': '00100',  # Shift
       'S': '01100',  # Subtract
       'T': '00101',  # Store
       'Z': '01101',  # Stop and ring bell
       'O': '01001',  # Output (print)
       'U': '00111',  # Store
       'P': '00000',  #
       '*': '01111',  # (erase)
       '!': '10100',  # (phi)
       'W': '00010',  # (phi)
       '&': '11000',  # Delta
       'V': '11111'}  # Multiply

   inv_opcodes = {}

   for k, v in opcodes.iteritems():
       inv_opcodes[v] = inv_opcodes.get(v, [])
       inv_opcodes[v].append(k)

   # TODO - Need to double check all items in menu work.

# These are the commands supported by the CLI.
#
   commands = {
            'create':'This command creates a new EDSAC machine object.',
            'clear':'This command clears the screen.',
            'restart':'This command reinitializes the current machine.',
            'reset':'This command simulates pressing the reset button on the machine.',
            'registers':'This command displays the current register values.',
            '(m)emory':'This command displays the current contents of memory',
            '(s)tep':'This command enters single step mode, issue reset to leave step mode.',
            'start':'This command simulates pressing the start button on the machine.',
            'debug':'Toggle DEBUG mode for more verbose or less verbose output',
            '(a)cc':'This command displays the accumulator.',
            'scr':'This command displays the sequence control register.',
            'ot':'This command displays the order tank register.',
            'multiplier':'This command displays the multiplier register.',
            'multiplicand':'This command displays the multiplicand register.',
            '(l)oad':'This command loads a program from paper tape (simulated in from a file).',
            '(d)ump':'This command dumps the entire machine state.',
            'setbit':'This command sets a bit of memory to 1.',
            'list':'This command lists the assembler code loaded.',
            'clearbit':'This command sets a bit of memory to 0.',
            '(h)elp':'This command prints this list of help.',
            'testacc': 'Set acc to all 1\'s for testing',
            '(e)xit':'This command exits the CLI.'}

# This prints the menu
#
   def print_welcome():
      time_now=localtime()
      hour=time_now.tm_hour
      minute=time_now.tm_min
      second=time_now.tm_sec
      print "Welcome to the EDSAC simulator!"
      print "Version",version,", start time is ",hour,":",minute,":",second
      print "\nEntering the CLI for ", object.name," simulator."
      print "Machine memory, total words=",object.words,", word size=",object.wordSize
      print "                total bits=",(object.bits-1),", starting at 0 and ending at ",(object.bits-2)
      print "\nThe commands available are:\n"
      for command, command_help in commands.items():
          print "{0:12} - {1}".format(command, command_help)
      print "\n"


# This resets the entire simulator
#
   def reset():
      machineName = object.name
      i = raw_input("Press enter to simulate pressing reset button on machine.")
      os.system('clear')
      newMachine=EDSAC(machineName)
      cli(newMachine)

# This restarts the simulator, creating a duplicate version of the EDSAC currently running, but reinitialized
#
   def restart():
      machineName = object.name
      i = raw_input("Press enter to restart EDSAC with freshly initialized machine and current machine name...")
      os.system('clear')
      newMachine=EDSAC(machineName)
      cli(newMachine)
       
# This prints the menu/help
#
   def help():
      print_welcome()

# This exits the simulator
   def exit():
      sys.exit("Goodbye!")

# This sets a bit in memory, used for debugging.
   def setbit():
      print "Memory starts at location 0 and ends at location",object.bits-1
      bitToSet = raw_input("Please enter the bit location to set to 1 ->")
      if (bitToSet == ""):
         do_nothing()
         return
      setBit(object.memory,int(bitToSet))

# This clears a bit in memory, used for debugging.
   def clearbit():
      print "Memory starts at location 0 and ends at location",object.bits-1
      bitToSet = raw_input("Please enter the bit location to set to 0 ->")
      if (bitToSet == ""):
         do_nothing()
         return
      clearBit(object.memory,int(bitToSet))

# This prints the contents of the order tank
   def ot():
      print "Printing value of order tank register (starting bit 0, ending bit 16):"
      print "Order Tank Register:",
      for bit in range(0,(object.otSize)):
          print "{0:1}".format(testBit(object.ot,bit)),
      print "\n"

# This prints the contents of the multiplier
   def multiplier():
      print "Printing value of multiplier register (starting bit 0, ending bit 34):"
      print "Multiplier Register:",
      for bit in range(0,(object.multiplierSize)):
          print "{0:1}".format(testBit(object.multiplier,bit)),
      print "\n"

# This prints the contents of the multiplicand
   def multiplicand():
      print "Printing value of multiplicand register (starting bit 0, ending bit 34):"
      print "Multiplicand Register:",
      for bit in range(0,(object.multiplicandSize)):
          print "{0:1}".format(testBit(object.multiplicand,bit)),
      print "\n"

# This prints the contents of the sequence control register
   def scr():
      print "Printing value of sequence control register (starting bit 0, ending bit 9):"
      print "Sequence Control Register:",
      for bit in range(0,(object.scrSize)):
          print "{0:1}".format(testBit(object.scr,bit)),
      print "\n"

# This prints the contents of the accumulator
   def acc():
      print "Printing value of accumulator (starting bit 0, ending bit 70):"
      print "Accumulator:",
      for bit in range(0,(object.accSize)):
          print "{0:1}".format(testBit(object.acc,bit)),
      print "\n"

# This clears the screen
   def clear():
      os.system('clear')

# This prints the contents of the registers and memory
   def dump():
       registers()
       memory()

# This prints the contents of all registers
   def registers():
      acc()
      scr()
      ot()
      multiplier()
      multiplicand()

# This creates an instantiantion of an EDSAC object.
   def create():
      c2 = raw_input("Please enter a name for your EDSAC->")
      newEdsac = EDSAC(c2)
      cli(newEdsac)

# This prints the contents of memory.
   def memory():
      print "Dumping contents of memory:"
      print "---------------------------"
      print "Total words in memory is ", object.words
      print "Word size is ", object.wordSize
      print "Total bits in memory is ", object.bits-1
      currentWord=0
      for bit in range(0,(object.bits-1)):
          if (bit != 0):
             if (((bit+1) % object.wordSize) == 0):
                print "{0:1}".format(testBit(object.memory,bit))
                currentWord = currentWord + 1
                # used to paginate
                if ((currentWord % object.pageSize) == 0):
                   i = raw_input("Press enter to continue or \"q\" to quit -> ")
                   if (i == 'q'):
                      break;
                if (currentWord != object.words):
                   print "Word ({0})-".format(currentWord),
             else:
                print "{0:1}".format(testBit(object.memory,bit)),
          else:
              print "Word ({0})-".format(currentWord),
              print "{0:1}".format(testBit(object.memory,bit)),
      print "\n"


      #print(object.bits, len(object.memory), (len(object.memory) * object.wordSize) - object.bits, bin(object.memory[0]))
 
# A stupid helper function, that should be done away with
   def myIsDigit(s):
      if (s=='0' or s=='1' or s=='2' or s=='3' or s=='4' or s=='5' or s=='6' or s=='7' or s=='8' or s=='9'):
         return True
      else: 
         return False 

# This decodes the address (10 bits) and the operand (1 character)
   def decode_address_and_operand_type(line):
       #print "Decoding address"

       i = 1
       address = 0
       while (myIsDigit(line[i])):
          #print "i=", i, "Line[i]=",line[i]
          address = 10*address + int(line[i])
          i = i + 1
       operandType = line[i]
       return (address, operandType)


# This implements the T command (opcode)
   def execute_T():
      if (object.debugMode):
          print "Executing T order, program counter is ", object.programCounter
      if (object.programCounter == 31):
          if (object.debugMode):
             print "First instruction, marking the beginning"
      else:
          #print "In T order, not first"
          if (object.wordHasAddress[object.programCounter] == True):
             #print "Transferring accumulator to memory location", object.wordAddress[object.programCounter]
             #print "Zeroing accumulator.."
             for bit in range(0, (object.accSize)):
                 clearBit(object.acc, bit)
          else:
             #print "Zeroing accumulator.."
             for bit in range(0, (object.accSize)):
                 clearBit(object.acc, bit)

# This gets the address value in a memory address
   def getAddressValue(address):
       valueList = []
       if (object.debugMode):
          print "Getting value at address", address
       bitNumber = (address * object.wordSize) + 6
       #print "BitNumber=", bitNumber
       for bit in range(bitNumber, bitNumber+10):
           if (testBit(object.memory, bit) == 1):
               valueList.append('1')
           else:
               valueList.append('0')
       # print "Value list = ", valueList
       valueStr = ''.join(valueList)
       value = int(valueStr, 2)
       #print "Value=", value
       return value
       #for bit in range(bitNumber, (object.wordSize)):
       #    accStr = str(bit)
       #print "accumlator string = ", accStr

# This gets the Order value (first 5 bits) in an address
   def getOrderValue(address):
       valueList = []
       #print "Getting order value at address", address
       bitNumber = (address * object.wordSize)
       #print "BitNumber=", bitNumber
       for bit in range(bitNumber, bitNumber+5):
           if (testBit(object.memory, bit) == 1):
               valueList.append('1')
           else:
               valueList.append('0')
       #print "Value list = ", valueList
       valueStr = ''.join(valueList)
       #print "Value String is ", valueStr
       #value = int(valueStr, 2)
       #print "Value=", value
       return valueStr

# This gets the current accumulator value
   def getAccValue():
       accList = []

       for bit in range(0, (object.accSize)):
           if (testBit(object.acc, bit) == 1):
               accList.append('1')
           else:
               accList.append('0')
       #print "accumlator list = ", accList
       accStr = ''.join(accList)
       accInt = int(accStr,2)
       #print "acc=", accInt
       return accInt

# This adds a value to the accumulator
   def addValueToAccumulator(value):
       #value = getAddressValue(address)
       binaryValue = str(bin(value)[2:].zfill(70))
       accumulator = getAccValue()
       newAcc = accumulator + value
       #print "New acc will be", newAcc
       newBinaryAcc = str(bin(newAcc)[2:].zfill(70))
       #print "Size of newBinaryAcc", len(newBinaryAcc)
       #print "Adding Value at address ", value, "to accumulator, accumulator is ", accumulator, "value is ", value
       #print "New binary value is ", newBinaryAcc
       for bit in range(0, (object.accSize-1)):
          if (newBinaryAcc[bit] == '1'):
              setBit(object.acc, bit+1)
              #print "setting Bit to 1 = ", bit
          else:
              clearBit(object.acc, bit+1)
              #print "setting Bit to 0 = ", bit
       newValue = getAccValue()
       #print "New accumulator value is ", newValue
       return

# This implements the S command (opcode)
   def execute_S():
       if (object.debugMode):
          print 'Executing order S'
   #     TODO - Need to implement order S

# This implements the G command (opcode)
   def execute_G():
       if (object.debugMode):
          print "Executing order G"
       if (testBit(object.acc,0) == 0):
           accNegative = False
           #print "Accumulator is Positive"
       else:
           accNegative = True
           #print "Accumulator is Negative"
       if (accNegative == False):
           jumpAddress = object.wordAddress[object.programCounter]
           if (object.debugMode):
              print "Jumping to address", jumpAddress
           object.programCounter = jumpAddress-1
           updatedSCR = str(bin(object.programCounter)[2:].zfill(10))
           copyPCtoSCR(updatedSCR)
       else:
           if (object.debugMode):
              print "Not Jumping, Accumulator is Negative"
       if (object.debugMode):
          print "New program counter is ", object.programCounter
       return

# This implements the U command (opcode)
   def execute_U():
       accValue = getAccValue()
       #writeAddress = address = object.wordAddress[object.programCounter]
       writeAddress = object.wordAddress[object.programCounter]
       writeBit = writeAddress * object.wordSize + 6
       object.wordAddress[writeAddress] = accValue
       if (object.debugMode):
          print "Executing U order, acc is ", accValue, "writeBit is ", writeBit
       binaryValue = str(bin(accValue)[2:].zfill(10))
       #print "New binary value for address", writeAddress," is", binaryValue
       for bit in range(0, (10)):
           if (binaryValue[bit] == '1'):
               setBit(object.memory, writeBit)
               # print "setting Bit to 1 = ", bit
           else:
               clearBit(object.memory, writeBit)
               # print "setting Bit to 0 = ", bit
           writeBit = writeBit + 1
       #object.wordAddress[]
       return

# This implements the A command (opcode)
   def execute_A():
       if (object.debugMode):
          print "Executing A order."
       if (object.wordHasAddress[object.programCounter] == True):
           value = getAddressValue(object.wordAddress[object.programCounter])
           addValueToAccumulator(value)
       return

# This implements the O command (opcode)
   def execute_O():
       if (object.debugMode):
          print "Executing O order, program counter is", object.programCounter
       if (object.wordHasAddress[object.programCounter] == True):
           #address = object.wordAddress[object.programCounter]
           orderValue = getOrderValue(object.wordAddress[object.programCounter])
           #myOpCode = get_opcode(address)
           #print "Order Value is ", orderValue
           ch = inv_opcodes[orderValue]
           #print "{0:1}".format(testBit(object.ot, bit)),
           print "{0}".format(ch[0].rstrip())
           # TODO - This is a poors man's exit, once the S command is implemented, this can be deleted.
           if (ch[0] == "&"):
               print "Hit location 56"
               print "This machine has a limited implementation of the EDSAC instruction set."
               print "It was implemented to demonstrate the original \"Hello!World\" program written for EDSAC."
               print "Therefore, we will reset the machine at this point."
               x = raw_input("Press enter to reset machine...")
               reset()
       return

# This implements the Z command (opcode)
   def execute_Z():
       if (object.debugMode):
          print "Executing Z order."
       print "beep.beep.beep."
       ##os.system("beep -f 555 -l 460")
       print "Stopping machine, until reset button is pressed (enter reset)."
       object.executing = False

# This decodes the opcode (first 5 bits of insruction)
   def decode_opcode(line):

       opcodeLetter = line[0]
       opcode = opcodes[opcodeLetter]
       #print "Opcode found for letter", opcodeLetter, ", it is ", opcode
       return opcode

# This loads a tape (file) into memory
   def load():

      #  TODO - Need to copy the rest of the word into memory (including address and operand type)
      startWord = 31
      currentWord = startWord
      currentBit = startWord * object.wordSize
      print "This command will load a program starting at word,",startWord,", which is bit",currentBit,"."
      filename = raw_input("Enter filename containing tape ->")
      try:
          file=open(filename, "r")
      except IOError:
          print "<ERROR>: File not found\n"
          return
      for line in file:
         print line,
         if line[0] != "#":
            object.wordOpcode[currentWord]=line[0]
            opcode = decode_opcode(line)
            #print "Loading ", opcode, " at word ", currentWord, "and bit ", currentBit
            if myIsDigit(line[1]):
               strAddress, operandType = decode_address_and_operand_type(line)
               address = int(strAddress)
               object.wordOperandType[currentWord] = operandType
               binaryAddress = str(bin(address)[2:].zfill(10))
               print "Address is ", address, ", binary address is ", binaryAddress
               object.wordHasAddress[currentWord] = True
               object.wordAddress[currentWord] = address
            else:
               object.wordHasAddress[currentWord] = False
               # If the address is missing, then the documentations states it is assumed 0
               address = 0
               binaryAddress = str(bin(address)[2:].zfill(10))
               #print "No address"
               object.wordOperandType[currentWord] = line[1]
            for bit in opcode:
                if (bit == '1'):
                   setBit(object.memory, currentBit)
                else:
                   clearBit(object.memory,currentBit)
                currentBit = currentBit + 1
            setBit(object.memory, currentBit) # Added to set the Spare bit to 1 - always
            currentBit = currentBit + 1 # Added for the Spare bit between OPCODE and Address in Order
            for bit in binaryAddress:
                if (bit == '1'):
                    setBit(object.memory, currentBit)
                else:
                    clearBit(object.memory, currentBit)
                currentBit = currentBit + 1
            # This sets the last bit of the Order to 1 for operand Type of D, and 0 for operand type of F
            if (operandType == "D"):
                setBit(object.memory, currentBit)
            else:
                clearBit(object.memory, currentBit)
            #junk = raw_input("Press enter to continue...")
            currentWord = currentWord + 1
            currentBit = currentWord * object.wordSize
         #else:
            #print "Comment, skipping."
      object.programLoaded = True

        
# This allows you to list the program loaded
   def list():
       if (object.programLoaded == True):
          print "Listing assembler program..."
          for address in sorted(object.wordOpcode.iterkeys()):
             print "Address %s has opcode %s, operand type %s" % (address, object.wordOpcode[address], object.wordOperandType[address]),
             if (object.wordHasAddress[address] == True):
                print "and it has address",
                print object.wordAddress[address]
             else:
                print ", no address"
          x = raw_input("program loaded, press enter to continue...")
       else:
          x = raw_input("No program loaded, press enter to continue...")

   def get_opcode(word):
       startBit = word * object.wordSize
       opcode = str(testBit(object.memory,startBit)) + str(testBit(object.memory,startBit+1)) + str(testBit(object.memory,startBit+2)) + str(testBit(object.memory,startBit+3))+str(testBit(object.memory,startBit+4))
       #print "Opcode = ", opcode
       #x = raw_input("Press enter:")
       return opcode

# This copies the current instruction to the order tank
   def copyInstructiontoOT(address):
       # type: (object) -> object
       #print "Copying address ", address, "to order tank."
       bitNumber = address * object.wordSize
       otBit = 0
       for bit in range(bitNumber, (object.otSize+bitNumber)):
           if (testBit(object.memory, bit) == 1):
               setBit(object.ot, otBit)
           else:
               clearBit(object.ot, otBit)
           otBit = otBit + 1

# This copies the program counter to the sequence control registers (which was the program counter in the actual EDSAC)
   def copyPCtoSCR(updatedSCR):
       # print "Copying ", updatedSCR, "to SCR"
       for bit in range(0, (object.scrSize)):
           if (updatedSCR[bit] == '1'):
               # print "Setting bit", bit, "to 1"
               setBit(object.scr, bit)
           else:
               clearBit(object.scr, bit)
               # print "Setting bit", bit, "to 0"
               # scr()

# This enables step mode in the simulator so that you can execute one instruction at a time
   def step():
       if object.programLoaded == False:
          print "No program loaded."
          return
       object.stepMode = True
       start()

# This starts the current loaded program running
   def start():

      if object.programLoaded == False:
         print "No program loaded."
         return

      object.executing = True

      if (object.stepMode == True):
          print "In step mode.."

      print "Starting execution at word ", object.programCounter

      opcodeExecution = {
          '00111': execute_U,
          '01100': execute_S,
          '11011': execute_G,
          '01101': execute_Z,
          '00101': execute_T,
          '01001': execute_O,
          '11100': execute_A
      }

      while (object.executing == True):

         copyInstructiontoOT(object.programCounter)
         opcode = get_opcode(object.programCounter)
         updatedSCR = str(bin(object.programCounter)[2:].zfill(10))
         copyPCtoSCR(updatedSCR)
         #print "Executing at ", updatedSCR

         try:
            opcodeExecution[opcode]()
            object.programCounter = object.programCounter+1
         except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
         except ValueError:
             print "Value error."
         except:
             print "Unexpected error:", sys.exc_info()[0]
             raise
             exit()

         if (object.stepMode == True):
             return

# debugging command used to set the accumulator to all 1's
   def testacc():
       for bit in range(0, (object.accSize)):
           setBit(object.acc,bit)


# This toggles debug mode for more verbose output
   def debug():
       if (object.debugMode == True):
           print "Turning debug mode off."
           object.debugMode = False
       else:
           print "Turning debug mode on."
           object.debugMode = True


# Helper function for the CLI.
   def do_nothing():
      print "Doing nothing!"

# This is the menu for the CLI, actually this is a pattern in Python that
# uses a dictionary to issue a function call. So if you type the key, the key[index] is executed.
#
   options = { 
               'help':help,
               'h':help,
               'memory':memory,
               'm':memory,
               '?':help,
               'exit':exit,
               'e':exit,
               'q':exit,
               'clear':clear,
               'create':create,
               'setbit':setbit,
               'dump':dump,
                'd':dump,
               'load':load,
               'l':load,
               'registers':registers,
               'acc':acc,
               'a':acc,
               'scr':scr,
               'ot':ot,
               'multiplier':multiplier,
               'multiplicand':multiplicand,
               'clearbit':clearbit,
               'restart':restart,
               'reset':reset,
               'start':start,
               'list':list,
               'step':step,
               's':step,
               'debug':debug,
               'testacc':testacc,
               '':do_nothing,
             }

   print_welcome()

   while True:
     c1 = raw_input(prompt)
     #print "Command entered is ", c1
     # The following is the PYTHONIC way to do a case statement using a dictionary 
     try:
        options[c1]()
     except (NameError, KeyError):
        print "Sorry, command not yet implemented."

     
     #if c1 == 'help':
        #print_welcome()
     #elif c1 == 'exit':
        #print "Goodbye!"
        #break;
     #elif c1 == 'clear':
        #os.system('clear')
     #else
        #print "Command not yet implemented."

def main():
  os.system('clear')

  # Create the initial EDSAC object instantiation
  edsac1=EDSAC("edsac1")
  cli(edsac1)

main() 
