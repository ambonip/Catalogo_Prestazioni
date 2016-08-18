# Aggiorno le date
# aggiorno le date del db vecchio
from __future__ import print_function
from datetime import date, datetime, timedelta
import mysql.connector

conn = mysql.connector.connect(host='localhost', database='old_catalog', user='root', password='Ambo999', port='3306')
conn2 = mysql.connector.connect(host='localhost', database='tests_catalog', user='root', password='Ambo999',
                                port='3306')
cursor = conn.cursor()
cursor2 = conn2.cursor()

query = " select ID_analita,d_revisione from esami"
cursor.execute(query)
rows = cursor.fetchall()
for row in rows:
    query2 = """update ignore tests_catalog.esami set
		modified_on='{data_mod}' where id={id}""".format(data_mod=row[1], id=row[0])
    try:
        cursor2.execute(query2)
    except:
        print(query2)
conn2.commit()