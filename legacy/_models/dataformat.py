
__all__ = ['data_formats','datahandler']

data_formats = ('csv','json')

def datahandler(format = 'csv'):
    '''
    Constructor for a data handler
    '''
    sf = str(format).lower()
    if sf == 'csv':
        return csv_handler()
    elif sf == 'json':
        return json_handler()
     
        