import math
import os
from matplotlib import pyplot as plt

__rm_size = 4 * (1024 ** 3)
__hpl_perf = []
__ptrans_perf = []


def __calculate_N(cs):
	n = math.sqrt(((__rm_size * cs) / 8)) * 0.9
	print('Calculated N values for 4GB RAM: {}'.format(n))
	return n


def __change_txt(txt, val):
	fill_txt = [' ']*13
	val_str = str(val)
	val_len = len(val_str)
	val_lt = list(val_str)
	fl = val_lt+ fill_txt[val_len:]+ txt[13:]
	txt.clear()
	txt.extend(fl)


def __manipulate_input_file_hpcc(cs, p, q, n, nb):
	print('Cluster Size {}:'.format(cs))
	print('-'*15)
	print()
		
	print('Optimizing N value to run the benchmark faster: [{}/{}] -> {} (Block Aligned)'.format(__calculate_N(cs), nb, n)) 
	
	ip_file = 'hpcc-1.4.3/hpccinf.txt'
	line_count, p_line, q_line = 0, 0, 0
	
	with open(ip_file, 'r') as f:
		text = f.readlines()
		
	for line in text:
		line_count += 1
		if 'Ps' in line:
			p_line = line_count
		elif 'Qs' in line:
			q_line = line_count
		elif ' Ns' in line:
			n_line = line_count
		elif '  NBs' in line:
			nb_line = line_count
		
	p_txt = list(text[p_line - 1])
	q_txt = list(text[q_line - 1])
	n_txt = list(text[n_line - 1])
	nb_txt = list(text[nb_line - 1])
	
	__change_txt(p_txt, p)
	__change_txt(q_txt, q)
	__change_txt(n_txt, n)
	__change_txt(nb_txt, nb)
	
	text[p_line - 1] = ''.join(p_txt) 
	text[q_line - 1] = ''.join(q_txt)
	text[n_line - 1] = ''.join(n_txt)
	text[nb_line - 1] = ''.join(nb_txt)
	
	os.system('rm -rf {}'.format(ip_file))		

	with open(ip_file, 'w') as w:
		w.writelines(text)


def __parse_hpl_ptrans_perf(txt, cs):
	gbs_total = 0.0
	count = 0

	for line in txt:
		if 'WR11C2R4' in line:
			hpl_perf = line.split()[-1]
			__hpl_perf.append(hpl_perf)
			print('HPL Performance for cluster size: {} is {} GFlops'.format(cs, hpl_perf))
		elif 'WALL' in line:
			count += 1
			gbs_total += float(line.split()[-2])

	ptrans_perf = gbs_total/count
	print('PTRANS Performance for cluster size: {} is {} GB/s'.format(cs, ptrans_perf))
	print()
	__ptrans_perf.append(ptrans_perf)


def __show_perf_graph(bm, sched):
	plt.figure(figsize=(8,6), dpi=80)
	plt.xlabel('Cluster Size')
	X = [i for i in range(1, 4)]

	if bm == 'ptrans':
		plt.ylabel('GB/s')
		plt.title('Performace of PTRANS benchmark on {} Schduler'.format(sched)) 
		plt.plot(X, __ptrans_perf)
		plt.show()
	elif bm == 'hpl':
		plt.ylabel('Gflops')
		plt.title('Performace of HPL benchmark on {} Schduler'.format(sched)) 
		plt.plot(X, __hpl_perf)
		plt.show()


def __get_node_list(size, txt):
	with open('hosts', 'w+') as f:
		f.write(txt[size -1])


def __run_hpcc_job_with_cluster(sched, cs, np, host_data):
	__get_node_list(cs, host_data)
	os.system('rm -rf hpcc-1.4.3/hpccoutf.txt')
	os.chdir('hpcc-1.4.3')
	cmd = 'mpirun -np {} -hostfile ../hosts -{} hpcc'.format(np, sched)
	print('Command: {}'.format(cmd))
	print()
	os.system(cmd)
	os.chdir('..')
	
	with open('hpcc-1.4.3/hpccoutf.txt', 'r') as f:
		txt = f.readlines()
	
	__parse_hpl_ptrans_perf(txt, cs)	


def run_hpcc_bm(sched):
	
	print()	
	print('Running HPCC Benchmark with {} scheduler'.format(sched))
	print("*"*44)
	print()

	with open('mpi_hosts', 'r') as f:
		txt = f.readlines()

	__manipulate_input_file_hpcc(1, 1, 1, 217, 96)
	__run_hpcc_job_with_cluster(sched, 1, 2, txt)	

	__manipulate_input_file_hpcc(2, 1, 2, 960, 96)
	__run_hpcc_job_with_cluster(sched, 2, 4, txt)

	__manipulate_input_file_hpcc(3, 1, 3, 1440, 96)
	__run_hpcc_job_with_cluster(sched, 3, 6, txt)

	__show_perf_graph('hpl', sched)
	__show_perf_graph('ptrans', sched)
	os.system('rm -rf hosts')

