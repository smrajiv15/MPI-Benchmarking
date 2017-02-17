import subprocess as sp
import os
from matplotlib import pyplot as plt

__tracing_time = {}
__cluster_keys = ['first', 'second', 'third']


def __get_render_time(cls_size, output):
	output = output.decode('utf-8')	
	output = output.rstrip('\r')
	time = 0
	
	for row in output.split('\n'):
		if 'Tracing Time' in row:
			_, time = row.split(':')
			break
	time = time.split()
	__tracing_time[cls_size] = time[0]


def __run_tachyon_job_with_cluster(np, sched, size, cls_size):
	exec_path = 'tachyon/compile/linux-mpi/tachyon'
	ip_file = 'tachyon/scenes/teapot.dat'
	
	print('Cluster Size {}:'.format(size))
	print('-'*15)
	print()

	cmd = 'mpirun -np {} -{} -hostfile hosts {} {}'. format(np, sched, exec_path, ip_file)
	print('Command: {}'.format(cmd))
	op = sp.check_output(cmd, shell=True)
	__get_render_time(cls_size, op)
	print("Tracing Time: {} Seconds.".format(__tracing_time[cls_size]))	
	print()


def __show_tachyon_performace_graph(sched):
	plt.figure(figsize=(8,6), dpi=80)
	plt.title('Performance on Tachyon Benchmark with {} Scheduler'.format(sched))
	plt.xlabel("Cluster Size")
	plt.ylabel("Time in Seconds")
	X = [i for i in range(1, 4)]
	Y = [i for i in [__tracing_time[j] for j in __cluster_keys]]
	plt.plot(X, Y)
	plt.show()


def __get_node_list(size, txt):
	with open('hosts', 'w+') as f:
		f.write(txt[size -1])


def run_tachyon_bm(sched):

	print()	
	print('Running Tachyon Benchmark with {} scheduler'.format(sched))
	print("*"*47)
	print()

	with open('mpi_hosts', 'r') as f:
		txt = f.readlines()

	__get_node_list(1, txt)
	__run_tachyon_job_with_cluster(2, sched, 1, 'first')

	__get_node_list(2, txt)				
	__run_tachyon_job_with_cluster(4, sched, 2, 'second')

	__get_node_list(3, txt)	
	__run_tachyon_job_with_cluster(6, sched, 3, 'third')
	
	__show_tachyon_performace_graph(sched)
	os.system('rm -rf hosts')

