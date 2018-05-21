from psycopg2.extras import DictCursor, RealDictCursor

def fetch_geometry(db, layer, clip_poly):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        '''
            SELECT *
            FROM {table}
            WHERE ST_Intersects(
                geometry,
                ST_GeomFromText('{clip_poly}', 3857)
            ) AND ({filter});
        '''.format(
            table=layer.db_table,
            filter=layer.compile_filter(),
            clip_poly=clip_poly
        )
    )

    for result in cursor:
        yield result
