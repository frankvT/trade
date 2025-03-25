
def pretty_print(x, fw= 10, dig= 2, indent=1):
      """ Pretty printing dicts, lists and tuples"""
    
      indent = int(indent)
  
      def pretty_print_tup(t, indent=indent):
            """also works for lists""" 
            res = ""
            for v in t:
                  if isinstance(v, float) or isinstance(v, int):
                        formstr = f"{v:{fw}.{dig}f}"
                  else:
                        formstr = f"{v:>{fw}}"
                  res += "\t"*indent + formstr
            res += "\n"
            return res

      def pretty_print_dict(d, indent=indent):
            res = ""
            for k, v in d.items():
              
                  res += "\t"*indent + f"{f'{k}:':<{fw}}"  
                  
                  if isinstance(v, dict):
                        res += "\n"+ pretty_print_dict(v, indent+1)
                   
                  elif isinstance(v, tuple) or isinstance(v, list) :
                        res += pretty_print_tup(v) 
                  else:
                        if isinstance(v, float) or isinstance(v, int):
                              formstr = f"{v:{fw}.{dig}f}"
                        else:
                              formstr = f"{v:>{fw}}"

                        res += "\t"*indent + formstr + "\n"
            return res
      
      if isinstance(x, dict):
          s = pretty_print_dict(x, indent)
      elif isinstance(x, tuple) or isinstance(x, list) :
          s = pretty_print_tup(x, indent)
      else:
            s = x    
      
      return s
# end pretty

'''
# for testing
d = {
            "SYSTEM": 'lin',
            "MONEY": 'Euros',
            "VOLUME": 'Tons',
            "TAR_type": 'Ave',
            "TAR_val": 0.2,
            "homedem_pars": {"const": 20,
                             "slope": -15 },
            "homesup_pars": {"const":-1,
                            "slope": 10},
            "forsup_pars": {"const": -2,
                            "slope": 15},
            "test1":['one', 2]
        }

print('dict: ', pretty_print(d))
l= ['one', 2, 'three']
print('list: ',  pretty_print(l))
t = ('one', 2, 'three')
print('tuple:', pretty_print(l))'
'''

# decorator to set units on functions

def set_unit(unit):
    """Register a unit on a function"""
    def decorator_set_unit(func):
        func.unit = unit
        return func
    return decorator_set_unit
