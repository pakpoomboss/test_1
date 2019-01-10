import os
import shutil
path = '/media/ubuntu/2236c044-00df-38be-2cd0-472d4e62f054/'

os.chdir(path)
files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)

oldest = files[0]
newest = files[-1]

print "Oldest:", oldest
print "Newest:", newest
print "All by modified oldest to newest:", files

#os.remove(newest)
shutil.rmtree(newest)

print "Oldest:", oldest
print "Newest:", newest
print "All by modified oldest to newest:", files
