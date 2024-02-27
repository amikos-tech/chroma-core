import csv
import json
import time


def apply_filter(entries, filter_query):
    """Filters a list of entries based on the provided filter query."""

    def condition(entry, query):
        """Evaluates if an entry meets the condition specified in query."""
        for key, value in query.items():
            if key in entry:
                if isinstance(value, dict):  # Handle operators
                    for operator, operand in value.items():
                        if operator == "$eq" and entry[key] != operand:
                            return False
                        elif operator == "$ne" and entry[key] == operand:
                            return False
                        elif operator == "$lt" and entry[key] >= operand:
                            return False
                        elif operator == "$lte" and entry[key] > operand:
                            return False
                        elif operator == "$gt" and entry[key] <= operand:
                            return False
                        elif operator == "$gte" and entry[key] < operand:
                            return False
                elif entry[key] != value:  # Simple key-value equality check
                    return False
            elif key == "$or":  # Handle $or separately
                if not any(condition(entry, sub_query) for sub_query in value):
                    return False
            else:
                return False
        return True

    def match(entry, conditions):
        """Checks if an entry matches all conditions."""
        for cond in conditions:
            if not condition(entry, cond):
                return False
        return True

    filtered_entries = [entry for entry in entries if match(entry, filter_query["$and"])]
    return filtered_entries




def apply_filter_v2(single_entry, filter_query):
    """Takes in single dictionary and filter query and returns True if the entry meets the condition."""

    def condition(entry:dict, query):
        """Evaluates if an entry meets the condition specified in query."""
        for key, value in query.items():
            if key in entry:
                if isinstance(value, dict):  # Handle operators
                    for operator, operand in value.items():
                        if operator == "$eq" and entry[key] != operand:
                            return False
                        elif operator == "$ne" and entry[key] == operand:
                            return False
                        elif operator == "$lt" and entry[key] >= operand:
                            return False
                        elif operator == "$lte" and entry[key] > operand:
                            return False
                        elif operator == "$gt" and entry[key] <= operand:
                            return False
                        elif operator == "$gte" and entry[key] < operand:
                            return False
                elif entry[key] != value:  # Simple key-value equality check
                    return False
            elif key == "$or":  # Handle $or separately
                if not any(condition(entry, sub_query) for sub_query in value):
                    return False
            elif key == "$and":  # Handle $and separately
                if not all(condition(entry, sub_query) for sub_query in value):
                    return False
            else:
                return False
        return True

    def match(entry, conditions):
        """Checks if an entry matches all conditions."""
        for cond in conditions:
            if not condition(entry, cond):
                return False
        return True
    return condition(single_entry, filter_query)


# Example usage
your_filter = {"$and": [{"category": "chroma"}, {"$or": [{"author": {"$eq": "john"}}, {"author": "jack"}]}]}
entries = [
    {"category": "chroma", "author": "john", "title": "Example 1"},
    {"category": "other", "author": "jack", "title": "Example 2"},
    {"category": "chroma", "author": "jane", "title": "Example 3"},
    {"category": "chroma", "author": "jack", "title": "Example 4"},
]


def read_file(filename: str):
    # Assuming your CSV file is named 'data.csv' and uses '|' as delimiter

    # Open the file and parse each line
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='|')

        for row in reader:
            # Assuming the JSON string is in the last column
            json_str = row[-1]

            try:
                # Parse the JSON string
                json_data = json.loads(json_str)
            except json.JSONDecodeError:
                # Handle the error
                # print(f'Error parsing JSON: {row}')
                continue

            # Now json_data holds the parsed JSON object
            # You can process it here as needed
            yield json_data

q ={"$and":[{"rand":{"$gte": 501}},{"rand":{"$lte": 502}}]}
# filtered_items = filter(lambda x: apply_filter_v2(x, q), read_file('exp-direct-filter.txt'))
items = []
start_time = time.perf_counter()
for entry in read_file('exp-direct-filter.txt'):
    if apply_filter_v2(entry, q):
        items.append(entry)
print(len(items))
print(f"Time taken: {time.perf_counter() - start_time} seconds")
# print(apply_filter(entries, your_filter))
