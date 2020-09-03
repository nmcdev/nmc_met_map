import numpy as np
import matplotlib as mpl
from nmc_met_graphics.cmap.cm import make_cmap
import nmc_met_graphics.cmap.cm as cm_collected


import nmc_met_map.lib.utility as utl
utl.filename_day_back_model(day_back=0.5,fhour=0,UTC=False)

a = [5,10,15,20,25,30,35,40,50,60,70,80,90]

# Normalize the bin between 0 and 1 (uneven bins are important here)
norm = [(float(i)-min(a))/(max(a)-min(a)) for i in a]

# Color tuple for every bin
C = np.array(
    [[145,0,34], [166,17,34], [189,46,36], [212,78,51], [227,109,66], 
    [250,143,67], [252,173,88], [254,216,132], [255,242,170], 
    [230,244,157], [188,227,120], [113,181,92], [38,145,75], [0,87,46]])

# Create a tuple for every color indicating the normalized 
# position on the colormap and the assigned color.
COLORS = []
for i, n in enumerate(norm):
    COLORS.append((n, np.array(C[i])/255.))

# Create the colormap
cmap = mpl.colors.LinearSegmentedColormap.from_list("rh", COLORS)