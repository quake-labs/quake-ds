from .DBQueries import *

create_comments = '''CREATE TABLE comments
                    (ID Serial PRIMARY KEY,
                    QuakeID int,
                    Source text,
                    name text,
                    comment text)'''

demo_comments = '''INSERT INTO comments
                (QuakeID, Source, Name, Comment)
                VALUES
                (0, 'USGS', 'Demo', 'This is a comment on quake 0')'''


def setup_comments():
    CONN = connect()
    curs = CONN.cursor()
    curs.execute('DROP TABLE IF EXISTS comments;')
    curs.execute(create_comments)
    curs.execute(demo_comments)
    curs.close()
    CONN.commit()
    CONN.close()


if __name__ == '__main__':
    setup_comments()
