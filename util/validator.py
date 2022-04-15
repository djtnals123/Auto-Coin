import string

class Validator:
    def isfloat(inp: string):
        try:
            float(inp)
        except:
            if inp is '':
                return True
            else:
                return False
        return True
    
    
    def isdigit(inp: string):
        if inp is '':
            return True
        return inp.isdigit()
    
    