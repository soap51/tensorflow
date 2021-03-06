# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Test conversion of graphs involving INT32 tensors and operations."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np

from tensorflow.python.compiler.tensorrt.test import tf_trt_integration_test_base as trt_test
from tensorflow.python.framework import constant_op
from tensorflow.python.framework import dtypes
from tensorflow.python.ops import array_ops
from tensorflow.python.ops import math_ops
from tensorflow.python.ops import nn
from tensorflow.python.platform import test


class ExcludeUnsupportedInt32Test(trt_test.TfTrtIntegrationTestBase):
  """Test exclusion of ops which are not supported in INT32 mode by TF-TRT"""

  def _ConstOp(self, shape, dtype):
    return constant_op.constant(np.random.randn(*shape), dtype=dtype)

  def GraphFn(self, x):
    dtype = x.dtype
    b = self._ConstOp((4, 10), dtype)
    x = math_ops.matmul(x, b)
    b = self._ConstOp((10,), dtype)
    x = nn.bias_add(x, b)
    return array_ops.identity(x, name='output_0')

  def GetParams(self):
    return self.BuildParams(self.GraphFn, dtypes.int32, [[100, 4]], [[100, 10]])

  def GetConversionParams(self, run_params):
    """Return a ConversionParams for test."""
    conversion_params = super(ExcludeUnsupportedInt32Test,
                              self).GetConversionParams(run_params)
    return conversion_params._replace(
        max_batch_size=100,
        maximum_cached_engines=1,
        # Disable layout optimizer, since it will convert BiasAdd with NHWC
        # format to NCHW format under four dimentional input.
        rewriter_config_template=trt_test.OptimizerDisabledRewriterConfig())

  def ExpectedEnginesToBuild(self, run_params):
    """Return the expected engines to build."""
    return []


if __name__ == '__main__':
  test.main()
