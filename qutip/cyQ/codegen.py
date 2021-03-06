#This file is part of QuTIP.
#
#    QuTIP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#    QuTIP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with QuTIP.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2011-2013, Paul D. Nation & Robert J. Johansson
#
###########################################################################
import numpy as np
from qutip import odeconfig
class Codegen():
    """
    Class for generating cython code files at runtime.
    """
    def __init__(self,h_terms=None,h_tdterms=None,h_td_inds=None,args=None,c_terms=None,c_tdterms=[],c_td_inds=None,tab="\t",type='me'):
        import sys,os
        sys.path.append(os.getcwd())
        #--------------------------------------------#
        #  CLASS PROPERTIES`                         #
        #--------------------------------------------#
        
        #--- Hamiltonian time-depdendent pieces ----#
        self.type=type
        if isinstance(h_terms,int):
            h_terms=range(h_terms)
        self.h_terms=h_terms        #number of H pieces
        self.h_tdterms=h_tdterms    #list of time-dependent strings
        self.h_td_inds=h_td_inds    #indicies of time-dependnt terms
        self.args=args              #args for strings
        #--- Collapse operator time-depdendent pieces ----#
        self.c_terms=c_terms        #number of C pieces
        self.c_tdterms=c_tdterms    #list of time-dependent strings
        self.c_td_inds=c_td_inds    #indicies of time-dependnt terms
        #--- Code generator properties----#
        self.code=[] #strings to be written to file
        self.tab=tab # type of tab to use
        self.level=0 #indent level
        #math functions available from numpy
        self.func_list=[func+'(' for func in dir(np.math)[4:-1]] #add a '(' on the end to guarentee function is selected 
        #fix pi and e strings since they are constants and not functions
        self.func_list[self.func_list.index('pi(')]='pi' 
    #--------------------------------------------#
    #  CLASS METHODS`                            #
    #--------------------------------------------#
    def write(self,string):
        """write lines of code to self.code"""
        self.code.append(self.tab*self.level+string+"\n")    
    #----
    def file(self,filename):
        """open file called filename for writing"""
        self.file=open(filename,"w")
    #----
    def generate(self,filename="rhs.pyx"):
        """generate the file"""
        self.time_vars()
        for line in cython_preamble():
            self.write(line)
        
        #write function for Hamiltonian terms (there is always at least one term)
        for line in cython_checks()+self.ODE_func_header():
            self.write(line)
        self.indent()
        for line in self.func_vars():
            self.write(line)
        for line in self.func_for():
            self.write(line)
        self.write(self.func_end())
        self.dedent()
        if self.type == 'mc':
            for line in cython_checks()+cython_spmv():
                 self.write(line)
        else:
            for line in cython_checks()+cython_spmvpy():
                 self.write(line)
        
        #generate collapse operator functions if any c_terms
        if any(self.c_tdterms):
            for line in cython_checks()+self.col_spmv_header()+cython_col_spmv():
                self.write(line)
            self.indent()
            for line in self.func_which():
                self.write(line)
            self.write(self.func_end())
            self.dedent()
            for line in cython_checks()+self.col_expect_header()+cython_col_expect(self.args):
                self.write(line)
            self.indent()
            for line in self.func_which_expect():
                self.write(line)
            self.write(self.func_end_real())
            self.dedent()
        self.file(filename)
        self.file.writelines(self.code)
        self.file.close()
        odeconfig.cgen_num+=1
    #----
    def indent(self):
        """increase indention level by one"""
        self.level+=1
    #----
    def dedent(self):
        """decrease indention level by one"""
        if self.level==0:
            raise SyntaxError("Error in code generator")
        self.level-=1
    #----
    def ODE_func_header(self):
        """Creates function header for time-dependent ODE RHS."""
        func_name="def cyq_td_ode_rhs("
        input_vars="double t, np.ndarray[CTYPE_t, ndim=1] vec" #strings for time and vector variables
        for k in self.h_terms:
            input_vars+=", np.ndarray[CTYPE_t, ndim=1] data"+str(k)+", np.ndarray[int, ndim=1] idx"+str(k)+", np.ndarray[int, ndim=1] ptr"+str(k)
        if any(self.c_tdterms):
            for k in range(len(self.h_terms),len(self.h_terms)+len(self.c_tdterms)):
                input_vars+=", np.ndarray[CTYPE_t, ndim=1] data"+str(k)+", np.ndarray[int, ndim=1] idx"+str(k)+", np.ndarray[int, ndim=1] ptr"+str(k)
        if self.args:
            td_consts=list(self.args.items())
            td_len=len(td_consts)
            for jj in range(td_len):
                kind=type(td_consts[jj][1]).__name__
                input_vars+=", np."+kind+"_t"+" "+td_consts[jj][0]
        func_end="):"
        return [func_name+input_vars+func_end]
    #----
    def col_spmv_header(self):
        """
        Creates function header for time-dependent
        collapse operator terms.
        """
        func_name="def col_spmv("
        input_vars="int which, double t, np.ndarray[CTYPE_t, ndim=1] data, np.ndarray[int] idx,np.ndarray[int] ptr,np.ndarray[CTYPE_t, ndim=2] vec"
        if len(self.args)>0:
            td_consts=list(self.args.items())
            td_len=len(td_consts)
            for jj in range(td_len):
                kind=type(td_consts[jj][1]).__name__
                input_vars+=", np."+kind+"_t"+" "+td_consts[jj][0]
        func_end="):"
        return [func_name+input_vars+func_end]
    #----
    def col_expect_header(self):
        """
        Creates function header for time-dependent
        collapse expectation values.
        """
        func_name="def col_expect("
        input_vars="int which, double t, np.ndarray[CTYPE_t, ndim=1] data, np.ndarray[int] idx,np.ndarray[int] ptr,np.ndarray[CTYPE_t, ndim=2] vec"
        if len(self.args)>0:
            td_consts=list(self.args.items())
            td_len=len(td_consts)
            for jj in range(td_len):
                kind=type(td_consts[jj][1]).__name__
                input_vars+=", np."+kind+"_t"+" "+td_consts[jj][0]
        func_end="):"
        return [func_name+input_vars+func_end]
    #----
    def time_vars(self):
        """
        Rewrites time-dependent parts to include np.
        """
        if self.h_tdterms:
            for jj in range(len(self.h_tdterms)):
                text=self.h_tdterms[jj]
                any_np=np.array([text.find(x) for x in self.func_list])
                ind=np.nonzero(any_np>-1)[0]
                for kk in ind:
                    new_text='np.'+self.func_list[kk]
                    text=text.replace(self.func_list[kk],new_text)
                self.h_tdterms[jj]=text
        if len(self.c_tdterms)>0:
            for jj in range(len(self.c_tdterms)):
                text=self.c_tdterms[jj]
                any_np=np.array([text.find(x) for x in self.func_list])
                ind=np.nonzero(any_np>-1)[0]
                for kk in ind:
                    new_text='np.'+self.func_list[kk]
                    text=text.replace(self.func_list[kk],new_text)
                self.c_tdterms[jj]=text
    #----
    def func_vars(self):
        """Writes the variables and their types & spmv parts"""
        func_vars=["",'cdef Py_ssize_t row','cdef int num_rows = len(vec)','cdef np.ndarray[CTYPE_t, ndim=2] out = np.zeros((num_rows,1),dtype=np.complex)']
        func_vars.append(" ") #add a spacer line between variables and Hamiltonian components.
        tdterms=self.h_tdterms
        hinds=0
        for ht in self.h_terms:
            hstr=str(ht)
            if self.type=='mc':
                str_out="cdef np.ndarray[CTYPE_t, ndim=2] Hvec"+hstr+" = "+"spmv(data"+hstr+","+"idx"+hstr+","+"ptr"+hstr+","+"vec"+")"
                if ht in self.h_td_inds:
                    str_out+=" * "+tdterms[hinds]
                    hinds+=1
                func_vars.append(str_out)
            else:
                if self.h_tdterms[ht] == "1.0":
                    str_out="spmvpy(data%s, idx%s, ptr%s, vec, 1.0, out)" % (ht,ht,ht)
                else:
                    str_out="spmvpy(data%s, idx%s, ptr%s, vec, %s, out)" % (ht,ht,ht,self.h_tdterms[ht])
                func_vars.append(str_out)
        if len(self.c_tdterms)>0:
            func_vars.append(" ") #add a spacer line between Hamiltonian components and collapse copoenets.
            terms=len(self.c_tdterms)
            tdterms=self.c_tdterms
            cinds=0
            for ct in range(terms):
                cstr=str(ct+hinds+1)
                str_out="cdef np.ndarray[CTYPE_t, ndim=2] Cvec"+str(ct)+" = "+"spmv(data"+cstr+","+"idx"+cstr+","+"ptr"+cstr+","+"vec"+")"
                if ct in range(len(self.c_td_inds)):
                    str_out+=" * np.abs("+tdterms[ct]+")**2"
                    cinds+=1
                func_vars.append(str_out)
        return func_vars
    #----
    def func_for(self):
        """Writes function for-loop"""
        func_terms=[]
        if self.type=='mc':
            func_terms.append("for row in range(num_rows):")
            sum_string="\tout[row,0] = Hvec0[row,0]"
            for ht in range(1,len(self.h_terms)):
                sum_string+=" + Hvec"+str(ht)+"[row,0]"
            if any(self.c_tdterms):
                for ct in range(len(self.c_tdterms)):
                    sum_string+=" + Cvec"+str(ct)+"[row,0]"
            func_terms.append(sum_string)
        return func_terms
    #----
    def func_which(self):
        """Writes 'else-if' statements forcollapse operator eval function"""
        out_string=[]
        ind=0
        for k in self.c_td_inds:
            out_string.append("if which == "+str(k)+":")
            out_string.append("\tout*= "+self.c_tdterms[ind])
            ind+=1
        return out_string
    #----
    def func_which_expect(self):
        """Writes 'else-if' statements for collapse expect function
        """
        out_string=[]
        ind=0
        for k in self.c_td_inds:
            out_string.append("if which == "+str(k)+":")
            out_string.append("\tout*= np.conj("+self.c_tdterms[ind]+")")
            ind+=1
        return out_string
    #----
    def func_end(self):
        return "return out"
    #----
    def func_end_real(self):
        return "return np.float64(np.real(out))"
        
