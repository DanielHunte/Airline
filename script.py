# Read in the file
with open('airline.py', 'r') as file :
  filedata = file.read()

# Replace the target string
filedata = filedata.replace('    ', '	')

# Write the file out again
with open('airline.py', 'w') as file:
  file.write(filedata)