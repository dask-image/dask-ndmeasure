# -*- coding: utf-8 -*-


import operator

import numpy

import dask.array

from . import _compat
from . import _pycompat


def _norm_input_labels_index(input, labels=None, index=None):
    """
    Normalize arguments to a standard form.
    """

    input = _compat._asarray(input)

    if labels is None:
        labels = (input != 0).astype(numpy.int64)
        index = None

    if index is None:
        labels = (labels > 0).astype(numpy.int64)
        index = dask.array.ones(tuple(), dtype=numpy.int64, chunks=tuple())

    labels = _compat._asarray(labels)
    index = _compat._asarray(index)

    if input.shape != labels.shape:
        raise ValueError("The input and labels arrays must be the same shape.")

    return (input, labels, index)


def _get_label_matches(labels, index):
    lbl_mtch = operator.eq(
        index[(Ellipsis,) + labels.ndim * (None,)],
        labels[index.ndim * (None,)]
    )

    return lbl_mtch


def _ravel_shape_indices(dimensions, dtype=int, chunks=None):
    """
    Gets the raveled indices shaped like input.

    Normally this could have been solved with `arange` and `reshape`.
    Unfortunately that doesn't work out of the box with older versions
    of Dask. So we try to solve this by using indices and computing
    the raveled index from that.
    """

    dtype = numpy.dtype(dtype)

    indices = _compat._indices(
        dimensions, dtype=dtype, chunks=chunks
    )

    indices = list(indices)
    for i in _pycompat.irange(len(indices)):
        indices[i] *= dtype.type(numpy.prod(indices[i].shape[i + 1:]))
    indices = dask.array.stack(indices).sum(axis=0)

    return indices
