#the same script extractStat in python instead of perl
import sys, re

column_names = ['EVENT_LOOP']
results = []


def add_column(name):
    if not name in column_names:
        sys.stderr.write('Adding column '+name+'\n') 
        column_names.append(name)

testnb = 0

for line in sys.stdin:
    exp = re.compile('TimingAuditor\.T\.\.\.\s+INFO\s+EVENT LOOP\s*\|\s*[\d\.]+\s+\|\s*([\d\.]+)\s+\|.*$')
    m = exp.search(line)
    if not m is None:
        testnb+=1
        ev = {}
        tmp = m.groups()[0]
        sys.stderr.write(str(testnb)+' Found event loop: '+tmp)
        ev['EVENT_LOOP'] = tmp
        mycontinue = 1
        colname = ""
        value = ""

        while(mycontinue > 0):
            for sl in sys.stdin:
                exp = re.compile('TimingAuditor\.T\.\.\.\s+INFO\s+(\w+)\s*\|\s*([\d\.]+)\s+\|\s*[\d\.]+\s+\|.*$')
                m = exp.search(sl)
                if not m is None:
                    colname = m.groups()[0]
                    value = m.groups()[1]
                    add_column(colname)
                    ev[colname] = value
                    if colname == 'Output':
                        mycontinue = 0
                        results.append(ev)
                        sys.stderr.write(str(testnb)+' EXIT\n')
        
for col in column_names:
    sys.stdout.write(col+',')

sys.stdout.write('\n')

for e in results:
    for col in column_names:
        sys.stdout.write(str(e[col])+',')  
    
    sys.stdout.write('\n')
