from common import TestCase, run_tests
import torch
from torch.autograd import Variable


class TestIndexing(TestCase):
    def test_single_int(self):
        v = Variable(torch.randn(5, 7, 3))
        self.assertEqual(v[4].shape, (7, 3))

    def test_multiple_int(self):
        v = Variable(torch.randn(5, 7, 3))
        self.assertEqual(v[4].shape, (7, 3))
        self.assertEqual(v[4, :, 1].shape, (7,))

    def test_none(self):
        v = Variable(torch.randn(5, 7, 3))
        self.assertEqual(v[None].shape, (1, 5, 7, 3))
        self.assertEqual(v[:, None].shape, (5, 1, 7, 3))
        self.assertEqual(v[:, None, None].shape, (5, 1, 1, 7, 3))
        self.assertEqual(v[..., None].shape, (5, 7, 3, 1))

    def test_step(self):
        v = Variable(torch.arange(10))
        self.assertEqual(v[::1], v)
        self.assertEqual(v[::2].data.tolist(), [0, 2, 4, 6, 8])
        self.assertEqual(v[::3].data.tolist(), [0, 3, 6, 9])
        self.assertEqual(v[::11].data.tolist(), [0])
        self.assertEqual(v[1:6:2].data.tolist(), [1, 3, 5])

    def test_step_assignment(self):
        v = Variable(torch.zeros(4, 4))
        v[0, 1::2] = Variable(torch.Tensor([3, 4]))
        self.assertEqual(v[0].data.tolist(), [0, 3, 0, 4])
        self.assertEqual(v[1:].data.sum(), 0)

    def test_byte_mask(self):
        v = Variable(torch.randn(5, 7, 3))
        mask = Variable(torch.ByteTensor([1, 0, 1, 1, 0]))
        self.assertEqual(v[mask].shape, (3, 7, 3))
        self.assertEqual(v[mask], torch.stack([v[0], v[2], v[3]]))

    def test_multiple_byte_mask(self):
        v = Variable(torch.randn(5, 7, 3))
        # note: these broadcast together and are transposed to the first dim
        mask1 = Variable(torch.ByteTensor([1, 0, 1, 1, 0]))
        mask2 = Variable(torch.ByteTensor([1, 1, 1]))
        self.assertEqual(v[mask1, :, mask2].shape, (3, 7))

    def test_byte_mask2d(self):
        v = Variable(torch.randn(5, 7, 3))
        c = Variable(torch.randn(5, 7))
        num_ones = (c > 0).data.sum()
        r = v[c > 0]
        self.assertEqual(r.shape, (num_ones, 3))

    def test_int_indices(self):
        v = Variable(torch.randn(5, 7, 3))
        self.assertEqual(v[[0, 4, 2]].shape, (3, 7, 3))
        self.assertEqual(v[:, [0, 4, 2]].shape, (5, 3, 3))
        self.assertEqual(v[:, [[0, 1], [4, 3]]].shape, (5, 2, 2, 3))

    def test_int_indices2d(self):
        # From the NumPy indexing example
        x = Variable(torch.arange(0, 12).view(4, 3))
        rows = Variable(torch.LongTensor([[0, 0], [3, 3]]))
        columns = Variable(torch.LongTensor([[0, 2], [0, 2]]))
        self.assertEqual(x[rows, columns].data.tolist(), [[0, 2], [9, 11]])

    def test_int_indices_broadcast(self):
        # From the NumPy indexing example
        x = Variable(torch.arange(0, 12).view(4, 3))
        rows = Variable(torch.LongTensor([0, 3]))
        columns = Variable(torch.LongTensor([0, 2]))
        result = x[rows[:, None], columns]
        self.assertEqual(result.data.tolist(), [[0, 2], [9, 11]])

    def test_basic_advanced_combined(self):
        # From the NumPy indexing example
        x = Variable(torch.arange(0, 12).view(4, 3))
        self.assertEqual(x[1:2, 1:3], x[1:2, [1, 2]])
        self.assertEqual(x[1:2, 1:3].data.tolist(), [[4, 5]])

        # Check that it is a copy
        unmodified = x.clone()
        x[1:2, [1, 2]].zero_()
        self.assertEqual(x, unmodified)

        # But assignment should modify the original
        unmodified = x.clone()
        x[1:2, [1, 2]] = 0
        self.assertNotEqual(x, unmodified)

    def test_int_assignment(self):
        x = Variable(torch.arange(0, 4).view(2, 2))
        x[1] = 5
        self.assertEqual(x.data.tolist(), [[0, 1], [5, 5]])

        x = Variable(torch.arange(0, 4).view(2, 2))
        x[1] = Variable(torch.arange(5, 7))
        self.assertEqual(x.data.tolist(), [[0, 1], [5, 6]])

    def test_byte_tensor_assignment(self):
        x = Variable(torch.arange(0, 16).view(4, 4))
        b = Variable(torch.ByteTensor([True, False, True, False]))
        value = Variable(torch.Tensor([3, 4, 5, 6]))
        x[b] = value
        self.assertEqual(x[0], value)
        self.assertEqual(x[1].data, torch.arange(4, 8))
        self.assertEqual(x[2], value)
        self.assertEqual(x[3].data, torch.arange(12, 16))


