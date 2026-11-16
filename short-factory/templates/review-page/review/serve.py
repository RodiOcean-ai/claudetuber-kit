"""The review page for a Remotion project (free kit template). Plays every tab LIVE in the browser (Remotion Player,
nothing is rendered); the person pins notes on the picture, comments on a whole tab, notes a sound on the timeline,
reads Claude's replies and approves each tab's build for rendering. Only standard Python (3.9+); the page itself is
bundled with the esbuild that every Remotion project already has in node_modules.

  python review/serve.py [port]                                  serve (default 3030) -> http://127.0.0.1:3030
  python review/serve.py notes [tab]                             print the notes (per tab, by time) and the approvals
  python review/serve.py reply <tab> <n> "text" [done]           Claude's answer under note n of a tab (number as on the page)
  python review/serve.py build <tab> "<label>" [--change "..."]... [--standin "..."]...   set a tab's build (marks it ready)

Tabs are the ids in review/items.json (written by review/make_items.py from review/contract.json); an exact id or a
prefix that fits only one tab is enough.
Files in review/: notes.json (notes + approvals), builds.json (label, changes, placeholders per tab), review.js (the
bundle, rebuilt whenever src/ or the page's .tsx files change), timeline.json (make_timeline.py),
sounds.json (sound effects and clips per tab, read by the page from the compositions).
A note: frame null = a comment on the whole tab (key C); track = a note on one timeline track, item = what is there.
The server listens on 127.0.0.1 only (this PC), never on the network. Writes (notes, approvals, sounds) are taken only
from the page itself: the request must come from this page's own address (Origin or Referer) and carry the random token
the server puts into the page on every start, so another website open in the same browser cannot write notes or approve
a build. Claude's commands below edit the files directly and need no token. Never expose or tunnel this page."""
import hmac, json, mimetypes, os, secrets, shutil, socket, subprocess, sys, threading, time, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

try:  # notes may hold any language; never let the console's code page break a request
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

RV = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(RV)
SRC, PUB = os.path.join(ROOT, 'src'), os.path.join(ROOT, 'public')
ASSETS = os.path.join(RV, '_bundle')       # pictures, fonts and sounds imported in the code (esbuild copies them here)
TYPES = {'.js': 'text/javascript', '.json': 'application/json', '.html': 'text/html; charset=utf-8', '.css': 'text/css',
         '.mp4': 'video/mp4', '.webm': 'video/webm', '.mov': 'video/quicktime', '.wav': 'audio/wav', '.mp3': 'audio/mpeg',
         '.m4a': 'audio/mp4', '.aac': 'audio/aac', '.ogg': 'audio/ogg', '.png': 'image/png', '.jpg': 'image/jpeg',
         '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp', '.avif': 'image/avif', '.svg': 'image/svg+xml',
         '.woff': 'font/woff', '.woff2': 'font/woff2', '.ttf': 'font/ttf', '.otf': 'font/otf'}
FILE_LOADERS = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'avif', 'svg', 'bmp', 'woff', 'woff2', 'ttf', 'otf',
                'mp3', 'wav', 'ogg', 'm4a', 'aac', 'mp4', 'webm', 'mov']
LOCK = threading.Lock()
EMPTY = {'notes': [], 'approvals': []}
TRACKS = {'picture', 'clips', 'voice', 'music', 'sfx'}
TOKEN = secrets.token_urlsafe(32)          # new on every start; only the page served from here knows it
MAX_BODY = 5_000_000                       # bytes; a note or a sounds list is far smaller


def item_ids():
    """the tab ids, read again on every request: re-running make_items.py needs no restart"""
    p = os.path.join(RV, 'items.json')
    if not os.path.exists(p):
        sys.exit('review/items.json is missing: fill in review/contract.json, then run  python review/make_items.py')
    return json.load(open(p, encoding='utf-8'))


item_ids()      # stop at once with a clear message when the tabs were never made


def sid(s):
    ids = item_ids()
    exact = [x for x in ids if x.lower() == s.lower()]       # an exact id wins (CH1 vs CH10)
    m = exact or [x for x in ids if x.lower().startswith(s.lower())]
    if len(m) != 1:
        sys.exit(f'unknown tab {s!r}; use one of {ids}')
    return m[0]


def jload(name, default):
    p = os.path.join(RV, name)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else json.loads(json.dumps(default))


