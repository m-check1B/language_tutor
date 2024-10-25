import cProfile
import pstats
import io
from functools import wraps

def profile(output_file=None):
    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            pr = cProfile.Profile()
            pr.enable()
            result = func(*args, **kwargs)
            pr.disable()
            
            s = io.StringIO()
            sortby = 'cumulative'
            ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            ps.print_stats()
            
            print(s.getvalue())
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(s.getvalue())
            
            return result
        return wrapper
    return inner
