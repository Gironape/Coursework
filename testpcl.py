import pickle
import json

with open('save/save_file.pkl', 'rb') as f:
    data = pickle.load(f)
    print(data)
