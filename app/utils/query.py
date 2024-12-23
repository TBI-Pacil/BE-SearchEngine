import re


class QueryProcessor:
    def __init__(self):
        self.regex = '[^\w\s]'

    def preprocessed_query(self, query: str) -> str:
        return re.sub(self.regex, '', query)
