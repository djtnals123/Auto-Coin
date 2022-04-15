import string

class Validator:
    def isfloat(inp: string):
        try:
            float(inp)
        except:
            if inp == '':
                return True
            else:
                return False
        return True
    
    
    def isdigit(inp: string):
        if inp == '':
            return True
        return inp.isdigit()
    
    