#
# Alternative implementation of the Cython code generator. Include the
# parameters directly in the generated code file instead of passing
# them as arguments through the ODE solver callback function
#       
class Codegen2():
    """
    Class for generating cython code files at runtime.
    """
    def __init__(self, n_L_terms, L_coeffs, args, tab="\t"):
        import sys,os
        sys.path.append(os.getcwd())
        self.n_L_terms = n_L_terms
        self.L_coeffs  = L_coeffs
        self.args      = args
        self.code=[]
        self.tab=tab
        self.level=0
        self.func_list=[func+'(' for func in dir(np.math)[4:-1]] #add a '(' on the end to guarentee function is selected 
        
    #
    # write lines of code to self.code
    #
    def write(self,string):
        self.code.append(self.tab*self.level+string+"\n")
    
    #
    # open file called filename for writing    
    #
    def file(self,filename):
        self.file=open(filename,"w")
   
    #
    # generate the file 
    #
    def generate(self,filename="rhs.pyx"):
        self.time_vars()
        for line in cython_preamble()+cython_checks()+self.func_header():
            self.write(line)
        self.indent()
        for line in self.func_body():
            self.write(line)
        self.write(self.func_end())
        self.dedent()
        for line in cython_checks()+cython_spmvpy():
            self.write(line)
        self.file(filename)
        self.file.writelines(self.code)
        self.file.close()
        odeconfig.cgen_num += 1        
        
    #increase indention level by one
    def indent(self):
        self.level+=1
        
    #decrease indention level by one
    def dedent(self):
        if self.level==0:
            raise SyntaxError("Error in code generator")
        self.level-=1
                
    def func_header(self):
        """
        Creates function header for time-dependent ODE RHS.
        """
        func_name  = "def cyq_td_ode_rhs("
        input_vars = "double t, np.ndarray[CTYPE_t, ndim=1] vec, " #strings for time and vector variables
        arg_list = []
        for k in range(self.n_L_terms):
            arg_list.append("np.ndarray[CTYPE_t, ndim=1] data"+str(k)+", np.ndarray[int, ndim=1] idx"+str(k)+", np.ndarray[int, ndim=1] ptr"+str(k))

        if self.args:
            for name, value in self.args.iteritems():
                kind = type(value).__name__
                arg_list.append("np."+kind+"_t"+" "+name)

        input_vars += ", ".join(arg_list)

        func_end="):"
        return [func_name+input_vars+func_end]
        
        
    def time_vars(self):
        """
        Rewrites time-dependent parts to include np.
        """
        for n in range(len(self.L_coeffs)):
            text = self.L_coeffs[n]
            any_np = np.array([text.find(x) for x in self.func_list])
            ind = np.nonzero(any_np>-1)[0]
            for m in ind:
                text = text.replace(self.func_list[m], 'np.'+self.func_list[m])
            self.L_coeffs[n]=text

            
    def func_body(self):
        """
        Writes the variables and their types & spmv parts
        """
        line_list = ['cdef int num_rows = len(vec)','cdef np.ndarray[CTYPE_t, ndim=2] out = np.zeros((num_rows,1),dtype=np.complex)']

        for n in range(self.n_L_terms):
            if self.L_coeffs[n] == "1.0":
                str_out="spmvpy(data%s, idx%s, ptr%s, vec, 1.0, out)" % (n,n,n)
            else:
                str_out="spmvpy(data%s, idx%s, ptr%s, vec, %s, out)" % (n,n,n,self.L_coeffs[n])
            line_list.append(str_out)
        return line_list
        
    def func_end(self):
        return "return out"        
        
        
