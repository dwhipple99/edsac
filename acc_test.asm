# This is a comment
# I created this file to show a very simple accumulator test
#
# For this example, start the simulator
#
#   issue the command "acc" to show the state of the accumulator, it should be all 0's
#   issue the command "testacc" to set the accumulator to all 1's
#   issue the command "acc" to show the state of the accumulator, it should be all 1's
#   issue the command "load acc_test.asm", this loads this test program
#   issue the command "start" to execute this program, the command TF will zero out the accumulator
#   issue the command "acc" to show the state of the accumulator, it should be all 0's
#
#00101 - 31
T35F
#00101 - 33
TF 
#01101 - 32
ZF
