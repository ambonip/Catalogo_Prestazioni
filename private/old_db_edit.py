# aggiorno le date del db vecchio
from __future__ import print_function
from datetime import date, datetime, timedelta
import mysql.connector

conn = mysql.connector.connect(host='localhost', database='old_catalog', user='root', password='Ambo999', port='3306')
conn2 = mysql.connector.connect(host='localhost', database='tests_catalog', user='root', password='Ambo999',
                                port='3306')
cursor = conn.cursor()
cursor2 = conn2.cursor()

# cambio del fomato data del vecchio db
query = """
SELECT ID_analita,d_approvazione,d_pubblicazione FROM esami
"""
cursor.execute(query)
rows = cursor.fetchall()
for row in rows:
    data_approvazione = str(row[1])
    try:
        data_list = data_approvazione.split(r"/")
        update_query = """UPDATE esami SET d_revisione='{}-{}-{}' WHERE ID_Analita='{}'""".format(data_list[2],
                                                                                                  data_list[1],
                                                                                                  data_list[0], row[0])
        # print ("idanalita: {}, data approvazione:{}, data pubblicazione: {}, nuova data{}-{}-{}".format(row[0],row[1],row[2],data_list[2],data_list[1],data_list[0]))
        # print(update_query)
        try:
            cursor.execute(update_query)
            pass
        except:
            print(update_query)
    except:
        print('non aggiornabile: {}'.format(data_approvazione))

conn.commit()

# Aggiorno i campi booleani con T e F
query = " select ID_analita,Attivo,urgenza,routine,esterni,Prenotazione,Service,obsoleto from esami"
cursor.execute(query)
rows = cursor.fetchall()
for row in rows:
    data_num = list(row[1:])
    data = ['T' if x == 1 else 'F' for x in data_num]
    print(data)
    try:
        query2 = """update ignore tests_catalog.esami set
		attivo='{attivo}',
		eseguibile_urgenza='{urgenza}',
		eseguibile_routine='{routine}',
		eseguibile_esterni='{esterni}',
		prenotazione='{prenotazione}',
		service='{service}',
		obsoleto='{obsoleto}'
		where id={id_analita}
		""".format(attivo=data[0], urgenza=data[1], routine=data[2], esterni=data[3], prenotazione=data[4],
                   service=data[5], obsoleto=data[6], id_analita=row[0])
        cursor2.execute(query2)

    except:
        pass

conn2.commit()

# Aggiorno le date
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

cursor.close()
cursor2.close()
conn.close()
conn2.close()
