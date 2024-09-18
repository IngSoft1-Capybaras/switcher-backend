from enum import Enum
from pony.orm.dbapiprovider import StrConverter

#Definimos la conversión de enum para poder utilizar los tipos definidos en la DB
class EnumConverter(StrConverter):
         
    def validate(self, val, bool):
        '''
            verificamos que val sea una instancia de la clase Enum
            asegura que solo valores validos de enum sean procesados
            evitando errores de tipo'''
            
        if isinstance(val, Enum):
            return val
        raise ValueError(f"Expected an Enum, got {type(val)}")
    
    def py2sql(self, val):
        '''
            Convertir un valor enum de Python a una string con 
            el valor de su nombre para poder guardarlo en la DB
        '''
        return val.name
        
    
    def sql2py(self, val):
        '''
            Convertir la representación de SQL de un valor enum
            al valor de enum en Python que le corresponde 
        '''
        return self.py_type(val)
    

