from qutip import *

def probqmc2(E,kappa,gamma,g,wc,w0,wl,N,tlist,ntraj):
	ida=qeye(N)
	idatom=qeye(2)
	a=tensor(destroy(N),idatom)
	sm=tensor(ida,sigmam())
	H=(w0-wl)*sm.dag()*sm+(wc-wl)*a.dag()*a+1j*g*(a.dag()*sm-sm.dag()*a)+E*(a.dag()+a)

	#collapse operators
	C1=sqrt(2*kappa)*a
	C2=sqrt(gamma)*sm
	C1dC1=C1.dag()*C1
	C2dC2=C2.dag()*C2

	#intial state
	psi0=tensor(basis(N,0),basis(2,1))

	# evolve and calculate expectation values
	expt_list = mcwf_evolve(tlist, H, psi0, ntraj, [C1, C2], [C1dC1, C2dC2, a])

	return expt_list[0], expt_list[1], expt_list[2]
	

kappa=2
gamma=0.2
g=1
wc=0
w0=0
wl=0
E=0.5
N=4
tlist=linspace(0,10,100)
ntraj=100

start_time=time.time()
count1, count2, infield = probqmc2(E,kappa,gamma,g,wc,w0,wl,N,tlist,ntraj)
print 'time elapsed = ' +str(time.time()-start_time) 

plot(tlist,real(count1))
plot(tlist,real(count2))
xlabel('Time')
ylabel('Transmitted Intensity and Spontaneous Emission')
show()

