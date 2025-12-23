def select(table: str, columns: 'list | None' = None, **where): return (f'SELECT {"*" if columns is None or len(columns) <= 0 else ", ".join(columns)} FROM {table}' + where_clause(**where), (*flatten(*where.values()),))
def insert(table: str, **values): return (f'INSERT INTO {table} ({", ".join(values)}) VALUES ({", ".join("?" * len(values))})', (*values.values(),))
def update(table: str, where: 'dict | None' = None, returning: 'list | None' = None, **set): return (f'UPDATE {table}' + ((' SET ' + ", ".join(f"{key} = ?" for key in set)) if len(set) > 0 else '') + (where_clause(**where) if where is not None else '') + ((' RETURNING ' + (', '.join(key for key in returning) if len(returning) > 0 else '*')) if returning is not None else ''), (*set.values(), *(flatten(*where.values()) if where is not None else ())))
def delete(table: str, **where): return (f'DELETE FROM {table}' + where_clause(**where), (*flatten(*where.values()),))

def where_clause(**conditions): return (' WHERE ' + ' AND '.join(f'{key} {"IN" if type(value) in (list, tuple) else "="} {("(" + ", ".join("?" * len(value)) + ")") if type(value) in (list, tuple) else "?"}' for key, value in conditions.items())) if len(conditions) > 0 else ''
def flatten(*values): return [value for sub in values for value in (sub if type(sub) in (list, tuple) else [sub])]

if __name__ == '__main__': # Tests
    print(*select('users', ['id', 'name'], id=1, status='active'), sep=';    ')
    print(*insert('users', id=1, status='active'), sep=';    ')
    print(*update('users', {'id': 1, 'status': 'active'}, id=1, status='inactive'), sep=';    ')
    print(*delete('users', id=1, status='inactive'), sep=';    ')
    print(*select('users', ['id', 'name'], id=1, status=('active', 'inactive')), sep=';    ')
    print(*select('users', ['id', 'name'], id=1, country=('Indonesia', 'Malaysia', 'Singapore', 'Timor Leste')), sep=';    ')