def jsave(name, d):
    p = os.path.join(RV, name)
    with open(p + '.tmp', 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
    os.replace(p + '.tmp', p)


def newest(paths):
    m = 0.0
    for p in paths:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in files:
                    m = max(m, os.path.getmtime(os.path.join(root, f)))
        elif os.path.exists(p):
            m = max(m, os.path.getmtime(p))
    return m


def bundle_time():
    """newest change to what goes into review.js: the project's src/ and the page's .tsx files"""
    return newest([SRC] + [os.path.join(RV, f) for f in os.listdir(RV) if f.endswith('.tsx')])


def code_time():
    """what the page compares to show "Claude changed the videos: reload" (also new timeline data)"""
    return max(bundle_time(), newest([os.path.join(RV, 'timeline.json')]))


def fkey(n):
    return -1 if n.get('frame') is None else n['frame']


def esbuild():
    """The project's own esbuild (Remotion installs it), looked for in node_modules here and in the folders above."""
    names = ['esbuild.cmd', 'esbuild.exe'] if os.name == 'nt' else ['esbuild']
    d = ROOT
    while True:
        for n in names:
            p = os.path.join(d, 'node_modules', '.bin', n)
            if os.path.exists(p):
                return p
        up = os.path.dirname(d)
        if up == d:
            break
        d = up
    return shutil.which('esbuild')


def bundle():
    out = os.path.join(RV, 'review.js')
    if os.path.exists(out) and os.path.getmtime(out) >= bundle_time():
        return ''
    exe = esbuild()
    if not exe:
        return 'esbuild was not found. Run "npm install" in the project folder first (Remotion brings esbuild with it).'
    cmd = [exe, 'review/ReviewApp.tsx', '--bundle', '--format=iife', '--jsx=automatic', '--loader:.json=json',
           '--define:process.env.NODE_ENV="production"', '--target=chrome120', '--outfile=review/review.js',
           '--asset-names=_bundle/[name]-[hash]', '--public-path=/', '--log-level=warning']
    cmd += [f'--loader:.{x}=file' for x in FILE_LOADERS]
    t = time.time()
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        print('BUILD FAILED\n' + r.stdout + r.stderr, flush=True)
        return (r.stdout + r.stderr).strip() or f'esbuild stopped with code {r.returncode}'
    print(f'built review.js in {time.time() - t:.1f} s', flush=True)
    return ''


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code); self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(b))); self.send_header('Cache-Control', 'no-store'); self.end_headers()
        self.wfile.write(b)

    def _text(self, txt, code=200, ctype='text/plain; charset=utf-8', extra=()):
        b = txt.encode('utf-8')
        self.send_response(code); self.send_header('Content-Type', ctype); self.send_header('Content-Length', str(len(b)))
        self.send_header('Cache-Control', 'no-store')
        for k, v in extra:
            self.send_header(k, v)
        self.end_headers(); self.wfile.write(b)

    def _own(self):
        port = self.server.server_address[1]
        return (f'http://127.0.0.1:{port}', f'http://localhost:{port}')

    def _host_ok(self):
        """asked for by this PC's own address (stops a website that points its own name at 127.0.0.1)"""
        return self.headers.get('Host', '') in [o[len('http://'):] for o in self._own()]

    def _write_ok(self):
        """a write comes from this page: its own Origin (or, without one, its own Referer) and this run's token"""
        own, origin = self._own(), self.headers.get('Origin')
        if origin is not None:
            from_page = origin in own
        else:
            ref = self.headers.get('Referer') or ''
            from_page = any(ref == o or ref.startswith(o + '/') for o in own)
        sent = self.headers.get('X-Review-Token', '').encode('utf-8', 'replace')
        return from_page and hmac.compare_digest(sent, TOKEN.encode('ascii'))

    def _page(self):
        """index.html with this run's token in it (the page reads it and sends it back on every write)"""
        html = open(os.path.join(RV, 'index.html'), encoding='utf-8').read()
        html = html.replace('<head>', f'<head>\n<meta name="review-token" content="{TOKEN}">', 1)
        return self._text(html, ctype='text/html; charset=utf-8',
                          extra=[('X-Frame-Options', 'DENY'), ('Content-Security-Policy', "frame-ancestors 'none'")])

    def _file(self, path):
        size = os.path.getsize(path)
        ctype = TYPES.get(os.path.splitext(path)[1].lower()) or mimetypes.guess_type(path)[0] or 'application/octet-stream'
        start, end, code = 0, size - 1, 200
        rng = self.headers.get('Range')
        if rng and rng.startswith('bytes='):
            a, _, b = rng[6:].split(',')[0].strip().partition('-')
            try:
                if a == '':
                    start, end = max(0, size - int(b)), size - 1
                else:
                    start, end = int(a), (min(int(b), size - 1) if b else size - 1)
            except ValueError:
                start, end = 0, size - 1
            if start >= size or start > end:
                self.send_response(416); self.send_header('Content-Range', f'bytes */{size}'); self.end_headers(); return
            code = 206
        self.send_response(code); self.send_header('Content-Type', ctype); self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Length', str(end - start + 1)); self.send_header('Cache-Control', 'no-cache')
        if code == 206:
            self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.end_headers()
        try:
            with open(path, 'rb') as f:
                f.seek(start); left = end - start + 1
                while left > 0:
                    chunk = f.read(min(1 << 20, left))
                    if not chunk:
                        break
                    self.wfile.write(chunk); left -= len(chunk)
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
            pass

    @staticmethod
    def _inside(base, rel):
        full = os.path.normpath(os.path.join(base, rel.lstrip('/')))
        return full if full.startswith(os.path.normpath(base) + os.sep) and os.path.isfile(full) else None

    def do_GET(self):
        if not self._host_ok():
            return self._text('refused: open the page at http://127.0.0.1:<port>', 403)
        path = unquote(urlparse(self.path).path)
        if path in ('/', '/index.html'):
            err = bundle()
            if err:
                return self._text('The review page could not be built:\n\n' + err, 500)
            return self._page()
        if path == '/review.js':
            bundle()
            return self._file(os.path.join(RV, 'review.js'))
        if path == '/review.css':     # only there when the project's code imports CSS
            css = os.path.join(RV, 'review.css')
            return self._file(css) if os.path.exists(css) else self._text('', ctype='text/css')
        if path == '/api/state':
            with LOCK:
                d = jload('notes.json', EMPTY)
            return self._json({'builds': jload('builds.json', {}), 'notes': d['notes'], 'approvals': d['approvals'], 'code': code_time()})
        if path == '/api/timeline':
            tl = jload('timeline.json', {})
            tl['sounds'] = jload('sounds.json', {})
            return self._json(tl)
        if path == '/favicon.ico':
            self.send_response(204); self.end_headers(); return
        if path.startswith('/_bundle/'):
            full = self._inside(ASSETS, path[len('/_bundle/'):])
            if full:
                return self._file(full)
        full = self._inside(PUB, path)      # staticFile() paths: the project's public/ folder
        if not full:
            return self._text('not found', 404)
        return self._file(full)

    def do_POST(self):
        if not (self._host_ok() and self._write_ok()):
            print('REFUSED a write that did not come from the review page itself', flush=True)
            return self._text('refused: writes are only taken from the review page itself (reload the page)', 403)
        path = urlparse(self.path).path
        n = int(self.headers.get('Content-Length') or 0)
        if n > MAX_BODY:
            return self._text('too big', 413)
        try:
            body = json.loads(self.rfile.read(n) or b'{}')
        except ValueError:
            return self._text('bad json', 400)
        with LOCK:
            d = jload('notes.json', EMPTY)
            tab = str(body.get('style', ''))
            label = jload('builds.json', {}).get(tab, {}).get('label', '')
            if path == '/api/sounds':
                key, items = str(body.get('key', '')), body.get('items')
                if key not in item_ids() or not isinstance(items, list):
                    return self._text('bad sounds', 400)
                snd = jload('sounds.json', {})
                snd[key] = {'items': items, 'at': time.strftime('%Y-%m-%d %H:%M:%S'), 'code': body.get('code')}
                jsave('sounds.json', snd)
                return self._json({'ok': True, 'n': len(items)})
            if path == '/api/notes':
                text = str(body.get('text', '')).strip()
                if not text or tab not in item_ids():
                    return self._text('empty note or unknown tab', 400)
                fr = body.get('frame')
                track = body.get('track') if body.get('track') in TRACKS else None
                item = str(body.get('item') or '')[:400] or None
                note = {'id': uuid.uuid4().hex[:8], 'style': tab, 'frame': None if fr is None else int(fr),
                        't': None if fr is None else round(float(body.get('t') or 0), 3), 'x': body.get('x'), 'y': body.get('y'),
                        'track': track, 'item': item, 'text': text,
                        'created': time.strftime('%Y-%m-%d %H:%M:%S'), 'status': 'open', 'build': label}
                d['notes'].append(note); jsave('notes.json', d)
                where = 'whole video' if fr is None else f"{note['t']:.2f} s (frame {note['frame']})"
                print(f"NOTE {tab} {where}{f' [{track}] {item}' if track else ''}: {text}", flush=True)
                return self._json(note)
            if path.startswith('/api/notes/') and path.endswith('/delete'):
                nid = path.split('/')[3]
                d['notes'] = [x for x in d['notes'] if not (x['id'] == nid and x['status'] == 'open')]
                jsave('notes.json', d); print(f'NOTE deleted {nid}', flush=True)
                return self._json({'ok': True})
            if path == '/api/approve':
                if tab not in item_ids():
                    return self._text('unknown tab', 400)
                a = {'style': tab, 'build': str(body.get('build') or label), 'at': time.strftime('%Y-%m-%dT%H:%M:%S')}
                d['approvals'].append(a); jsave('notes.json', d)
                print(f"APPROVED {tab} {a['build']} at {a['at']}", flush=True)
                return self._json(a)
        return self._text('not found', 404)


