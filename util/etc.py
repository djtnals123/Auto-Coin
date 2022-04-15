def is_checked(chk):
    var = chk.getvar(str(chk.cget('variable')))
    if(var == '0'):
        return False
    else:
        return True