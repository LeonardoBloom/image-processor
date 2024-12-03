import os

script_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_directory, 'mask', 'mask.jpg')

os.remove(file_path)