import re
pattern11 = r".*?\(([A-Za*--z\_\d\.]+)\)\s*\:\s*[\(\[\{\<]?([A-Za-z\_\d\.\-\>]+)[\)\]\}\>]?$"
print("appending...")
prefix = "#"
import sys


if len(sys.argv) != 2:
        print(f"用法: {sys.argv[0]} <file> ")
        sys.exit(1)

file = sys.argv[1]

print(f"iter_count: {file}")

t='''
CONFIG_PERF_EVENTS=y
CONFIG_HW_PERF_EVENTS=y
CONFIG_TRACING=y
CONFIG_FTRACE=y
CONFIG_KPROBES=y
CONFIG_HAVE_PERF_EVENTS=y
CONFIG_PROFILING=y
'''
#boot=set(['EFI']) #disable CONFIG_EFI  an example

boot=set([])


with open('output.txt', 'r') as input_file:
          with open(f'./files/{file}', 'a') as output_file:
                     output_file.write('#///////////////////////////////\n')
                    
                     for line in input_file:
                                          if line.startswith(prefix):
                                                  continue

                                          mat_t=re.findall(pattern11, line)
                                          print(line)
                                          print(mat_t)
                                          mat_t = mat_t[0]
                                          if  mat_t[1]=='on' or mat_t[1]=='-->':
                                               n = 'CONFIG_'+mat_t[0]+'=y\n' 
                                          elif mat_t[1]=='off': 
                                               n = 'CONFIG_'+mat_t[0]+'=n\n' 
                                          
                                          else:
                                               n = 'CONFIG_'+mat_t[0]+'='+mat_t[1] + '\n'        
                                          if mat_t[0] in boot:
                                               n="#"+n
                                          output_file.write(n)
                     output_file.write(t)
input_file.close()
output_file.close()

