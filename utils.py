#!/usr/bin/env python
#
# Copyright 2012 Google Inc.
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

"""Contains utility functions."""

import logging

import config
import docs
import models

from google.appengine.ext.deferred import defer
from google.appengine.ext import ndb


def intClamp(v, low, high):
  """Clamps a value to the integer range [low, high] (inclusive).
  Args:
    v: Number to be clamped.
    low: Lower bound.
    high: Upper bound.
  Returns:
    An integer closest to v in the range [low, high].
  """
  return max(int(low), min(int(v), int(high)))