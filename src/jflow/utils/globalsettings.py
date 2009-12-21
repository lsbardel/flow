

__all__ = ['msetting','get_machine','set_machines','outerpath']


class msetting:
    
    def __init__(self,
                 engine   = 'sqlite3',  #'postgresql_psycopg2',
                 host     = '',
                 port     = '',         # 5432 for postgresql (usually)
                 tempdir  = '.',
                 name     = '',
                 user     = '',
                 password = '',
                 cache    = '',
                 app_path = ''):
        self.engine   = engine
        self.host     = host
        self.port     = str(port)
        self.name     = name
        self.user     = user
        self.password = password
        self.cache    = cache
        self.tempdir  = tempdir
        self.machine  = None
        self.app_path = app_path
        
        
def get_machine(machines, default_setting):
    import platform
    node = platform.node()
    node = node.split('.')[0]
    sett = machines.get(node, default_setting)
    sett.machine = node
    return sett
    
def set_outerpath(p):
    global outer_path
    outer_path = p
    return outer_path

outer_path  = None