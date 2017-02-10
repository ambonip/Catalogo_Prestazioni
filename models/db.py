# -*- coding: utf-8 -*-

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)


if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL(myconf.take('db.uri'), pool_size=10, check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')


## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()


#departements
db.define_table('unitaoperativa',
                Field('descrizione','string',length=255,required=True,label=T('Description')),
                Field('responsabile','string',required=True,label=T('Director')),
                format='%(descrizione)s',
               )
db.unitaoperativa.descrizione.requires=IS_NOT_EMPTY()
db.unitaoperativa.descrizione.requires=IS_NOT_IN_DB(db,'unitaoperativa.descrizione')

#extra fields for users
auth.settings.extra_fields['auth_group']= [ Field('id_unitaoperativa','reference unitaoperativa'),]#departement
auth.settings.extra_fields['auth_user']= [ Field('id_unitaoperativa','reference unitaoperativa'),]#departement



## create all tables needed by auth if not custom tables
auth.define_tables(username=True, signature=False)
db.auth_user.id_unitaoperativa.readable=False
db.auth_user.id_unitaoperativa.writable=False

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.actions_disabled.append('register')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

# uploaded file handling
db.define_table('local_file',
                 Field('file_name','upload',required=True,autodelete=True),
                 Field('description','text',required=True),
                 Field('funct','string'),
                 Field('enabled','boolean'),
                 Field('tipo','list:string',required=True),
                )
db.local_file.tipo.requires=IS_IN_SET(('immagine','PDF','altro'))

#Tests materials
db.define_table('materiali',
                Field('materiale',required=True, label=T('Sample material')),
                Field('sigla',required=True, label=T('Initial')),
                Field('id_unitaoperativa','reference unitaoperativa'),
                auth.signature,
                format='%(sigla)s - ',
               )
db.materiali.materiale.reqires=IS_NOT_EMPTY()
db.materiali.sigla.reqires=IS_NOT_EMPTY()

# Tests methods
db.define_table('metodi',
                Field('metodo',required=True, label=T('Method')),
                Field('id_unitaoperativa','reference unitaoperativa'),
                auth.signature,
                format='%(metodo)s'
                )
db.metodi.metodo.requres=IS_NOT_EMPTY()

#Containers
db.define_table('contenitori',
                Field('contenitore',required=True, label=T('Container')),
                Field('nota','text',label='nota'),
                Field('cod_ord',label='Codice magazzino'),
                Field('immagine','upload',autodelete=True, label=T('Image')),
                Field('id_unitaoperativa','reference unitaoperativa'),
                auth.signature,
                format='%(contenitore)s'
                )
db.contenitori.contenitore.requires=IS_NOT_EMPTY()
db.contenitori.immagine.requires=IS_EMPTY_OR(IS_IMAGE(maxsize=(300,300)))

#Departements units
db.define_table('settori',
                Field('settore',required=True, label=T('Area')),
                Field('responsabile', label=T('Director')),
                Field('sos_responsabile', label=T('Director substitute')),
                Field('telefono', label=T('Phone number')),
                Field('mail',requires = IS_EMAIL(error_message='email non valida')),
                Field('id_unitaoperativa','reference unitaoperativa'),
                format='%(settore)s'
                )
db.settori.settore.requires=IS_NOT_EMPTY()

#tests
db.define_table('esami',
                Field('analita',required=True,label=T('Description')),
                Field('search_keywords',required=True,label=T('Search keyword')),
                Field('attivo','boolean',required=True,default=False,label=T('Enable full view')),
                Field('id_unitaoperativa','reference unitaoperativa',required=True,label='Unità operativa'),
                Field('id_materiali','reference materiali',required=True,label='Materiale'),
                Field('id_contenitore','reference contenitori',required=True,label='Contenitore'),
                Field('id_metodo','reference metodi',required=True,label='Metodo'),
                Field('id_settore','reference settori',required=True,label='Settore'),
                Field('codice_metafora',label='Cocice analisi in concerto'),
                Field('codice_DM',label='Codice Nomenclatore Aziendale'),
                Field('tariffa_DM',label='Tariffa DM'),
                #
                Field('eseguibile_urgenza','boolean',default=False,label='Esame eseguibile in urgenza'),
                Field('eseguibile_routine','boolean',default=True,label='Esame eseguibile in routine'),
                Field('eseguibile_esterni','boolean',default=False,label='Esame eseguibile per esterni'),
                Field('prenotazione','boolean',default=False,label='Prenotazione necessaria'),
                Field('service','boolean',default=False,required=True,label='In service'),
                Field('obsoleto','boolean',default=False,required=True,label='Non più eseguito'),
                #
                Field('preparazione_paziente','text',label='Preparazione del paziente'),
                Field('moduli_richiesta','upload',autodelete=True,label='Modulo di richiesta PDF'),
                Field('raccolta','text',label='Modalità di raccolta'),
                Field('volume_minimo',label='Volume minimo'),
                Field('trasporto','text',label='Modalità di trasporto'),
                #
                Field('unita_misura',label='Unità di misura'),
                Field('riferimento','text',label='Valori di riferimento'),
                Field('interpretazione','text'),
                Field('interferenze','text'),
                Field('giorni_effettuazione',label='Giorni di effettuazione'),
                Field('udm_tempo_attesa',label='Unità di misura per tempo di refertazione (giorni, ore ..)'),
                Field('tempo_refertazione',label='Tempo di refertaznione in routine'),
                Field('tempo_refertazione_urgenza',label='Tempo di refertazione in urgenza min.'),
                Field('conservazione','text',label='Modalità di conservazione'),
                #
                Field('veq', 'text', label='Veq eseguite'),
                Field('note','text'),
                Field('numero_revisione', label='Numero di revisone', default='0'),
                auth.signature,
                format='%(analita)s',
                )
db.esami.analita.requires=IS_NOT_EMPTY()
db.esami.id_materiali.requires=IS_NOT_EMPTY()
db.esami.id_materiali.requires=IS_IN_DB(db,db.materiali.id,'%(sigla)s - %(materiale)s')
db.esami.id_contenitore.requires=IS_NOT_EMPTY()
db.esami.id_contenitore.requires=IS_IN_DB(db,db.contenitori.id,'%(contenitore)s')
db.esami.id_metodo.requires=IS_NOT_EMPTY()
db.esami.id_metodo.requires=IS_IN_DB(db,db.metodi.id,'%(metodo)s')
db.esami.id_settore.requires=IS_NOT_EMPTY()
db.esami.id_settore.requires=IS_IN_DB(db,db.settori.id,'%(settore)s')
db.esami.id_unitaoperativa.requires=IS_NOT_EMPTY()
db.esami.id_unitaoperativa.requires=IS_IN_DB(db,db.unitaoperativa.id,'%(descrizione)s')
db.esami.search_keywords.requires=IS_NOT_EMPTY()
db.esami.moduli_richiesta.requires= IS_EMPTY_OR(IS_UPLOAD_FILENAME(extension='pdf'))
db.esami.codice_metafora.requires= IS_NOT_EMPTY()

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
