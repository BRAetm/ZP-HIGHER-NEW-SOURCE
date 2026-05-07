import frida, time, sys

EXE = r"C:\Users\brael\Downloads\zp-higher-lite-full\ZP-HIGHER-Lite.exe"
JS = open(r"C:\Users\brael\Downloads\zp-higher-lite-full\trace.js").read()

# Add the anti-debug hooks too — paste them inline
ANTI_JS = '''
'use strict';
function antiDebug() {
    var k32 = Process.findModuleByName('kernel32.dll');
    var ntdll = Process.getModuleByName('ntdll.dll');
    var isDbg = k32 && k32.findExportByName('IsDebuggerPresent');
    if (isDbg) Interceptor.replace(isDbg, new NativeCallback(function(){ return 0; }, 'int', []));
    var crd = k32 && k32.findExportByName('CheckRemoteDebuggerPresent');
    if (crd) Interceptor.replace(crd, new NativeCallback(function(h, p){ if(!p.isNull()) p.writeInt(0); return 1; }, 'int', ['pointer','pointer']));
    var ntq = ntdll.findExportByName('NtQueryInformationProcess');
    if (ntq) {
        var orig = new NativeFunction(ntq, 'uint32', ['pointer','uint32','pointer','uint32','pointer']);
        Interceptor.replace(ntq, new NativeCallback(function(h, ic, p, l, r){
            var s = orig(h, ic, p, l, r);
            if (s === 0 && !p.isNull()) {
                if (ic === 7 || ic === 30) p.writePointer(NULL);
                else if (ic === 31) p.writeInt(1);
            }
            return s;
        }, 'uint32', ['pointer','uint32','pointer','uint32','pointer']));
    }
    var cpw = k32 && k32.findExportByName('CreateProcessW');
    if (cpw) Interceptor.attach(cpw, {
        onEnter: function(args) {
            try {
                var a = (args[0].isNull() ? '' : args[0].readUtf16String()) + ' ' + (args[1].isNull() ? '' : args[1].readUtf16String());
                if (/tasklist|wmic/i.test(a)) this.block = true;
            } catch(_) {}
        },
        onLeave: function(r) { if (this.block) r.replace(0); }
    });
}
antiDebug();
'''

device = frida.get_local_device()
sessions = []

def on_msg(msg, data):
    print(msg.get("payload") or msg)
    sys.stdout.flush()

def attach(pid, label):
    s = device.attach(pid)
    s.enable_child_gating()
    sessions.append(s)
    sc1 = s.create_script(ANTI_JS); sc1.on("message", on_msg); sc1.load()
    sc2 = s.create_script(JS);      sc2.on("message", on_msg); sc2.load()
    print(f"[*] attached {label} pid={pid}")
    sys.stdout.flush()

def on_child(child):
    try: attach(child.pid, "child")
    except Exception as e: print(f"[!] {e}")
    device.resume(child.pid)

device.on("child-added", on_child)
pid = device.spawn(EXE)
attach(pid, "parent")
device.resume(pid)
print(f"[*] spawned {pid}")
sys.stdout.flush()

try:
    while True: time.sleep(1)
except KeyboardInterrupt:
    for s in sessions: s.detach()
