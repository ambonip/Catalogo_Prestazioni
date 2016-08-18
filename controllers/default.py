# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index():
    form = SQLFORM.factory(
        Field('Cerca_prestazione',
              requires=(IS_NOT_EMPTY(),
                        IS_LENGTH(minsize=3),
                        IS_SLUG(check=False, error_message='non deve contenere spazi o caratteri particolari'))),
        submit_button='cerca prestazione'
    )
    if form.process().accepted:
        redirect(URL('default', 'analisi_filtrate', vars=form.vars))

    return dict(message=T('Search test'), content=('Pagina di ricerca prestazioni'),
                title=('Catalogo delle prestazioni'), form=form)


def analisi_filtrate():
    # HIDE DB FIELDS
    db.esami.id.readable = False
    # QUERY THE DB
    query = (db.esami.analita.contains(request.vars.Cerca_prestazione) | db.esami.search_keywords.contains(
        request.vars.Cerca_prestazione))

    campi = [db.materiali.sigla, db.esami.id, db.esami.analita, db.materiali.materiale, db.esami.obsoleto]
    intestazione = {'esami.id': 'ID',
                    'esami.analita': 'Descrizione',
                    'esami.obsoleto': 'Non più eseguito',
                    'materiali.materiale': 'Materiale'
                    }
    # SORT ORDER
    ordinamento = [db.esami.analita]
    # lunghezza campi
    lunghezza = {'esami.analita': 60, 'esami.obsoleto': 5}
    # LINK OTHER TABLE
    left = db.esami.on(db.esami.id_materiali == db.materiali.id)
    # DISPLAY ADDITIONAL LINKS
    # links=[lambda row: A('Visualiza',_href=URL('default','scheda_esami',args=[row('esami.id')]),_class='btn btn-info')]
    links = [
        lambda row: A(T('Open'), _href=URL('default', 'scheda_esami', args=[row('esami.id')]), _class='btn btn-info')]
    # BULD THE GRID
    grid = SQLFORM.grid(query=query, left=left, fields=campi, headers=intestazione,
                        orderby=ordinamento, links=links,
                        create=False, deletable=False,
                        editable=False, details=False, paginate=20,
                        maxtextlength=lunghezza, csv=False,
                        links_placement='left'
                        , buttons_placement='both',
                        searchable=False
                        )
    return dict(lista=grid)


def view_container():
    # display container info  for external user
    id_contenitore = request.args(0)
    cont = db.contenitori[id_contenitore]
    return dict(cont=cont)

def adv_search():
    # grid for advanced search
    links = [
        lambda row: A(T('Open'), _href=URL('default', 'scheda_esami', args=[row('esami.id')]), _class='btn btn-info')]
    grid = SQLFORM.smartgrid(db.esami,
                             searchable=dict(parent=True, child=True),
                             #create=dict(parent=False, child=False),
                             #deletable=dict(parent=False, child=False),
                             #editable=dict(parent=False, child=False),
                             # details=dict(parent=False, child=False),
                             details=False,
                             create=False,
                             deletable=False,
                             editable=False,
                             paginate=50,
                             fields=(db.esami.id_materiali, db.esami.analita, db.esami.id_contenitore,
                                     db.esami.id_unitaoperativa, db.esami.obsoleto),
                             maxtextlengths={'esami.id_materiali': 8, 'esami.analita': 50, 'esami.id_contenitore': 60},
                             links=links

                             )
    return dict(grid=grid)


def scheda_esami():
    id_esame = request.args(0)
    anal = db.esami[id_esame]
    mat = db.materiali[anal.id_materiali]
    met = db.metodi[anal.id_metodo]
    sett = db.settori[anal.id_settore]
    cont = db.contenitori[anal.id_contenitore]
    uo = db.unitaoperativa[anal.id_unitaoperativa]
    return dict(anal=anal, mat=mat, met=met, sett=sett, cont=cont, uo=uo)

def scheda_esami_print():
    id_esame = request.args(0)
    anal = db.esami[id_esame]
    mat = db.materiali[anal.id_materiali]
    met = db.metodi[anal.id_metodo]
    sett = db.settori[anal.id_settore]
    cont = db.contenitori[anal.id_contenitore]
    uo = db.unitaoperativa[anal.id_unitaoperativa]
    return dict(anal=anal, mat=mat, met=met, sett=sett, cont=cont, uo=uo)




def license():
    return locals()


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

def fast_download():
   # very basic security (only allow fast_download on your_table.upload_field):
   if not request.args(0).startswith("yourtable.upload_field"):
       return download()
   # remove/add headers that prevent/favors client-side caching
   del response.headers['Cache-Control']
   del response.headers['Pragma']
   del response.headers['Expires']
   filename = os.path.join(request.folder,'uploads',request.args(0))
   # send last modified date/time so client browser can enable client-side caching
   response.headers['Last-Modified'] = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(os.path.getmtime(filename)))
   return response.stream(open(filename,'rb'))


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


def info():
    id = auth.user
    gr = auth.groups()  # [:1]
    uo = auth.user.id_unitaoperativa
    return locals()
