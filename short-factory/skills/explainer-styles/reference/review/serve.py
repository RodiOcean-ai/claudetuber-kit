"""The owner's review page for the 11 styles (adapted from short-factory/scripts/review_server.py, 14 Nov 2026).
Plays every style LIVE in the browser (Remotion Player, nothing is rendered), one tab per style; the owner clicks a spot at
any moment and leaves a note on that style, reads Claude's replies, and approves each style's build for rendering.

  py -3.13 review/serve.py [port]                                   serve (default 3020) -> http://127.0.0.1:3020
  py -3.13 review/serve.py notes [style]                            print notes (per style, by time) and approvals
  py -3.13 review/serve.py reply <style> <n> "text" [done]          Claude's answer under note n of a style (number as on the page)
  py -3.13 review/serve.py build <style> "<label>" [--change "..."]... [--standin "..."]...   set a style's build (marks it ready)
Styles are the composition ids (S01-KineticTypography ...); a prefix like S01 is enough.
Files: review/notes.json (notes + approvals), review/builds.json (label, changes, placeholders per style), review/review.js
(the bundle, rebuilt with esbuild whenever src/ or ReviewApp.tsx changes).
Writes (notes, approvals) are taken only from the page itself: its own address and the random token put into the page
on every start. Claude's commands edit the files directly. Never expose or tunnel this page."""
import hmac, json, mimetypes, os, secrets, subprocess, sys, threading, time, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

RV = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(RV)
SRC, PUB = os.path.join(ROOT, 'src'), os.path.join(ROOT, 'public')
TYPES = {'.js': 'text/javascript', '.json': 'application/json', '.html': 'text/html; charset=utf-8', '.css': 'text/css',
         '.mp4': 'video/mp4', '.webm': 'video/webm', '.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.png': 'image/png',
         '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.woff2': 'font/woff2'}
LOCK = threading.Lock()
TOKEN = secrets.token_urlsafe(32)          # new on every start; only the page served from here knows it
MAX_BODY = 5_000_000                       # bytes; a note is far smaller
STYLE_IDS = ['S01-KineticTypography', 'S02-MotionGraphics', 'S03-Screencast', 'S04-Isometric', 'S05-Whiteboard', 'S06-Comic',
             'S07-TwoPointFiveD', 'S08-Collage', 'S09-CharacterStory', 'S10-ThreeD', 'S11-StopMotion',
             'T05-WhiteboardThreeJS', 'T06-ComicThreeJS']
EMPTY = {'notes': [], 'approvals': []}


def sid(s):
    m = [x for x in STYLE_IDS if x.lower().startswith(s.lower())]
    if len(m) != 1:
        sys.exit(f'unknown style {s!r}; use one of {STYLE_IDS}')
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


def code_time():
    return newest([SRC, os.path.join(RV, 'ReviewApp.tsx')])


