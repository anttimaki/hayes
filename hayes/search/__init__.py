# -- encoding: UTF-8 --
from collections import defaultdict
from hayes.search.queries import FilteredQuery
from hayes.utils import object_to_dict


class Search(object):
	def __init__(self, query, filter=None, fields=None, sort=None):
		# XXX: facets?
		self.query = query
		self.filter = filter
		self.fields = fields
		self.sort = sort

	def to_dict(self):
		res = {}

		if self.filter:
			query = FilteredQuery(self.query, self.filter)
		else:
			query = self.query

		res["query"] = object_to_dict(query)

		if self.fields is not None:
			res['fields'] = self.fields

		if self.sort:
			res['sort'] = self.sort

		return res


class SearchResult(dict):
	def __init__(self, obj):
		source = obj.pop("_source", None)
		fields = obj.pop("fields", None)
		super(SearchResult, self).__init__(obj)
		if source:
			self.update(source)
		if fields:
			self.update(fields)


class SearchResults(object):
	def __init__(self, search, raw_result, start, count):
		self.search = search
		self.raw_result = raw_result
		self.start = start
		self.count = count
		self.took = int(raw_result["took"])
		hit_data = raw_result["hits"]
		self.hits = [SearchResult(res) for res in hit_data["hits"]]
		self.total = int(hit_data["total"])
		if self.total > 0:
			self.page_no = int(self.start / self.count)
			self.n_pages = int(self.count / self.total)
		else:
			self.page_no = self.n_pages = 0
		self.by_type = defaultdict(list)
		for hit in self.hits:
			self.by_type[hit.get("_type")].append(hit)
		self.by_type = dict(self.by_type.iteritems())