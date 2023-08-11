from typing import List, Union, Literal, Any, Dict

from chromadb.types import WhereOperator, LiteralValue


class Where(object):
    query: Dict[str, Any]

    def __init__(self) -> None:
        self.query = {}

    def _add_condition(
        self,
        field: str,
        operator: Union[WhereOperator, Literal["$in"]],
        value: Union[LiteralValue, List[LiteralValue]],
    ) -> "Where":
        if field not in self.query:
            self.query[field] = {}
        self.query[field][operator] = value
        return self

    def gt(self, field: str, value: LiteralValue) -> "Where":
        return self._add_condition(field, "$gt", value)

    def gte(self, field: str, value: LiteralValue) -> "Where":
        return self._add_condition(field, "$gte", value)

    def lt(self, field: str, value: LiteralValue) -> "Where":
        return self._add_condition(field, "$lt", value)

    def lte(self, field: str, value: LiteralValue) -> "Where":
        return self._add_condition(field, "$lte", value)

    def ne(self, field: str, value: LiteralValue) -> "Where":
        return self._add_condition(field, "$ne", value)

    def eq(self, field: str, value: LiteralValue) -> "Where":
        return self._add_condition(field, "$eq", value)

    def in_(self, field: str, values: List[LiteralValue]) -> "Where":
        return self._add_condition(field, "$in", values)

    def and_(self, *conditions: "Where") -> "Where":
        if "$and" not in self.query:
            self.query["$and"] = []
        for condition in conditions:
            self.query["$and"].append(condition.query)
        return self

    def or_(self, *conditions: "Where") -> "Where":
        if "$or" not in self.query:
            self.query["$or"] = []
        for condition in conditions:
            self.query["$or"].append(condition.query)
        return self

    def get_query(self) -> Dict[str, Any]:
        return self.query


class WhereDocument(object):
    query: Dict[str, Any]

    def __init__(self) -> None:
        self.query = {}

    def contains(self, value: str) -> "WhereDocument":
        self.query["$contains"] = value
        return self

    def and_(self, *conditions: "WhereDocument") -> "WhereDocument":
        self.query["$and"] = [condition.query for condition in conditions]
        return self

    def or_(self, *conditions: "WhereDocument") -> "WhereDocument":
        self.query["$or"] = [condition.query for condition in conditions]
        return self

    def get_query(self) -> Dict[str, Any]:
        return self.query


# if __name__ == '__main__':
#     # Example usage
#     builder = (Where()
#                .gt("age", 21)
#                .eq("status", "active")
#                .in_("tags", ["admin", "user"])
#                .and_(Where().lt("score", 50), Where().ne("country", "US")))
#
#     print(builder.get_query())
