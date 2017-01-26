# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

#response.logo = A(B('web',SPAN(2),'py'),XML('&trade;&nbsp;'),
#                  _class="navbar-brand",_href="http://www.web2py.com/",
#                  _id="web2py-logo")
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Paolo Amboni <paolo.amboni@gmail.com>'
response.meta.description = 'catalogo delle prestazioni di laboratorio'
response.meta.keywords = 'laboratorio, analisi, catalogo, prestazioni'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('Home'), False, URL('default', 'index'), []),
    (T('Advanced search'),False,URL('default','adv_search'),[])
]


# costruisco submenu per configurazione
sub_conf=[('Gestione Materiali',False,URL('gestione','mat')),
          ('Gestione contenitori',False,URL('gestione','cont')),
          ('Gestione metodi',False,URL('gestione','metod')),
          ('Gestione settori',False,URL('gestione','sett')),
          ('Gestione analisi',False,URL('gestione','lis_anal')),
         ]
#costruisco submenu per esportazione liste
sub_export=[('esporta analisi',False,URL('gestione','exp_anal')),
            ('esporta contenitori',False,URL('gestione','exp_cont')),
            ('esporta metodi',False,URL('gestione','exp_meto')),
            ('esporta materiali',False,URL('gestione','exp_mate')),
            ]
response.menu+=[('Esporta',False,'#',sub_export)]# aggancio il menù di esportazione
if auth.has_membership('superuser'):#aggiungo gestione unità operative solo per superuser
    sub_conf.append(('Unità operative',False,URL('gestione','unop')))
    sub_conf.append(('Configurazione generale',False,URL('gestione','gen_cfg')))
    response.menu+=[('Gestione utenti',False,URL('gestione','ges_user',[]))]

if auth.is_logged_in():#aggiungo i menù solo per utenti loggati
    response.menu+=[('Cofigurazione',False,'#',sub_conf)]#al menu configurzione aggancio il submenu preparato prima
    #response.menu+=[('Esporta',False,'#',sub_export)]# aggancio il menù di esportazione
#########################################################################
## provide shortcuts for development. remove in production
#########################################################################



if "auth" in locals(): auth.wikimenu()
