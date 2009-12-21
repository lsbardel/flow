


class holding(object):
    
    def __init__(self,
                 size,
                 cost_unit_local,
                 book_cost_local,
                 cost_unit_base,
                 book_cost_base,
                 db_date):
        self.size = size
        self.cost_unit_local = cost_unit_local
        self.book_cost_local = book_cost_local
        self.cost_unit_base  = cost_unit_base
        self.book_cost_base  = book_cost_base
        self.dt              = db_date
        
    def traded_price(self):
        if self.cost_unit_local:
            return self.cost_unit_local
        else:
            return self.cost_unit_base
    
    
    