def tensor(*args, **kwargs):
    return Variable(torch.Tensor(*args, **kwargs))


def byteTensor(data):
    return Variable(torch.ByteTensor(data))


def ones(*args):
    return Variable(torch.ones(*args))


def zeros(*args):
    return Variable(torch.zeros(*args))


# The tests below are from NumPy test_indexing.py with some modifications to
# make them compatible with PyTorch. It's licensed under the BDS license below:
#
# Copyright (c) 2005-2017, NumPy Developers.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided
#        with the distribution.
#
#     * Neither the name of the NumPy Developers nor the names of any
#        contributors may be used to endorse or promote products derived
#        from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


class NumpyTests(TestCase):
    def test_index_no_floats(self):
        a = Variable(torch.Tensor([[[5]]]))

        self.assertRaises(IndexError, lambda: a[0.0])
        self.assertRaises(IndexError, lambda: a[0, 0.0])
        self.assertRaises(IndexError, lambda: a[0.0, 0])
        self.assertRaises(IndexError, lambda: a[0.0, :])
        self.assertRaises(IndexError, lambda: a[:, 0.0])
        self.assertRaises(IndexError, lambda: a[:, 0.0, :])
        self.assertRaises(IndexError, lambda: a[0.0, :, :])
        self.assertRaises(IndexError, lambda: a[0, 0, 0.0])
        self.assertRaises(IndexError, lambda: a[0.0, 0, 0])
        self.assertRaises(IndexError, lambda: a[0, 0.0, 0])
        self.assertRaises(IndexError, lambda: a[-1.4])
        self.assertRaises(IndexError, lambda: a[0, -1.4])
        self.assertRaises(IndexError, lambda: a[-1.4, 0])
        self.assertRaises(IndexError, lambda: a[-1.4, :])
        self.assertRaises(IndexError, lambda: a[:, -1.4])
        self.assertRaises(IndexError, lambda: a[:, -1.4, :])
        self.assertRaises(IndexError, lambda: a[-1.4, :, :])
        self.assertRaises(IndexError, lambda: a[0, 0, -1.4])
        self.assertRaises(IndexError, lambda: a[-1.4, 0, 0])
        self.assertRaises(IndexError, lambda: a[0, -1.4, 0])
        # self.assertRaises(IndexError, lambda: a[0.0:, 0.0])
        # self.assertRaises(IndexError, lambda: a[0.0:, 0.0,:])

    def test_none_index(self):
        # `None` index adds newaxis
        a = tensor([1, 2, 3])
        self.assertEqual(a[None].dim(), a.dim() + 1)

    def test_empty_tuple_index(self):
        # Empty tuple index creates a view
        a = tensor([1, 2, 3])
        self.assertEqual(a[()], a)
        self.assertEqual(a[()].data_ptr(), a.data_ptr())

    # @unittest.skip('failing')
    def test_empty_fancy_index(self):
        # Empty list index creates an empty array
        a = tensor([1, 2, 3])
        self.assertEqual(a[[]], Variable(torch.Tensor()))

        b = tensor([]).long()
        self.assertEqual(a[[]], Variable(torch.LongTensor()))

        b = tensor([]).float()
        self.assertRaises(RuntimeError, lambda: a[b])

    def test_ellipsis_index(self):
        a = tensor([[1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]])
        self.assertIsNot(a[...], a)
        self.assertEqual(a[...], a)
        # `a[...]` was `a` in numpy <1.9.
        self.assertEqual(a[...].data_ptr(), a.data_ptr())

        # Slicing with ellipsis can skip an
        # arbitrary number of dimensions
        self.assertEqual(a[0, ...], a[0])
        self.assertEqual(a[0, ...], a[0, :])
        self.assertEqual(a[..., 0], a[:, 0])

        # Slicing with ellipsis always results
        # in an array, not a scalar
        self.assertEqual(a[0, ..., 1], tensor([2]))

        # Assignment with `(Ellipsis,)` on 0-d arrays
        # b = np.array(1)
        # b[(Ellipsis,)] = 2
        # self.assertEqual(b, 2)

    def test_single_int_index(self):
        # Single integer index selects one row
        a = tensor([[1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]])

        self.assertEqual(a[0].data, [1, 2, 3])
        self.assertEqual(a[-1].data, [7, 8, 9])

        # Index out of bounds produces IndexError
        self.assertRaises(IndexError, a.__getitem__, 1 << 30)
        # Index overflow produces Exception  NB: different exception type
        self.assertRaises(Exception, a.__getitem__, 1 << 64)

    def test_single_bool_index(self):
        # Single boolean index
        a = tensor([[1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]])

        self.assertEqual(a[True], a[None])
        self.assertEqual(a[False], a[None][0:0])

    def test_boolean_shape_mismatch(self):
        arr = ones((5, 4, 3))

        # TODO: prefer IndexError
        index = byteTensor([True])
        self.assertRaisesRegex(RuntimeError, 'mask', lambda: arr[index])

        index = byteTensor([False] * 6)
        self.assertRaisesRegex(RuntimeError, 'mask', lambda: arr[index])

        index = Variable(torch.ByteTensor(4, 4)).zero_()
        self.assertRaisesRegex(RuntimeError, 'mask', lambda: arr[index])

        self.assertRaisesRegex(RuntimeError, 'mask', lambda: arr[(slice(None), index)])

    def test_boolean_indexing_onedim(self):
        # Indexing a 2-dimensional array with
        # boolean array of length one
        a = tensor([[0., 0., 0.]])
        b = byteTensor([True])
        self.assertEqual(a[b], a)
        # boolean assignment
        a[b] = 1.
        self.assertEqual(a, tensor([[1., 1., 1.]]))

    def test_boolean_assignment_value_mismatch(self):
        # A boolean assignment should fail when the shape of the values
        # cannot be broadcast to the subscription. (see also gh-3458)
        a = Variable(torch.arange(0, 4))

        def f(a, v):
            a[a > -1] = tensor(v)

        self.assertRaisesRegex(Exception, "expand", f, a, [])
        self.assertRaisesRegex(Exception, 'expand', f, a, [1, 2, 3])
        self.assertRaisesRegex(Exception, 'expand', f, a[:1], [1, 2, 3])

    def test_boolean_indexing_twodim(self):
        # Indexing a 2-dimensional array with
        # 2-dimensional boolean array
        a = tensor([[1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]])
        b = byteTensor([[True, False, True],
                        [False, True, False],
                        [True, False, True]])
        self.assertEqual(a[b], tensor([1, 3, 5, 7, 9]))
        self.assertEqual(a[b[1]], tensor([[4, 5, 6]]))
        self.assertEqual(a[b[0]], a[b[2]])

        # boolean assignment
        a[b] = 0
        self.assertEqual(a, tensor([[0, 2, 0],
                                    [4, 0, 6],
                                    [0, 8, 0]]))

    def test_everything_returns_views(self):
        # Before `...` would return a itself.
        a = tensor(5)

        self.assertIsNot(a, a[()])
        self.assertIsNot(a, a[...])
        self.assertIsNot(a, a[:])

    def test_broaderrors_indexing(self):
        a = zeros(5, 5)
        self.assertRaisesRegex(RuntimeError, 'match the size', a.__getitem__, ([0, 1], [0, 1, 2]))
        self.assertRaisesRegex(RuntimeError, 'match the size', a.__setitem__, ([0, 1], [0, 1, 2]), 0)

    def test_trivial_fancy_out_of_bounds(self):
        a = zeros(5)
        ind = ones(20).long()
        ind[-1] = 10
        self.assertRaises(RuntimeError, a.__getitem__, ind)
        self.assertRaises(RuntimeError, a.__setitem__, ind, 0)
        ind = ones(20).long()
        ind[0] = 11
        self.assertRaises(RuntimeError, a.__getitem__, ind)
        self.assertRaises(RuntimeError, a.__setitem__, ind, 0)

    def test_index_is_larger(self):
        # Simple case of fancy index broadcasting of the index.
        a = zeros((5, 5))
        a[[[0], [1], [2]], [0, 1, 2]] = tensor([2, 3, 4])

        self.assertTrue((a[:3, :3] == tensor([2, 3, 4])).all())

    def test_broadcast_subspace(self):
        a = zeros((100, 100))
        v = Variable(torch.arange(0, 100))[:, None]
        b = Variable(torch.arange(99, -1, -1).long())
        a[b] = v
        expected = b.double().unsqueeze(1).expand(100, 100)
        self.assertEqual(a, expected)


if __name__ == '__main__':
    run_tests()
