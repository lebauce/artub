try:
    import psyco
except ImportError:
    psyco = None
    
    
def __proxy_t(f):
    return psyco.proxy(f)
    
    
def __proxy_f(f):
    return f
    
if psyco:
    proxy = __proxy_t
else:
    proxy = __proxy_f