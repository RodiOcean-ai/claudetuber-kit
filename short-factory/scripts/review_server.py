"""The owner's review page on localhost (14 Nov 2026): play an episode's edit LIVE in the browser (Remotion Player, nothing is
rendered), click a spot at any moment and leave a note, read Claude's replies, approve the build for rendering.
Owner: "From now on you NEVER rendering before I approve the build in the online broswer (local host)" and "Add also note
system that I can point on the browser closing the communication gap".

  python review_server.py serve <episode or its edit folder> [port]     (default port 3010; then open http://127.0.0.1:3010)
  python review_server.py notes <episode>                               print the notes (open first) and approvals
  python review_server.py reply <episode> <note number> "text" [done]   Claude's answer under a note (number as on the page)
  python review_server.py build <episode> <build.json>                  set the build's title, label, changes, placeholders

Files (in <episode>/edit/review/): ReviewApp.tsx + index.html (copied from templates/review on every start), review.js
(the bundle, rebuilt by esbuild whenever edit/src or the app changes), notes.json (notes + approvals), build.json.
Writes (notes, approvals) are taken only from the page itself: its own address and the random token put into the page
on every start. Claude's commands edit the files directly. Never expose or tunnel this page."""
import hmac, json, mimetypes, os, secrets, shutil, subprocess, sys, threading, time, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(os.path.dirname(HERE), 'templates', 'review')
TYPES = {'.js': 'text/javascript', '.json': 'application/json', '.html': 'text/html; charset=utf-8', '.css': 'text/css',
         '.mp4': 'video/mp4', '.webm': 'video/webm', '.mov': 'video/quicktime', '.wav': 'audio/wav', '.mp3': 'audio/mpeg',
         '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml', '.ttf': 'font/ttf',
         '.woff2': 'font/woff2'}
LOCK = threading.Lock()
TOKEN = secrets.token_urlsafe(32)          # new on every start; only the page served from here knows it
MAX_BODY = 5_000_000                       # bytes; a note is far smaller


def edit_dir(p):
    p = os.path.abspath(p)
    return p if os.path.isdir(os.path.join(p, 'src')) else os.path.join(p, 'edit')


