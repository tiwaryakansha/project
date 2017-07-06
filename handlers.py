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

"""Contains the non-admin ('user-facing') request handlers for the app."""


import logging
import urllib
import wsgiref

from base_handler import BaseHandler
import config
import docs
import models
import utils

from google.appengine.api import search
from google.appengine.api import users
from google.appengine.ext.deferred import defer
from google.appengine.ext import ndb


class IndexHandler(BaseHandler):
  """Displays the 'home' page."""

  def get(self):
    cat_info = models.Category.getCategoryInfo()
    sort_info = docs.Product.getSortMenu()
    template_values = {
        'cat_info': cat_info,
        'sort_info': sort_info,
    }
    self.render_template('index.html', template_values)


class ShowProductHandler(BaseHandler):
  """Display product details."""

  def parseParams(self):
    """Filter the param set to the expected params."""
    # The dict can be modified to add any defined defaults.

    params = {
        'pid': '',
        'pname': '',
        'category': ''
    }
    for k, v in params.iteritems():
      # Possibly replace default values.
      params[k] = self.request.get(k, v)
    return params

  def get(self):
    """Do a document search for the given product id,
    and display the retrieved document fields."""

    params = self.parseParams()

    pid = params['pid']
    if not pid:
      # we should not reach this
      msg = 'Error: do not have product id.'
      url = '/'
      linktext = 'Go to product search page.'
      self.render_template(
          'notification.html',
          {'title': 'Error', 'msg': msg,
           'goto_url': url, 'linktext': linktext})
      return
    doc = docs.Product.getDocFromPid(pid)
    if not doc:
      error_message = ('Document not found for pid %s.' % pid)
      return self.abort(404, error_message)
      logging.error(error_message)
    pdoc = docs.Product(doc)
    pname = pdoc.getName()
    app_url = wsgiref.util.application_uri(self.request.environ)
    #rlink = '/reviews?' + urllib.urlencode({'pid': pid, 'pname': pname})
    template_values = {
        'app_url': app_url,
        'pid': pid,
        'pname': pname,
        #'review_link': rlink,
        #'comment': params['comment'],
        #'rating': params['rating'],
        'category': pdoc.getCategory(),
        'prod_doc': doc,
        # for this demo, 'admin' status simply equates to being logged in
        'user_is_admin': users.get_current_user()}
    self.render_template('product.html', template_values)





