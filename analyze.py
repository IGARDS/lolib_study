import pandas as pd
import numpy as np

import sys
from pathlib import Path
home = str(Path.home())

sys.path.insert(0,"%s/ranking_toolbox"%home)

import base
import pyrankability

if len(sys.argv) < 3:
    print("Usage: python analyze.py <group> <file>")
    exit(0)
    
group = sys.argv[1]
file = sys.argv[2]

data_dir = f'{home}/lolib_study/data/'
results_dir = f'{home}/lolib_study/RPLib/'

file_path = f'{data_dir}/{group}/{file}'
result_path = f'{results_dir}/{group}/{file}.json'

D = base.read_instance(file_path)

# Remove anything that has no information
sums1 = D.sum(axis=0)
sums2 = D.sum(axis=1)
mask = sums1 + sums2 != 2*np.diag(D)
D = D.loc[mask,mask]

# Solve using LP which should be fast
delta_lp,details_lp = pyrankability.rank.solve(D,method='lop',cont=True)

# Next round and then convert to a dictionary style that is passed to later functions
orig_sol_x = pyrankability.common.threshold_x(details_lp['x'])
# Fix any that can be rounded. This leaves Gurubi a much smaller set of parameters
fix_x = {}
rows,cols = np.where(orig_sol_x==0)
for i in range(len(rows)):
    fix_x[rows[i],cols[i]] = 0
rows,cols = np.where(orig_sol_x==1)
for i in range(len(rows)):
    fix_x[rows[i],cols[i]] = 1
    
#solutions = pd.DataFrame(columns=["cont","fix_x","delta","details"])

cont = False
delta,details = pyrankability.rank.solve(D,method='lop',fix_x=fix_x,cont=cont)
solution = pd.Series([cont,fix_x,delta,details],index=["cont","fix_x","delta","details"],name=0)

try:
    cont = False
    orig_sol_x = details['x']
    orig_obj = details['obj']
    other_delta,other_detail = pyrankability.search.solve_any_diff(D,orig_obj,orig_sol_x,method='lop')
    other_solution = pd.Series([cont,orig_obj,orig_sol_x,delta,details],index=["cont","orig_obj","orig_sol_x","delta","details"],name=1)
    print('Found multiple solutions for %s'%file_path)
except:
    print('Cannot find multiple solutions for %s (or another problem occured)'%file_path)

instance = base.LOLibInstance()
instance.D = D
instance.obj = orig_obj
instance.add_solution(solution['details']['P'][0])
instance.add_solution(other_solution['details']['P'][0])
#solutions = pd.concat([solution,other_solution],axis=1).T
#record = pd.Series({"group":group,"file":file,"D":D,"mask":mask,"method":"lop","solutions":solutions})

print('Writing to',result_path)
open(result_path,'w').write(instance.to_json())