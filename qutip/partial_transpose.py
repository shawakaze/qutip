# This file is part of QuTIP.
#
#    QuTIP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
# Significant parts of this code was contributed by Jonas Neergaard-Nielsen
#
###########################################################################

#
# Note: Experimental, work in progress.
# 

import numpy as np

from qutip.qobj import Qobj

def partial_transpose(rho, pt_mask, method='dense'):
    """
    Return the partial transpose of a Qobj instance `rho`,
    where `pt_mask` is an array/list with length that equals
    the number of components of `rho` (that is, the length of
    `rho.dims[0]`), and the values in `pt_mask` indicates whether
    or not the corresponding subsystem is to be transposed.
    """
    if method == 'sparse':
        return _partial_transpose_sparse(rho, pt_mask)
    else:           
        return _partial_transpose_dense(rho, pt_mask)


def _partial_transpose_dense(rho, pt_mask):
    """
    Based on Jonas' implementation using numpy.
    Very fast for dense problems.
    """
    nsys = len(pt_mask)
    pt_dims = np.arange(2*nsys).reshape(2,nsys).T
    pt_idx = np.concatenate([[pt_dims[n,pt_mask[n]] for n in range(nsys)],
                            [pt_dims[n,1-pt_mask[n]] for n in range(nsys)]])

    data = rho.data.toarray().reshape(np.array(rho.dims).flatten()).transpose(pt_idx).reshape(rho.shape)
    return Qobj(data, dims=rho.dims)


def _partial_transpose_sparse(rho, pt_mask):
    """
    Implement the partial transpose using the CSR sparse matrix.
    """

    data = sp.lil_matrix((rho.shape[0],rho.shape[1]), dtype=complex)
    
    for m in range(len(rho.data.indptr)-1):

        n1 = rho.data.indptr[m]
        n2 = rho.data.indptr[m+1]
    
        psi_A = state_index_number(rho.dims[0], m)
    
        for idx, n in enumerate(rho.data.indices[n1:n2]):
        
            psi_B = state_index_number(rho.dims[1], n)
            
            m_pt = state_number_index(rho.dims[1], choose(pt_mask, [psi_A, psi_B]))
            n_pt = state_number_index(rho.dims[0], choose(pt_mask, [psi_B, psi_A]))
            
            data[m_pt, n_pt] = rho.data.data[n1+idx]
            
    return Qobj(data.tocsr(), dims=rho.dims)


def _partial_transpose_reference(rho, pt_mask):
    """
    This is a reference implementation that explicitly loops over
    all states and performs the transpose. It's slow but easy to 
    understand and useful for testing.
    """

    A_pt = zeros(rho.shape, dtype=complex)
    
    for psi_A in state_number_enumerate(rho.dims[0]):
        m = state_number_index(rho.dims[0], psi_A)
        
        for psi_B in state_number_enumerate(rho.dims[1]):
            n = state_number_index(rho.dims[1], psi_B)

            m_pt = state_number_index(rho.dims[1], choose(pt_mask, [psi_A, psi_B]))
            n_pt = state_number_index(rho.dims[0], choose(pt_mask, [psi_B, psi_A]))
            
            A_pt[m_pt, n_pt] = rho.data[m,n]
            
    return Qobj(A_pt, dims=rho.dims)