def cython_preamble():
    """
    Returns list of strings for standard Cython file preamble.
    """
    line0="# This file is generated automatically by QuTiP. (C) 2011-2013 Paul D. Nation & J. R. Johansson"
    line1="import numpy as np"
    line2="cimport numpy as np"
    line3="cimport cython"
    line4=""
    line5="ctypedef np.complex128_t CTYPE_t"
    line6="ctypedef np.float64_t DTYPE_t"
    return [line0,line1,line2,line3,line4,line5,line6]

def cython_checks():
    """
    List of strings that turn off Cython checks.
    """
    line0=""
    line1=""
    line2="@cython.boundscheck(False)"
    line3="@cython.wraparound(False)"
    return [line0,line1,line2,line3]


def cython_spmv():
    """
    Writes SPMV function.
    """
    line0="def spmv(np.ndarray[CTYPE_t, ndim=1] data, np.ndarray[int] idx,np.ndarray[int] ptr,np.ndarray[CTYPE_t, ndim=1] vec):"
    line1="\tcdef Py_ssize_t row"
    line2="\tcdef int jj,row_start,row_end"
    line3="\tcdef int num_rows=len(vec)"
    line4="\tcdef CTYPE_t dot"
    line5="\tcdef np.ndarray[CTYPE_t, ndim=2] out = np.zeros((num_rows,1),dtype=np.complex)"
    line6="\tfor row in range(num_rows):"
    line7="\t\tdot=0.0"
    line8="\t\trow_start = ptr[row]"
    line9="\t\trow_end = ptr[row+1]"
    lineA="\t\tfor jj in range(row_start,row_end):"
    lineB="\t\t\tdot=dot+data[jj]*vec[idx[jj]]"
    lineC="\t\tout[row,0]=dot"
    lineD="\treturn out"
    return [line0,line1,line2,line3,line4,line5,line6,line7,line8,line9,lineA,lineB,lineC,lineD]

