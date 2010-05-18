import datetime

from jflow.log import LoggingClass
from jflow.core.cache import cache


def toyyyymmyy(dt):
    return dt.day + 100*(dt.month + 100*dt.year)

class Portfolio(LoggingClass):
    '''Portfolio Cache Handler build on to of jflow.core.cache'''
    
    def get_team_aggregate(self, team, date):
        '''For a given team and date aggregate all portfolios
        
            * **team** string code defining the team
            * **date** date required
        '''
        key = '%s-%s-%s' % (self,team.lower(),toyyyymmyy(date))
        agg = cache.get(key)
        if agg:
            return agg
        data = self.get_team_data(team, date)
        agg = self._build_team_aggregate(key, team, date, data)
        cache.set(key,agg)
        return agg
    
    def _build_team_aggregate(self, key, team, date):
        '''Build team aggregate. This function should be called only by get_team_aggregate
        '''
        
        
        
    def get_team_data(self, team, date):
        raise NotImplementedError('This function needs to be implemented by derived class')
    