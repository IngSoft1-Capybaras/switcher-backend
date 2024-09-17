from enum import Enum
from pony.orm.dbapiprovider import StrConverter

class EnumConverter(StrConverter):        
    def py2sql(self, val):
        return val.value
    
    def sql2py(self, val):
        return self.py_type(val)


    