def cython_spmvpy():
    """
    Writes spmvpy function: out = out + a * (data,idx,pty) * vec
    """
    code = """def spmvpy(np.ndarray[CTYPE_t, ndim=1] data, np.ndarray[int] idx,np.ndarray[int] ptr, np.ndarray[CTYPE_t, ndim=1] vec, CTYPE_t a, np.ndarray[CTYPE_t, ndim=2] out):
\tcdef Py_ssize_t row
\tcdef int jj,row_start,row_end
\tcdef int num_rows=len(vec)
\tcdef CTYPE_t dot
\tfor row in range(num_rows):
\t\tdot=0.0
\t\trow_start = ptr[row]
\t\trow_end = ptr[row+1]
\t\tfor jj in range(row_start, row_end):
\t\t\tdot = dot + data[jj]*vec[idx[jj]]
\t\tout[row,0] = out[row,0] + a * dot
\treturn out
    """
    return code.split("\n")

def cython_col_spmv():
    """
    Writes col_SPMV vars.
    """
    line1="\tcdef Py_ssize_t row"
    line2="\tcdef int jj,row_start,row_end"
    line3="\tcdef int num_rows=len(vec)"
    line4="\tcdef CTYPE_t dot"
    line5="\tcdef np.ndarray[CTYPE_t, ndim=2] out = np.zeros((num_rows,1),dtype=np.complex)"
    line6="\tfor row in range(num_rows):"
    line7="\t\tdot=0.0"
    line8="\t\trow_start = ptr[row]"
    line9="\t\trow_end = ptr[row+1]"
    lineA="\t\tfor jj in range(row_start,row_end):"
    lineB="\t\t\tdot=dot+data[jj]*vec[idx[jj],0]"
    lineC="\t\tout[row,0]=dot"
    return [line1,line2,line3,line4,line5,line6,line7,line8,line9,lineA,lineB,lineC]

def cython_col_expect(args):
    """
    Writes col_expect vars.
    """
    line1="\tcdef Py_ssize_t row"
    line2="\tcdef int num_rows=len(vec)"
    line3="\tcdef CTYPE_t out = 0.0"
    line4="\tcdef np.ndarray[CTYPE_t, ndim=2] vec_ct = vec.conj().T"
    line5="\tcdef np.ndarray[CTYPE_t, ndim=2] dot = col_spmv(which,t,data,idx,ptr,vec"
    if args:
        for td_const in args.items():
            line5+=","+td_const[0]
    line5+=")"
    line6="\tfor row in range(num_rows):"
    line7="\t\tout+=vec_ct[0,row]*dot[row,0]"
    return [line1,line2,line3,line4,line5,line6,line7]
