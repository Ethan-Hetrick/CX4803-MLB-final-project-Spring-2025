import numpy as np
import matplotlib.pyplot as plt
import sys
import scipy
import os # Import os for path manipulation

input_ani_file = sys.argv[1]
input_af_file = sys.argv[2]

with open(input_ani_file, "r") as ani_file:
    
