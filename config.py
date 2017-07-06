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

""" Holds configuration settings.
"""


PRODUCT_INDEX_NAME = 'productsearch1'  # The document index name.
    # An index name must be a visible printable
    # ASCII string not starting with '!'. Whitespace characters are
    # excluded.

STORE_INDEX_NAME = 'stores1'



# the number of search results to display per page
DOC_LIMIT = 3

SAMPLE_DATA_SMARTPHONE = 'sample_data_smartphone.csv'
SAMPLE_DATA_LAPTOP = 'sample_data_laptop.csv'
UPDATE_PHONE_DATA = 'sample_data_phone_update.csv'
UPDATE_LAPTOP_DATA = 'sample_data_laptop_update.csv'


