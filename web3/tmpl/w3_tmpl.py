def head():
    '''head for html head '''
    head = '''
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/> 
        <link href="/css/basic.css" rel="stylesheet" type="text/css" />
<!--
        <link href="/js/jquery-ui-1.8.23.custom/css/smoothness/jquery-ui-1.8.23.custom.css" rel="stylesheet" type="text/css" />
-->

        <script src="/app/www/javascript/framework/underscore-min.js" type="text/javascript"> </script>
        <script src="/app/www/javascript/framework/backbone-min.js" type="text/javascript"> </script>
        <script src="/app/www/javascript/framework/jquery.min.js" type="text/javascript"> </script>

<!--
        <script src="/js/jquery-ui-1.8.23.custom/js/jquery-ui-1.8.23.custom.min.js" type="text/javascript"> </script>

        <script src="/js/jquery.form.js" type="text/javascript"></script>
        <script src="/js/jquery.validate.js" type="text/javascript"></script>
-->

    '''
    cdn ='''
    <script src ="//underscorejs.org/underscore-min.js" type="text/javascript"></script>
    <script src ="//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js" type ="text/javascript"></script>
    <script src ="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/jquery-ui.min.js"></script>
    <script src ="//ajax.googleapis.com/ajax/libs/swfobject/2.2/swfobject.js"></script>
    '''

    return head


def header():
    '''header for page'''
    header = \
    '''
    '''
    return header

def footer():
    footer = '''
        <!--[if IE 6]>
        <script src="//letskillie6.googlecode.com/svn/trunk/2/zh_CN.js" defer=true></script>
        <![endif]-->
        '''
    return footer

def nav(remote_user_name:str=None, remote_user:str=None, remote_role:str=None, remote_user_id:int=None, remote_role_id:int=None):
    '''nav menu for role '''

    menu = ""

    menu_externaluser = \
        '''
        '''
    menu_internaluser = \
        '''
        '''

    menu_poweruser = \
        '''
        '''
    menu_superuser = \
        '''
          <!--
          <li><a href="#"             title=""         >su1</a></li>
          <li><a href="#"             title=""         >su2</a></li>
          <li><a href="#"             title=""         >su3</a></li>
          -->
        '''



    if remote_role in ('externaluser', ):
        menu = "{}{}".format(menu, menu_externaluser)

    if remote_role in ('internaluser', ):
        menu = "{}{}{}".format(menu, menu_externaluser, menu_internaluser)

    if remote_role in ('poweruser', ):
        menu = "{}{}{}{}".format(menu, menu_externaluser, menu_internaluser, menu_poweruser)

    if remote_role in ('superuser', ):
        menu = "{}{}{}{}{}".format(menu, menu_externaluser, menu_internaluser, menu_poweruser, menu_superuser)


    menu = '<ul>{}<li><a href="/private/verification">Self</a></li><li><a href="/private/logout">logout</a></li></ul>'.format(menu)

    menu = menu + ( '<div id="clear_nav"></div><ul><li id="remote_user_name">{}</li><li id="remote_user">{}</li><li id="remote_role">{}</li><li id="remote_user_id">{}</li><li id="remote_role_id">{}</li></ul>'.format(remote_user_name, remote_user, remote_role, remote_user_id, remote_role_id) )
    return menu

def pager():
    '''
    '''
    attr = {
            'first':{'text':'|<',     'id':'', 'class':'class="pager-first"',          'style':''},
            'prev':{'text':'<-',      'id':'', 'class':'class="pager-prev"',           'style':''},
            'next':{'text':'->',      'id':'', 'class':'class="pager-next"',           'style':''},
            'last':{'text':'>|',      'id':'', 'class':'class="pager-last"',           'style':''},
            'item':{'text':'',        'id':'', 'class':'class="pager-item"',           'style':'', 'wrap':{'element':'', 'id':'', 'class':'', 'style':''}},
            'current':{'text':'',     'id':'', 'class':'class="pager-cuurent active"', 'style':'', 'wrap':{'element':'span', 'id':'', 'class':'', 'style':''},  'href':'javascript:void(0);'},
            }
    return attr
