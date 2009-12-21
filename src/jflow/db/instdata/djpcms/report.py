
import add


class view(add.view):
    '''
     Add new data id to database.
     If the data id is a financial instrument, a new
     instrument will be also added to the database.
    '''

    def title(self):
        return 'Reporting  %s' % self.object