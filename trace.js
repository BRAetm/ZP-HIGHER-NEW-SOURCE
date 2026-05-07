'use strict';
var done = false;
function pyExp(name) {
    var m = Process.findModuleByName('python311.dll');
    if (!m) return null;
    return m.findExportByName(name);
}
function poll() {
    if (done) return;
    var fnEnsure = new NativeFunction(pyExp('PyGILState_Ensure'),'int',[]);
    var fnRel    = new NativeFunction(pyExp('PyGILState_Release'),'void',['int']);
    var fnRun    = new NativeFunction(pyExp('PyRun_SimpleString'),'int',['pointer']);
    var code = [
        'try:',
        '    import sys, builtins, traceback, time',
        '    if getattr(builtins, "_zp_traced", False): raise SystemExit',
        '    LOG = r"C:\\\\Users\\\\brael\\\\Downloads\\\\zp-higher-lite-full\\\\trace.log"',
        '    def L(s):',
        '        try:',
        '            with open(LOG, "a") as f:',
        '                f.write(time.strftime("%H:%M:%S ") + str(s) + "\\n")',
        '        except: pass',
        '    # Hook QMessageBox.critical/warning/information to log + suppress',
        '    from PySide6.QtWidgets import QMessageBox',
        '    for mname in ["critical","warning","information","question"]:',
        '        orig = getattr(QMessageBox, mname, None)',
        '        if orig is None: continue',
        '        def make_wrap(name, o):',
        '            def w(*a, **kw):',
        '                try:',
        '                    title = a[1] if len(a)>1 else kw.get("title","?")',
        '                    text  = a[2] if len(a)>2 else kw.get("text","?")',
        '                    L("QMessageBox." + name + " title=" + repr(title) + " text=" + repr(text))',
        '                    L("STACK:\\n" + "".join(traceback.format_stack()[-8:]))',
        '                except: pass',
        '                return QMessageBox.StandardButton.Ok',
        '            return w',
        '        setattr(QMessageBox, mname, staticmethod(make_wrap(mname, orig)))',
        '    # Hook sys.exit to log',
        '    _orig_exit = sys.exit',
        '    def _hook_exit(code=None):',
        '        L("sys.exit(" + str(code) + ")")',
        '        L("STACK:\\n" + "".join(traceback.format_stack()[-10:]))',
        '        return _orig_exit(code) if code is not None else _orig_exit()',
        '    sys.exit = _hook_exit',
        '    # Hook __main__.main (if present) to trace its execution',
        '    main = sys.modules.get("__main__")',
        '    L("=== TRACE INSTALLED, main attrs include: " + ",".join([a for a in dir(main) if not a.startswith("_")][:30]) + " ===")',
        '    builtins._zp_traced = True',
        'except SystemExit: pass',
        'except Exception as e:',
        '    try:',
        '        with open(r"C:\\\\Users\\\\brael\\\\Downloads\\\\zp-higher-lite-full\\\\trace.log","a") as f:',
        '            f.write("ERR " + repr(e) + "\\n")',
        '    except: pass',
        ''
    ].join('\n');
    var st = fnEnsure();
    fnRun(Memory.allocUtf8String(code));
    fnRel(st);
}
function tryHook() {
    if (Process.findModuleByName('python311.dll')) {
        if (!done) {
            done = true;
            // Poll a few times in case PySide6 isn't ready immediately
            var n = 0;
            var iv = setInterval(function() {
                n++;
                done = false; poll(); done = true;
                if (n >= 60) clearInterval(iv);
            }, 200);
        }
    }
}
var ntdll = Process.getModuleByName('ntdll.dll');
Interceptor.attach(ntdll.findExportByName('LdrLoadDll'), { onLeave: function(_){ tryHook(); }});
tryHook();
