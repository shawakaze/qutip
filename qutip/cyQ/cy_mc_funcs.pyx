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
cimport numpy as np
cimport cython

ctypedef np.complex128_t CTYPE_t
ctypedef np.float64_t DTYPE_t

@cython.boundscheck(False)
@cython.wraparound(False)
def spmv(np.ndarray[CTYPE_t, ndim=1] data, np.ndarray[int] idx,np.ndarray[int] ptr,np.ndarray[CTYPE_t, ndim=2] vec):
    cdef Py_ssize_t row
    cdef int jj,row_start,row_end
    cdef int num_rows=len(vec)
    cdef CTYPE_t dot
    cdef np.ndarray[CTYPE_t, ndim=2] out = np.zeros((num_rows,1),dtype=np.complex)
    for row in range(num_rows):
        dot=0.0
        row_start = ptr[row]
        row_end = ptr[row+1]
        for jj in range(row_start,row_end):
            dot+=data[jj]*vec[idx[jj],0]
        out[row,0]=dot
    return out



@cython.boundscheck(False)
@cython.wraparound(False)
def mc_expect(np.ndarray[CTYPE_t, ndim=1] data, np.ndarray[int] idx,np.ndarray[int] ptr,int isherm, np.ndarray[CTYPE_t, ndim=2] state):
    cdef np.ndarray[CTYPE_t, ndim=2] y = spmv(data,idx,ptr,state)
    cdef np.ndarray[CTYPE_t, ndim=2] x = state.conj().transpose()
    cdef int num_rows = len(state)
    cdef CTYPE_t dot = 0.0j
    for row in range(num_rows):
        dot+=x[0,row]*y[row,0]
    if isherm:
        return np.real(dot)
    else:
        return dot


@cython.boundscheck(False)
@cython.wraparound(False)
def spmv1d(np.ndarray[CTYPE_t, ndim=1] data, np.ndarray[int] idx,np.ndarray[int] ptr,np.ndarray[CTYPE_t, ndim=1] vec):
    cdef Py_ssize_t row
    cdef int jj,row_start,row_end
    cdef int num_rows=len(vec)
    cdef CTYPE_t dot
    cdef np.ndarray[CTYPE_t, ndim=2] out = np.zeros((num_rows,1),dtype=np.complex)
    for row in range(num_rows):
        dot=0.0
        row_start = ptr[row]
        row_end = ptr[row+1]
        for jj in range(row_start,row_end):
            dot+=data[jj]*vec[idx[jj]]
        out[row,0]=dot
    return out























