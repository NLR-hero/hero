cd ../../../; source env.sh; cd tests/scaling/01_rds/

mpirun --oversubscribe -np 1 python test.py
mpirun --oversubscribe -np 2 python test.py
mpirun --oversubscribe -np 4 python test.py
mpirun --oversubscribe -np 8 python test.py
mpirun --oversubscribe -np 16 python test.py
mpirun --oversubscribe -np 32 python test.py
mpirun --oversubscribe -np 64 python test.py
mpirun --oversubscribe -np 128 python test.py
mpirun --oversubscribe -np 256 python test.py
mpirun --oversubscribe -np 512 python test.py
mpirun --oversubscribe -np 1024 python test.py
mpirun --oversubscribe -np 2048 python test.py