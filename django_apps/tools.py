from datetime import datetime
from algo.models import History

class diff:
    def __init__(self,avg_user,avg_clock,minn,maxn,count,total):
        self.avg_user = avg_user
        self.avg_clock = avg_clock
        self.minn = minn
        self.maxn = maxn
        self.count = count
        self.total = total

def fix_diffs(current, reference):
    yo_diff = diff(current.avg_user-reference.avg_user, current.avg_clock-reference.avg_clock, \
         current.minn-reference.minn, current.maxn-reference.maxn, \
         current.count-reference.count, current.total-reference.total)    

    return yo_diff

def fix_history(current, reference, diffs):
    history_table = '<H2>'+current.alg+' vs '+reference.alg+ '  ('+str(datetime.now())+') ' '</H2>' + \
    '<TABLE>' + \
    '<TR><TD></TD>' + \
    '<TD><div class=firstcell>Current</div></TD>' + \
    '<TD><div class=firstcell style=background-color:red>Reference</div></TD>' + \
    '<TD>Difference</TD></TR>' + \
    '<TR><TD>Algorithm</TD><TD>'+str(current.alg)+'</TD><TD>'+str(reference.alg)+'</TD><TD></TD></TR>' + \
    '<TR><TD>Avg_user</TD><TD>'+str(current.avg_user)+'</TD><TD>'+str(reference.avg_user)+'</TD><TD>'+str(diffs.avg_user)+'</TD></TR>' + \
    '<TR><TD>Avg_clock</TD><TD>'+str(current.avg_clock)+'</TD><TD>'+str(reference.avg_clock)+'</TD><TD>'+str(diffs.avg_clock)+'</TD></TR>' + \
    '<TR><TD>Min</TD><TD>'+str(current.minn)+'</TD><TD>'+str(reference.minn)+'</TD><TD>'+str(diffs.minn)+'</TD></TR>' + \
    '<TR><TD>Max</TD><TD>'+str(current.maxn)+'</TD><TD>'+str(reference.maxn)+'</TD><TD>'+str(diffs.maxn)+'</TD></TR>' + \
    '<TR><TD>Count</TD><TD>'+str(current.count)+'</TD><TD>'+str(reference.count)+'</TD><TD>'+str(diffs.count)+'</TD></TR>' + \
    '<TR><TD>Total</TD><TD>'+str(current.total)+'</TD><TD>'+str(reference.total) +'</TD><TD>'+str(diffs.total)+'</TD></TR>' + \
    '</TABLE>'
    
    return history_table
    
def generate_history():
    html_page = '<HTML>' + \
        '<link rel="stylesheet" href="http://lhcb-release-area.web.cern.ch/LHCb-release-area/DOC/css/lhcb.css" type="text/css" media="screen">' + \
        '<link rel="stylesheet" href="http://lhcb-release-area.web.cern.ch/LHCb-release-area/DOC/gauss/css/css.css" type="text/css" media="screen">' + \
        '<link rel="stylesheet" href="css.css" type="text/css" media="screen">' + \
        '<title>Algorithm comparing</title></HEAD><BODY><div class="ctitle"><TABLE id="pagetitle">' + \
        '<TBODY><TR><TD class=iconspace><A href="http://cern.ch/lhcb-comp">' + \
        '<IMG id=lhcblogo  src="http://lhcb-release-area.web.cern.ch/LHCb-release-area/DOC/images/lhcbcomputinglogo.gif" >' + \
        '</A></TD><TD vAlign=middle align=center><H1><a href="/algos" >Algorithms testing comparison</a></H1></TD>' + \
        '</TR></TBODY></TABLE></div><div class=pagebody><div id=manifest><p>The story of comparisons so far</p></div>' + \
        '<H2><a href="/algos" >Home</a></H2>'
    
    history = History.objects.all()
    for hist in history:
        html_page += hist.body

    
    html_page += '</BODY></HTML>'
    
    return html_page