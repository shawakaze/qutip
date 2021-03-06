#
#Calculates the Schrodinger cat state for
#a superposition of two coherent states.
#
from qutip import *
from pylab import * #loads matplotlib

def run():
    #Number of basis states
    N = 20 

    #amplitude of coherent states
    alpha=2.0+2j

    #define ladder oeprators
    a = destroy(N)

    #define displacement oeprators
    D1=displace(N,alpha)
    D2=displace(N,-alpha)

    #create superposition of coherent states
    psi=(D1+D2)*basis(N,0)

    #calculate Wigner function
    xvec = linspace(-5,5,200)
    yvec=xvec
    W=wigner(psi,xvec,yvec)

    #plot Wigner function as filled contour
    plt=contourf(xvec,yvec,W,100)
    xlim([-5,5])
    ylim([-5,5])
    title('Wigner function of Schrodinger cat')

    #add a colorbar for pseudoprobability
    cbar=colorbar(plt)#create colorbar
    cbar.ax.set_ylabel('Pseudoprobability')
    #show plot
    show()
    
if __name__ == "__main__":
    run()
