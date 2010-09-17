
from observer import lazyobject

__all__ = ['mulobserver']


class mulobserver(lazyobject):
    '''
    A specialization of a lazyobject.
    This class contains a list of observables to which an instance is attached to.
    When all the observables have sent thier update than self send updates to its
    observers.
    '''
    def __init__(self):
        super(mulobserver,self).__init__(frozen = True)
        self.__subjects = []
    
    def _append_subject(self, subject):
        if subject not in self.__subjects: 
            self.__subjects.append(subject)
        
    def _remove_subject(self, subject):
        try:
            self.__subjects.remove(subject)
        except:
            pass
        
    def __get_subjects(self):
        return self.__subjects
    subjects = property(fget = __get_subjects)
    
    def notify(self, args = None):
        '''
        When notifing observers send self as argument
        '''
        super(mulobserver,self).notify(self)
        
    def doupdate(self, subj):
        '''
        Got an update from subject. Remove subject from
        subject list
        '''
        self.lock.acquire()
        try:
            subj.detach(self)
            sbj = self.__subjects[:]
        except:
            # We got an update from a subject not in our subject list
            # This should not have happened.
            sbj = None
        finally:
            self.lock.release()
        
        if not sbj:
            self.handleupdate()
        
    def handleupdate(self):
        self.frozen = False
    