def bundle():
    out = os.path.join(RV, 'review.js')
    if os.path.exists(out) and os.path.getmtime(out) >= code_time():
        return ''
    exe = os.path.join(ROOT, 'node_modules', '.bin', 'esbuild.cmd' if os.name == 'nt' else 'esbuild')
    cmd = [exe, 'review/ReviewApp.tsx', '--bundle', '--format=iife', '--jsx=automatic', '--loader:.json=json',
           '--define:process.env.NODE_ENV="production"', '--target=chrome120', '--outfile=review/review.js', '--log-level=warning']
    t = time.time()
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        print('BUILD FAILED\n' + r.stdout + r.stderr, flush=True)
        return (r.stdout + r.stderr).strip()
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
            err = bundle()
            if err:
                return self._text('The review page could not be built:\n\n' + err, 500)
            return self._page(os.path.join(RV, 'index.html'))
        if path == '/review.js':
            bundle()
            return self._file(os.path.join(RV, 'review.js'))
        if path == '/api/state':
            with LOCK:
                d = jload('notes.json', EMPTY)
            return self._json({'builds': jload('builds.json', {}), 'notes': d['notes'], 'approvals': d['approvals'], 'code': code_time()})
        if path == '/favicon.ico':
            self.send_response(204); self.end_headers(); return
        full = os.path.normpath(os.path.join(PUB, path.lstrip('/')))
        if not full.startswith(os.path.normpath(PUB) + os.sep) or not os.path.isfile(full):
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
            style = str(body.get('style', ''))
            label = jload('builds.json', {}).get(style, {}).get('label', '')
            if path == '/api/notes':
                text = str(body.get('text', '')).strip()
                if not text or style not in STYLE_IDS:
                    return self._text('empty note or unknown style', 400)
                note = {'id': uuid.uuid4().hex[:8], 'style': style, 'frame': int(body.get('frame', 0)),
                        't': round(float(body.get('t', 0)), 3), 'x': body.get('x'), 'y': body.get('y'), 'text': text,
                        'created': time.strftime('%Y-%m-%d %H:%M:%S'), 'status': 'open', 'build': label}
                d['notes'].append(note); jsave('notes.json', d)
                print(f"NOTE {style} {note['t']:.2f} s (frame {note['frame']}): {text}", flush=True)
                return self._json(note)
            if path.startswith('/api/notes/') and path.endswith('/delete'):
                nid = path.split('/')[3]
                d['notes'] = [x for x in d['notes'] if not (x['id'] == nid and x['status'] == 'open')]
                jsave('notes.json', d); print(f'NOTE deleted {nid}', flush=True)
                return self._json({'ok': True})
            if path == '/api/approve':
                if style not in STYLE_IDS:
                    return self._text('unknown style', 400)
                a = {'style': style, 'build': str(body.get('build') or label), 'at': time.strftime('%Y-%m-%dT%H:%M:%S')}
                d['approvals'].append(a); jsave('notes.json', d)
                print(f"APPROVED {style} {a['build']} at {a['at']}", flush=True)
                return self._json(a)
        return self._text('not found', 404)


def style_notes(d, style):
    return sorted([n for n in d['notes'] if n['style'] == style], key=lambda n: n['frame'])


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args or args[0].isdigit():
        port = int(args[0]) if args else 3020
        if not os.path.exists(os.path.join(RV, 'notes.json')):
            jsave('notes.json', EMPTY)
        if bundle():
            print('first build failed (the page will show the error)', flush=True)
        srv = ThreadingHTTPServer(('127.0.0.1', port), H)
        print(f'review page: http://127.0.0.1:{port}', flush=True)
        srv.serve_forever()
    elif args[0] == 'notes':
        d = jload('notes.json', EMPTY)
        for s in ([sid(args[1])] if len(args) > 1 else STYLE_IDS):
            ns = style_notes(d, s)
            if not ns:
                continue
            print(f'== {s}')
            for i, n in enumerate(ns, 1):
                spot = '' if n['x'] is None else f" at x {n['x']:.2f} y {n['y']:.2f}"
                print(f"{i}. [{n['status']}] {n['t']:.2f} s (frame {n['frame']}){spot} [{n.get('build', '')}]: {n['text']}"
                      + (f"\n   reply: {n['reply']}" if n.get('reply') else ''))
        for a in d['approvals']:
            print(f"APPROVED: {a['style']} {a['build']} at {a['at']}")
    elif args[0] == 'reply':
        s, k, text = sid(args[1]), int(args[2]), args[3]
        with LOCK:
            d = jload('notes.json', EMPTY); n = style_notes(d, s)[k - 1]
            n['reply'] = text
            if len(args) > 4 and args[4] == 'done':
                n['status'] = 'done'
            jsave('notes.json', d)
        print('ok', n['id'])
    elif args[0] == 'build':
        s, label = sid(args[1]), args[2]
        ch = [args[i + 1] for i, a in enumerate(args) if a == '--change']
        st = [args[i + 1] for i, a in enumerate(args) if a == '--standin']
        b = jload('builds.json', {}); b[s] = {'label': label, 'changes': ch, 'standins': st, 'at': time.strftime('%Y-%m-%d %H:%M')}
        jsave('builds.json', b); print('ok', s, label)
    else:
        sys.exit(__doc__)
