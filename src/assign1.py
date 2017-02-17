import argparse
from tachyon import *
from hpcc import *

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Performance Analyzer Script')
	parser.add_argument('-benchmark', help='Selecting Benchmark to analyze performance - tachyon or hpcc', type=str, required=True)
	parser.add_argument('-sched', help='Select the scheduler to perform scheduling - byslot or bynode', type=str, required=True)

	args = parser.parse_args()
	bm_to_run = args.benchmark
	scheduler = args.sched
		
	if bm_to_run not in ['tachyon', 'hpcc']:
		print('Error: Invalid Benchmark: {}. Required: tachyon or hpcc'.format(bm_to_run))
		exit(0)

	if scheduler not in ['byslot', 'bynode']:
		print('Error: Invalid Scheduler: {}. Required: byslot or bynode '.format(scheduler))
		exit(0)

	os.system('rm -rf hosts')

	if bm_to_run == 'tachyon':
		run_tachyon_bm(scheduler)
	else:
		run_hpcc_bm(scheduler)

	os.system('rm -rf hosts')


