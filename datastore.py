import re
from collections import defaultdict

class Table:
    def __init__(self, columns):
        self.columns = [c.lower() for c in columns]  # Case-insensitive columns
        self.rows = []

class DataStore:
    def __init__(self):
        self.tables = {}

    def create_table(self, name, cols):
        if name in self.tables:
            raise ValueError(f"Table '{name}' already exists")
        self.tables[name] = Table([c.lower() for c in cols])

    def insert(self, table, cols, vals):
        tbl = self.tables.get(table)
        if not tbl:
            raise ValueError(f"Table '{table}' not found")
        cols = [c.lower() for c in cols]
        invalid_cols = [c for c in cols if c not in tbl.columns]
        if invalid_cols:
            raise ValueError(f"Invalid columns: {invalid_cols}")
        if len(cols) != len(vals):
            raise ValueError("Column/value count mismatch")
        row = {k: v for k, v in zip(cols, vals)}
        row.update({c: None for c in tbl.columns if c not in row})
        tbl.rows.append(row)

    def _parse_where(self, where_clause):
        if not where_clause:
            return None, None, None
        pattern = r"(\w+)\s*(=|!=|>|<|>=|<=|LIKE)\s*(.+)"
        m = re.match(pattern, where_clause, re.I)
        if not m:
            raise ValueError(f"Invalid WHERE clause: {where_clause}")
        col, op, val = m.groups()
        return col.lower(), op.upper(), val.strip(" '\"")

    def _apply_where(self, rows, where_clause, table_columns):
        if not where_clause:
            return rows
        col, op, val = self._parse_where(where_clause)
        if col not in table_columns:
            raise ValueError(f"Invalid column '{col}' in WHERE clause")
        
        # Value conversion
        try:
            val = int(val)
        except ValueError:
            try:
                val = float(val)
            except ValueError:
                pass

        # Operation mapping
        ops = {
            '=': lambda a, b: a == b,
            '!=': lambda a, b: a != b,
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
            'LIKE': lambda a, b: re.match(b.replace('%', '.*'), str(a))
        }
        return [r for r in rows if ops[op](r.get(col), val)]

    def select(self, table, cols, where=None, order_by=None, group_by=None, aggs=None, limit=None, offset=None):
        tbl = self.tables.get(table)
        if not tbl:
            raise ValueError(f"Table '{table}' not found")
        
        # Filter rows
        rows = self._apply_where(tbl.rows, where, tbl.columns)
        
        # Grouping and aggregation
        if group_by or aggs:
            grouped = defaultdict(list)
            key_col = group_by.lower() if group_by else None
            for r in rows:
                key = r.get(key_col, '') if key_col else '_all'
                grouped[key].append(r)
            
            agg_results = []
            for key, group in grouped.items():
                res = {}
                if group_by:
                    res[group_by] = key
                for alias, (func, col) in (aggs or {}).items():
                    values = [g[col] for g in group if g[col] is not None]
                    if func == 'COUNT':
                        res[alias] = len(values)
                    elif func == 'SUM':
                        res[alias] = sum(values) if values else 0
                    elif func == 'AVG':
                        res[alias] = sum(values)/len(values) if values else None
                    elif func == 'MIN':
                        res[alias] = min(values) if values else None
                    elif func == 'MAX':
                        res[alias] = max(values) if values else None
                agg_results.append(res)
            rows = agg_results

        # Sorting
        if order_by:
            col, direction = order_by
            reverse = direction.upper() == 'DESC'
            rows = sorted(rows, key=lambda x: x.get(col.lower()), reverse=reverse)

        # Pagination
        if offset:
            rows = rows[offset:]
        if limit:
            rows = rows[:limit]

        # Projection
        if cols == ['*']:
            return rows
        return [{c.lower(): r.get(c.lower()) for c in cols} for r in rows]

    def update(self, table, sets, where=None):
        tbl = self.tables.get(table)
        if not tbl:
            raise ValueError(f"Table '{table}' not found")
        sets = {k.lower(): v for k, v in sets.items()}
        invalid_cols = [c for c in sets if c not in tbl.columns]
        if invalid_cols:
            raise ValueError(f"Invalid columns: {invalid_cols}")
        rows = self._apply_where(tbl.rows, where, tbl.columns)
        for row in rows:
            row.update(sets)
        return len(rows)

    def delete(self, table, where=None):
        tbl = self.tables.get(table)
        if not tbl:
            raise ValueError(f"Table '{table}' not found")
        original_count = len(tbl.rows)
        tbl.rows = [r for r in tbl.rows if not self._apply_where([r], where, tbl.columns)]
        return original_count - len(tbl.rows)