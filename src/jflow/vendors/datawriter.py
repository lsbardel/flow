


def csvToCache(vfid, data, CacheFactory, std):
    '''
    Write the csv values into cache
    
    @param vfid:
    @param data:
    @param CacheFactory:
    @param std: function string to date converter    
    '''  
    if not data:
        return
    vid     = vfid.vid
    field   = vfid.field
    fcode   = vfid.vendor_field.code
    datestr = None
    for r in data:
        try:
            if not datestr:
                val   = None
                dt    = None
                found = 0
                for k,v in r.items():
                    if k == fcode:
                        val    = v
                        found += 1 
                    elif len(k) >= 4:
                        if k[len(k)-4:] == 'Date':
                            datestr = k
                            dt = v
                            found += 1
                    if found == 2:
                        break
                if found < 2:
                    raise ValueError
            else:
                val = r[fcode]
                dt  = r[datestr]
                
            val = float(val)
            dt  = std(dt)
            try:
                m = CacheFactory.get(vendor_id = vid, field = field, dt = dt)
                m.mkt_value = val
            except:
                m = CacheFactory(vendor_id = vid, field = field, dt = dt, mkt_value = val)
            m.save()
        except:
            pass

