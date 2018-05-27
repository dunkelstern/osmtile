import datetime
from psycopg2.extras import DictCursor, RealDictCursor

def fetch_geometry(db, layer, clip_poly):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    sql = '''
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

    # print(sql)
    start = datetime.datetime.now()
    cursor.execute(sql)
    end = datetime.datetime.now()
    print(" -> Query for {} took {} ms".format(layer.name, (end - start).total_seconds() * 1000.0))

    for result in cursor:
        yield result
