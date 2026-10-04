"""Independent numeric checks against the state actually rendered by JavaScript."""
import json
import math
from pathlib import Path

B=Path(__file__).resolve().parent
actual=json.loads((B/'qa/math-rendered.json').read_text())
loss=lambda w,b: (2*w+b-5)**2/2
eps=1e-5
gw=(loss(1+eps,0)-loss(1-eps,0))/(2*eps)
gb=(loss(1,eps)-loss(1,-eps))/(2*eps)
assert math.isclose(actual['scalar']['gw'],gw,abs_tol=1e-8)
assert math.isclose(actual['scalar']['gb'],gb,abs_tol=1e-8)
assert actual['updated']['pred']==3.5 and actual['updated']['L']==1.125
assert math.isclose(loss(1.2,0),3.38) and loss(4.5,0)==8
f=lambda x:x*x+x
gradient=(f(2+eps)-f(2-eps))/(2*eps)
assert math.isclose(actual['branch']['gradient'],gradient,abs_tol=1e-8)
def many(w):return w[0]**2+2*w[1]+w[2]
mode_grad=[]
for i in range(3):
    plus=[1.,1.,1.];minus=plus.copy();plus[i]+=eps;minus[i]-=eps
    mode_grad.append((many(plus)-many(minus))/(2*eps))
assert all(math.isclose(a,b,abs_tol=1e-8) for a,b in zip(mode_grad,actual['mode']['gradient']))
assert actual['chain']['values']==[2,4,5,25,5]
# Work through the displayed matrix entry by entry, independent of the JS reducer.
v=[2*1+1*2,1*1-3*2];a=[max(v[0],0),max(v[1],0)]
assert actual['selective']['v']==v and actual['selective']['a']==a
assert actual['selective']['L']==a[0]**2+a[1]**2==16
assert actual['selective']['ga']==[8,0]
assert math.isclose(actual['compression']['maxError'],.0034,abs_tol=1e-12)
states=json.loads((B/'qa/step-states.json').read_text())
ends={(s['scene'],s['step']):s for s in states if s['position']=='end'}
assert ends['s02','loss']['models']['values']['L']==4.5
assert ends['s05','residual']['models']['gradients']['r']==-3
assert ends['s06','prediction']['models']['gradients']['pred']==-3
assert ends['s06','bias']['models']['gradients']['b']==-3
assert ends['s06','weight']['models']['gradients']['w']==-6
assert ends['s08','square']['models']['contributions']==[4,0]
assert ends['s08','sum']['models']['gradient']==5
assert ends['s11','accumulate']['models']['buffer']==-12
assert ends['s11','clear']['models']['buffer']==-6
assert ends['s11','scale']['models']['buffer']==-6
assert ends['s13','checkpoint']['models']['saved']==1
assert ends['s13','recompute']['models']['recomputed']==5
assert ends['s14','compiler']['models']['recomputed']==[4,0]
report=dict(status='passed',independent_method='central finite differences and entrywise arithmetic',
    gradients=[gw,gb],branch_gradient=gradient,mode_gradients=mode_grad,
    final_loss=loss(1.6,.3),selective_matrix=v,selective_recomputed=a,
    inspected_actual_state_count=len(states),mechanism_checks=14,
    schematic_boundaries=['activation slots are illustrative, not measured bytes',
                         'compression rounding is illustrative, not the Adacc configuration',
                         'network connections illustrate the error path, not a training benchmark'])
(B/'qa/content-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
