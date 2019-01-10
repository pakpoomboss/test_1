import logging
import datetime
import time

counter = 1
path = '/home/ubuntu/Kub_Dee/Python2_7/04_temp/error_log/'

today = str(datetime.date.today())
timenow = time.ctime()
timenow = str(timenow[11:19])
date_time = today + ' ' + timenow
log_file= path + 'error_log_' + date_time + '.log'



while 1:
	raw_input('Press Enter to log...')

	logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', datefmt='%H:%M:%S')
	logging.warning('An example message. This is error number ' + str(counter) + '. \n\n\n')
	counter += 1