class Server(ThreadingHTTPServer):
    # Python's default lets a second server on Windows share the same port without an error, and the page then talks
    # to either at random. Claim the port for this server alone instead.
    allow_reuse_address = os.name != 'nt'

    def server_bind(self):
        if os.name == 'nt' and hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def tab_notes(d, tab):
    return sorted([n for n in d['notes'] if n['style'] == tab], key=fkey)


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args or args[0].isdigit():
        port = int(args[0]) if args else 3030
        if not os.path.exists(os.path.join(RV, 'notes.json')):
            jsave('notes.json', EMPTY)
        if bundle():
            print('first build failed (the page will show the error)', flush=True)
        with socket.socket() as probe:                     # something already answers there: do not share the port
            probe.settimeout(0.5)
            busy = probe.connect_ex(('127.0.0.1', port)) == 0
        try:
            if busy:
                raise OSError
            srv = Server(('127.0.0.1', port), H)
        except OSError:
            sys.exit(f'port {port} is already in use (another review page or program). Start with another port, '
                     f'for example: python review/serve.py {port + 1}')
        print(f'review page: http://127.0.0.1:{port}', flush=True)
        srv.serve_forever()
    elif args[0] == 'notes':
        d = jload('notes.json', EMPTY)
        for s in ([sid(args[1])] if len(args) > 1 else item_ids()):
            ns = tab_notes(d, s)
            if not ns:
                continue
            print(f'== {s}')
            for i, n in enumerate(ns, 1):
                spot = '' if n.get('x') is None else f" at x {n['x']:.2f} y {n['y']:.2f}"
                when = 'WHOLE VIDEO' if n.get('frame') is None else f"{n['t']:.2f} s (frame {n['frame']})"
                trk = f" TRACK {n['track']}" + (f" ({n['item']})" if n.get('item') else '') if n.get('track') else ''
                print(f"{i}. [{n['status']}] {when}{spot}{trk} [{n.get('build', '')}]: {n['text']}"
                      + (f"\n   reply: {n['reply']}" if n.get('reply') else ''))
        for a in d['approvals']:
            print(f"APPROVED: {a['style']} {a['build']} at {a['at']}")
    elif args[0] == 'reply' and len(args) >= 4:
        s, k, text = sid(args[1]), int(args[2]), args[3]
        with LOCK:
            d = jload('notes.json', EMPTY); ns = tab_notes(d, s)
            if not 1 <= k <= len(ns):
                sys.exit(f'{s} has {len(ns)} notes; there is no note {k}')
            n = ns[k - 1]
            n['reply'] = text
            if len(args) > 4 and args[4] == 'done':
                n['status'] = 'done'
            jsave('notes.json', d)
        print('ok', n['id'])
    elif args[0] == 'build' and len(args) >= 3:
        s, label = sid(args[1]), args[2]
        ch = [args[i + 1] for i, a in enumerate(args[:-1]) if a == '--change']
        st = [args[i + 1] for i, a in enumerate(args[:-1]) if a == '--standin']
        b = jload('builds.json', {}); b[s] = {'label': label, 'changes': ch, 'standins': st, 'at': time.strftime('%Y-%m-%d %H:%M')}
        jsave('builds.json', b); print('ok', s, label)
    else:
        sys.exit(__doc__)
