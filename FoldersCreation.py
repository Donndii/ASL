import os
import string

if not os.path.exists('Data'):
    os.makedirs('Data')

if not os.path.exists('Data/training'):
    os.makedirs('Data/training')

if not os.path.exists('Data/testing'):
    os.makedirs('Data/testing')

for i in string.ascii_uppercase:
    if not os.path.exists("Data/training/" + i):
        os.makedirs("Data/training/" + i)

    if not os.path.exists("Data/testing/" + i):
        os.makedirs("Data/testing/" + i)


