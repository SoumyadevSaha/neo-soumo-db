import re
import csv
from io import StringIO
from datastore import DataStore

class QueryProcessor:
    AGG_REGEX = re.compile(
        r"(SUM|AVG|COUNT|MIN|MAX)\((\w+)\)(?:\s+AS\s+(\w+))?", re.IGNORECASE
    )
    CLAUSE_ORDER = ['WHERE', 'GROUP BY', 'ORDER BY', 'LIMIT', 'OFFSET']

    def __init__(self):
        self.store = DataStore()

    def process(self, query):
        try:
            query = query.strip().rstrip(';')
            if not query:
                raise ValueError("Empty query")
            cmd = query.split()[0].upper()
            handler = getattr(self, f"_{cmd.lower()}", None)
            if not handler:
                raise ValueError(f"Unsupported command: {cmd}")
            return handler(query)
        except Exception as e:
            return {'error': str(e)}

    def _parse_value(self, value):
        value = value.strip()
        if value.lower() == 'null':
            return None
        for parser in [int, float]:
            try:
                return parser(value)
            except ValueError:
                continue
        return value.strip(" '\"")

    def _parse_sets(self, set_clause):
        sets = {}
        reader = csv.reader(StringIO(set_clause), quotechar="'", delimiter=',')
        for part in next(reader, []):
            part = part.strip()
            if not part:
                continue
            try:
                col, val = part.split('=', 1)
                sets[col.strip().lower()] = self._parse_value(val)
            except ValueError:
                raise ValueError(f"Invalid SET clause: {part}")
        return sets

    def _create(self, q):
        match = re.match(r"CREATE TABLE (\w+)\s*\((.*?)\)", q, re.I)
        if not match:
            raise ValueError("Invalid CREATE TABLE syntax")
        name, cols = match.groups()
        self.store.create_table(name, [c.strip() for c in cols.split(',')])
        return {'message': f"Table {name} created"}

    def _insert(self, q):
        match = re.match(r"INSERT INTO (\w+)\s*\((.+?)\)\s+VALUES\s*\((.+?)\)", q, re.I)
        if not match:
            raise ValueError("Invalid INSERT syntax")
        table, cols, vals = match.groups()
        
        # Parse values with CSV reader
        vals = next(csv.reader(StringIO(vals), []))
        parsed_vals = [self._parse_value(v) for v in vals]
        
        self.store.insert(
            table,
            [c.strip().lower() for c in cols.split(',')],
            parsed_vals
        )
        return {'message': f"Inserted 1 row into {table}"}

    def _select(self, q):
        # Extract main clauses
        clauses = re.split(r'(\bWHERE\b|\bGROUP BY\b|\bORDER BY\b|\bLIMIT\b|\bOFFSET\b)', q, flags=re.I)
        parts = [part.strip() for part in clauses if part.strip()]
        
        # Parse components
        select_part = parts[0]
        components = {'base': parts[0]}
        current_clause = None
        for part in parts[1:]:
            if part.upper() in self.CLAUSE_ORDER:
                current_clause = part.upper()
                components[current_clause] = []
            elif current_clause:
                components[current_clause].append(part)
        
        # Parse SELECT columns
        cols_part = select_part.split('FROM', 1)[0].replace('SELECT', '', 1).strip()
        cols = []
        aggs = {}
        for col in cols_part.split(','):
            col = col.strip()
            if col == '*':
                cols = ['*']
                break
            match = self.AGG_REGEX.match(col)
            if match:
                func, col, alias = match.groups()
                alias = alias or f"{func.lower()}_{col}"
                aggs[alias] = (func.upper(), col.lower())
            else:
                cols.append(col.lower())
        
        # Build query parameters
        params = {
            'where': ' '.join(components.get('WHERE', [])),
            'group_by': ' '.join(components.get('GROUP BY', [])).lower(),
            'order_by': None,
            'limit': None,
            'offset': None,
            'aggs': aggs or None
        }
        
        # Handle ORDER BY
        if 'ORDER BY' in components:
            order_parts = ' '.join(components['ORDER BY']).split()
            params['order_by'] = (
                order_parts[0].lower(),
                order_parts[1].upper() if len(order_parts) > 1 else 'ASC'
            )
        
        # Handle LIMIT/OFFSET
        if 'LIMIT' in components:
            params['limit'] = int(components['LIMIT'][0])
        if 'OFFSET' in components:
            params['offset'] = int(components['OFFSET'][0])
        
        table = re.search(r'FROM (\w+)', select_part, re.I).group(1)
        result = self.store.select(table, cols, **params)
        return {'data': result}

    def _update(self, q):
        match = re.match(r"UPDATE (\w+) SET (.+?)(?: WHERE (.+))?", q, re.I)
        if not match:
            raise ValueError("Invalid UPDATE syntax")
        table, set_clause, where = match.groups()
        updated = self.store.update(table, self._parse_sets(set_clause), where)
        return {'message': f"Updated {updated} rows"}

    def _delete(self, q):
        match = re.match(r"DELETE FROM (\w+)(?: WHERE (.+))?", q, re.I)
        if not match:
            raise ValueError("Invalid DELETE syntax")
        table, where = match.groups()
        deleted = self.store.delete(table, where)
        return {'message': f"Deleted {deleted} rows"}