class ProductSearchHandler(BaseHandler):
  """The handler for doing a product search."""

  _DEFAULT_DOC_LIMIT = 3  #default number of search results to display per page.
  _OFFSET_LIMIT = 1000

  def parseParams(self):
    """Filter the param set to the expected params."""
    params = {
        'qtype': '',
        'query': '',
        'category': '',
        'sort': '',
        'offset': '0'
    }
    for k, v in params.iteritems():
      # Possibly replace default values.
      params[k] = self.request.get(k, v)
    return params

  def post(self):
    params = self.parseParams()
    self.redirect('/psearch?' + urllib.urlencode(
        dict([k, v.encode('utf-8')] for k, v in params.items())))

  def _getDocLimit(self):
    """if the doc limit is not set in the config file, use the default."""
    doc_limit = self._DEFAULT_DOC_LIMIT
    try:
      doc_limit = int(config.DOC_LIMIT)
    except ValueError:
      logging.error('DOC_LIMIT not properly set in config file; using default.')
    return doc_limit

  def get(self):
    """Handle a product search request."""

    params = self.parseParams()
    self.doProductSearch(params)

  def doProductSearch(self, params):
    """Perform a product search and display the results."""

    # the defined product categories
    cat_info = models.Category.getCategoryInfo()
    # the product fields that we can sort on from the UI, and their mappings to
    # search.SortExpression parameters
    sort_info = docs.Product.getSortMenu()
    sort_dict = docs.Product.getSortDict()
    query = params.get('query', '')
    user_query = query
    doc_limit = self._getDocLimit()

    categoryq = params.get('category')
    if categoryq:
      # add specification of the category to the query
      # Because the category field is atomic, put the category string
      # in quotes for the search.
      query += ' %s:"%s"' % (docs.Product.CATEGORY, categoryq)

    sortq = params.get('sort')
    try:
      offsetval = int(params.get('offset', 0))
    except ValueError:
      offsetval = 0

    

    # cat_name = models.Category.getCategoryName(categoryq)
    psearch_response = []
    # For each document returned from the search
    for doc in search_results:
      # logging.info("doc: %s ", doc)
      pdoc = docs.Product(doc)
      # use the description field as the default description snippet, since
      # snippeting is not supported on the dev app server.
      description_snippet = pdoc.getDescription()
      price = pdoc.getPrice()
      # on the dev app server, the doc.expressions property won't be populated.
      for expr in doc.expressions:
        if expr.name == docs.Product.DESCRIPTION:
          description_snippet = expr.value
        # uncomment to use 'adjusted price', which should be
        # defined in returned_expressions in _buildQuery() below, as the
        # displayed price.
        # elif expr.name == 'adjusted_price':
          # price = expr.value

      # get field information from the returned doc
      pid = pdoc.getPID()
      cat = catname = pdoc.getCategory()
      pname = pdoc.getName()
      #avg_rating = pdoc.getAvgRating()
      # for this result, generate a result array of selected doc fields, to
      # pass to the template renderer
      psearch_response.append(
          [doc, urllib.quote_plus(pid), cat,
           description_snippet, price, pname, catname])
    if not query:
      print_query = 'All'
    else:
      print_query = query

    # Build the next/previous pagination links for the result set.
    (prev_link, next_link) = self._generatePaginationLinks(
        offsetval, returned_count,
        search_results.number_found, params)

    logging.debug('returned_count: %s', returned_count)
    # construct the template values
    template_values = {
        'base_pquery': user_query, 'next_link': next_link,
        'prev_link': prev_link, 'qtype': 'product',
        'query': query, 'print_query': print_query,
        'pcategory': categoryq, 'sort_order': sortq, 'category_name': categoryq,
        'first_res': offsetval + 1, 'last_res': offsetval + returned_count,
        'returned_count': returned_count,
        'number_found': search_results.number_found,
        'search_response': psearch_response,
        'cat_info': cat_info, 'sort_info': sort_info}
    # render the result page.
    self.render_template('index.html', template_values)

  def _buildQuery(self, query, sortq, sort_dict, doc_limit, offsetval):
    """Build and return a search query object."""

    # computed and returned fields examples.  Their use is not required
    # for the application to function correctly.
    computed_expr = search.FieldExpression(name='adjusted_price',
        expression='price * 1.08')
    returned_fields = [docs.Product.PID, docs.Product.DESCRIPTION,
                docs.Product.CATEGORY,docs.Product.PRICE, docs.Product.PRODUCT_NAME]

    if sortq == 'relevance':
      # If sorting on 'relevance', use the Match scorer.
      sortopts = search.SortOptions(match_scorer=search.MatchScorer())
      search_query = search.Query(
          query_string=query.strip(),
          options=search.QueryOptions(
              limit=doc_limit,
              offset=offsetval,
              sort_options=sortopts,
              snippeted_fields=[docs.Product.DESCRIPTION],
              returned_expressions=[computed_expr],
              returned_fields=returned_fields
              ))
    """else:
      # Otherwise (not sorting on relevance), use the selected field as the
      # first dimension of the sort expression, and the average rating as the
      # second dimension, unless we're sorting on rating, in which case price
      # is the second sort dimension.
      # We get the sort direction and default from the 'sort_dict' var.
      if sortq == docs.Product.AVG_RATING:
        expr_list = [sort_dict.get(sortq), sort_dict.get(docs.Product.PRICE)]
      else:
        expr_list = [sort_dict.get(sortq), sort_dict.get(
              docs.Product.AVG_RATING)]
      sortopts = search.SortOptions(expressions=expr_list)
      # logging.info("sortopts: %s", sortopts)
      search_query = search.Query(
          query_string=query.strip(),
          options=search.QueryOptions(
              limit=doc_limit,
              offset=offsetval,
              sort_options=sortopts,
              snippeted_fields=[docs.Product.DESCRIPTION],
              returned_expressions=[computed_expr],
              returned_fields=returned_fields
              ))"""
    return search_query

  

  def _generatePaginationLinks(
        self, offsetval, returned_count, number_found, params):
    """Generate the next/prev pagination links for the query.  Detect when we're
    out of results in a given direction and don't generate the link in that
    case."""

    doc_limit = self._getDocLimit()
    pcopy = params.copy()
    if offsetval - doc_limit >= 0:
      pcopy['offset'] = offsetval - doc_limit
      prev_link = '/psearch?' + urllib.urlencode(pcopy)
    else:
      prev_link = None
    if ((offsetval + doc_limit <= self._OFFSET_LIMIT)
        and (returned_count == doc_limit)
        and (offsetval + returned_count < number_found)):
      pcopy['offset'] = offsetval + doc_limit
      next_link = '/psearch?' + urllib.urlencode(pcopy)
    else:
      next_link = None
    return (prev_link, next_link)



class StoreLocationHandler(BaseHandler):
  """Show the reviews for a given product.  This information is pulled from the
  datastore Review entities."""

  def get(self):
    """Show a list of reviews for the product indicated by the 'pid' request
    parameter."""

    query = self.request.get('location_query')
    lat = self.request.get('latitude')
    lon = self.request.get('longitude')
    # the location query from the client will have this form:
    # distance(store_location, geopoint(37.7899528, -122.3908226)) < 40000
    # logging.info('location query: %s, lat %s, lon %s', query, lat, lon)
    try:
      index = search.Index(config.STORE_INDEX_NAME)
      # search using simply the query string:
      # results = index.search(query)
      # alternately: sort results by distance
      loc_expr = 'distance(store_location, geopoint(%s, %s))' % (lat, lon)
      sortexpr = search.SortExpression(
            expression=loc_expr,
            direction=search.SortExpression.ASCENDING, default_value=0)
      sortopts = search.SortOptions(expressions=[sortexpr])
      search_query = search.Query(
          query_string=query.strip(),
          options=search.QueryOptions(
              sort_options=sortopts,
              ))
      results = index.search(search_query)
    except search.Error:
      logging.exception("There was a search error:")
      self.render_json([])
      return
    # logging.info("geo search results: %s", results)
    response_obj2 = []
    for res in results:
      gdoc = docs.Store(res)
      geopoint = gdoc.getFieldVal(gdoc.STORE_LOCATION)
      resp = {'addr': gdoc.getFieldVal(gdoc.STORE_ADDRESS),
              'storename': gdoc.getFieldVal(gdoc.STORE_NAME),
              'lat': geopoint.latitude, 'lon': geopoint.longitude}
      response_obj2.append(resp)
    logging.info("resp: %s", response_obj2)
    self.render_json(response_obj2)
