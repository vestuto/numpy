import common_info
from c_spec import common_base_converter
import sys,os

# these may need user configuration.
if sys.platform == "win32":
    wx_base = r'c:\wxpython-2.3.3.1'
else:
    # probably should do some more discovery here.
    wx_base = '/usr/lib/wxPython'

def get_wxconfig(flag):
    wxconfig = os.path.join(wx_base,'bin','wx-config')
    import commands
    res,settings = commands.getstatusoutput(wxconfig + ' --' + flag)
    print 'wx:', flag, settings
    if res:
        msg = wxconfig + ' failed. Impossible to learn wxPython settings'
        raise RuntimeError, msg
    return settings.split()

wx_to_c_template = \
"""
class %(type_name)s_handler
{
public:    
    %(c_type)s convert_to_%(type_name)s(PyObject* py_obj, const char* name)
    {
        %(c_type)s wx_ptr;        
        // work on this error reporting...
        if (SWIG_GetPtrObj(py_obj,(void **) &wx_ptr,"_%(type_name)s_p"))
            handle_conversion_error(py_obj,"%(type_name)s", name);
        %(inc_ref_count)s
        return wx_ptr;
    }
    
    %(c_type)s py_to_%(type_name)s(PyObject* py_obj,const char* name)
    {
        %(c_type)s wx_ptr;        
        // work on this error reporting...
        if (SWIG_GetPtrObj(py_obj,(void **) &wx_ptr,"_%(type_name)s_p"))
            handle_bad_type(py_obj,"%(type_name)s", name);
        %(inc_ref_count)s
        return wx_ptr;
    }    
};

%(type_name)s_handler x__%(type_name)s_handler = %(type_name)s_handler();
#define convert_to_%(type_name)s(py_obj,name) \\
        x__%(type_name)s_handler.convert_to_%(type_name)s(py_obj,name)
#define py_to_%(type_name)s(py_obj,name) \\
        x__%(type_name)s_handler.py_to_%(type_name)s(py_obj,name)

"""

class wx_converter(common_base_converter):
    def __init__(self,class_name="undefined"):
        self.class_name = class_name
        common_base_converter.__init__(self)

    def init_info(self):
        common_base_converter.init_info(self)
        # These are generated on the fly instead of defined at 
        # the class level.
        self.type_name = self.class_name
        self.c_type = self.class_name + "*"
        self.return_type = self.class_name + "*"
        self.to_c_return = None # not used
        self.check_func = None # not used
        self.headers.append('"wx/wx.h"')
        if sys.platform == "win32":        
            # These will be used in many cases
            self.headers.append('<windows.h>')        
            
            # These are needed for linking.
            self.libraries.extend(['kernel32','user32','gdi32','comdlg32',
                                   'winspool', 'winmm', 'shell32', 
                                   'oldnames', 'comctl32', 'ctl3d32',
                                   'odbc32', 'ole32', 'oleaut32', 
                                   'uuid', 'rpcrt4', 'advapi32', 'wsock32'])
                                   
            # not sure which of these macros are needed.
            self.define_macros.append(('WIN32', '1'))
            self.define_macros.append(('__WIN32__', '1'))
            self.define_macros.append(('_WINDOWS', '1'))
            self.define_macros.append(('STRICT', '1'))
            # I think this will only work on NT/2000/XP set
            # set to 0x0400 for earlier versions.
            # Hmmm.  setting this breaks stuff
            #self.define_macros.append(('WINVER', '0x0350'))

            self.library_dirs.append(os.path.join(wx_base,'lib'))
            self.include_dirs.append(os.path.join(wx_base,'include'))            
            

            # how do I discover unicode or not unicode??            
            # non-unicode            
            #self.libraries.append('wxmswh')
            #self.include_dirs.append(os.path.join(wx_base,'lib','mswdllh'))
            
            # unicode
            self.libraries.append('wxmswuh')
            self.include_dirs.append(os.path.join(wx_base,'lib','mswdlluh'))
            self.define_macros.append(('UNICODE', '1'))
        else:
            cxxflags = get_wxconfig('cxxflags')
            libflags = get_wxconfig('libs') + get_wxconfig('gl-libs')
            ldflags = get_wxconfig('ldflags')
            self.extra_compile_args.extend(cxxflags)
            self.extra_link_args.extend(libflags)
            self.extra_link_args.extend(ldflags)
        self.support_code.append(common_info.swig_support_code)
    
    def type_match(self,value):
        is_match = 0
        try:
            wx_class = value.this.split('_')[-2]
            if wx_class[:2] == 'wx':
                is_match = 1
        except AttributeError:
            pass
        return is_match

    def generate_build_info(self):
        if self.class_name != "undefined":
            res = common_base_converter.generate_build_info(self)
        else:
            # if there isn't a class_name, we don't want the
            # we don't want the support_code to be included
            import base_info
            res = base_info.base_info()
        return res
        
    def py_to_c_code(self):
        return wx_to_c_template % self.template_vars()

    #def c_to_py_code(self):
    #    return simple_c_to_py_template % self.template_vars()
                    
    def type_spec(self,name,value):
        # factory
        class_name = value.this.split('_')[-2]
        new_spec = self.__class__(class_name)
        new_spec.name = name        
        return new_spec

    def __cmp__(self,other):
        #only works for equal
        res = -1
        try:
            res = cmp(self.name,other.name) or \
                  cmp(self.__class__, other.__class__) or \
                  cmp(self.class_name, other.class_name) or \
                  cmp(self.type_name,other.type_name)
        except:
            pass
        return res
"""
# this should only be enabled on machines with access to a display device
# It'll cause problems otherwise.
def test(level=10):
    from scipy_test.testing import module_test
    module_test(__name__,__file__,level=level)

def test_suite(level=1):
    from scipy_test.testing import module_test_suite
    return module_test_suite(__name__,__file__,level=level)
"""        