def load_notes(rv):
    p = os.path.join(rv, 'notes.json')
    if not os.path.exists(p):
        return {'notes': [], 'approvals': []}
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def save_notes(rv, d):
    p = os.path.join(rv, 'notes.json')
    with open(p + '.tmp', 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
    os.replace(p + '.tmp', p)


def load_build(rv):
    p = os.path.join(rv, 'build.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


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


def bundle(ed):
    """Rebuild review/review.js if the edit's code or the app changed. Returns an error text or ''."""
    rv = os.path.join(ed, 'review'); out = os.path.join(rv, 'review.js')
    if os.path.exists(out) and os.path.getmtime(out) >= newest([os.path.join(ed, 'src'), os.path.join(rv, 'ReviewApp.tsx')]):
        return ''
    exe = os.path.join(ed, 'node_modules', '.bin', 'esbuild.cmd' if os.name == 'nt' else 'esbuild')
    cmd = [exe, 'review/ReviewApp.tsx', '--bundle', '--format=iife', '--jsx=automatic', '--loader:.json=json',
           '--define:process.env.NODE_ENV="production"', '--target=chrome120', '--outfile=review/review.js', '--log-level=warning']
    t = time.time()
    r = subprocess.run(cmd, cwd=ed, capture_output=True, text=True)
    if r.returncode:
        print('BUILD FAILED\n' + r.stdout + r.stderr, flush=True)
        return (r.stdout + r.stderr).strip()
    print(f'built review.js in {time.time() - t:.1f} s', flush=True)
    return ''


def make_handler(ed):
    rv = os.path.join(ed, 'review'); pub = os.path.join(ed, 'public')

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

        def _page(self, index):
            """index.html with this run's token in it (the page reads it and sends it back on every write)"""
            html = open(index, encoding='utf-8').read()
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

        def do_GET(self):
            if not self._host_ok():
                return self._text('refused: open the page at http://127.0.0.1:<port>', 403)
            path = unquote(urlparse(self.path).path)
            if path in ('/', '/index.html'):
                err = bundle(ed)
                if err:
                    return self._text('The review page could not be built:\n\n' + err, 500)
                return self._page(os.path.join(rv, 'index.html'))
            if path == '/review.js':
                bundle(ed)
                return self._file(os.path.join(rv, 'review.js'))
            if path == '/api/state':
                with LOCK:
                    d = load_notes(rv)
                code = newest([os.path.join(ed, 'src'), os.path.join(rv, 'ReviewApp.tsx')])   # the page offers a reload when it changes
                return self._json({'build': load_build(rv), 'notes': d['notes'], 'approvals': d['approvals'], 'code': code})
            if path == '/favicon.ico':
                self.send_response(204); self.end_headers(); return
            full = os.path.normpath(os.path.join(pub, path.lstrip('/')))
            if not full.startswith(os.path.normpath(pub) + os.sep) or not os.path.isfile(full):
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
            label = load_build(rv).get('label', '')
            with LOCK:
                d = load_notes(rv)
                if path == '/api/notes':
                    text = str(body.get('text', '')).strip()
                    if not text:
                        return self._text('empty note', 400)
                    note = {'id': uuid.uuid4().hex[:8], 'frame': int(body.get('frame', 0)), 't': round(float(body.get('t', 0)), 3),
                            'x': body.get('x'), 'y': body.get('y'), 'text': text,
                            'created': time.strftime('%Y-%m-%d %H:%M:%S'), 'status': 'open', 'build': label}
                    d['notes'].append(note); save_notes(rv, d)
                    print(f"NOTE {note['t']:.2f} s (frame {note['frame']}): {text}", flush=True)
                    return self._json(note)
                if path.startswith('/api/notes/') and path.endswith('/delete'):
                    nid = path.split('/')[3]
                    d['notes'] = [x for x in d['notes'] if not (x['id'] == nid and x['status'] == 'open')]
                    save_notes(rv, d); print(f'NOTE deleted {nid}', flush=True)
                    return self._json({'ok': True})
                if path == '/api/approve':
                    a = {'build': str(body.get('build') or label), 'at': time.strftime('%Y-%m-%dT%H:%M:%S')}
                    d['approvals'].append(a); save_notes(rv, d)
                    print(f"APPROVED {a['build']} at {a['at']}", flush=True)
                    return self._json(a)
            return self._text('not found', 404)

    return H


def serve(ep, port=3010):
    ed = edit_dir(ep); rv = os.path.join(ed, 'review')
    os.makedirs(rv, exist_ok=True)
    for f in ('ReviewApp.tsx', 'index.html'):
        shutil.copyfile(os.path.join(TEMPLATE, f), os.path.join(rv, f))
    if not os.path.exists(os.path.join(rv, 'notes.json')):
        save_notes(rv, {'notes': [], 'approvals': []})
    err = bundle(ed)
    if err:
        print('first build failed (the page will show the error)', flush=True)
    srv = ThreadingHTTPServer(('127.0.0.1', port), make_handler(ed))
    print(f'review page: http://127.0.0.1:{port}  ({ed})', flush=True)
    srv.serve_forever()


def sorted_notes(d):
    return sorted(d['notes'], key=lambda n: n['frame'])


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, ep = sys.argv[1], sys.argv[2]
    rv = os.path.join(edit_dir(ep), 'review')
    if cmd == 'serve':
        serve(ep, int(sys.argv[3]) if len(sys.argv) > 3 else 3010)
    elif cmd == 'notes':
        d = load_notes(rv)
        for i, n in enumerate(sorted_notes(d), 1):
            spot = '' if n['x'] is None else f" at x {n['x']:.2f} y {n['y']:.2f}"
            print(f"{i}. [{n['status']}] {n['t']:.2f} s (frame {n['frame']}){spot} [{n.get('build', '')}]: {n['text']}"
                  + (f"\n   reply: {n['reply']}" if n.get('reply') else ''))
        for a in d['approvals']:
            print(f"APPROVED: {a['build']} at {a['at']}")
    elif cmd == 'reply':
        k, text = int(sys.argv[3]), sys.argv[4]
        with LOCK:
            d = load_notes(rv); n = sorted_notes(d)[k - 1]
            n['reply'] = text
            if len(sys.argv) > 5 and sys.argv[5] == 'done':
                n['status'] = 'done'
            save_notes(rv, d)
        print('ok', n['id'])
    elif cmd == 'build':
        shutil.copyfile(sys.argv[3], os.path.join(rv, 'build.json')); print('ok')
    else:
        sys.exit(__doc__)
