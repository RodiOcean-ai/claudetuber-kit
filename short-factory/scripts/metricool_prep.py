"""Get a finished Short ready for Metricool (14 Nov 2026, owner: "I want to fully automate this"; first two posts scheduled
this way the same day). Copies the final video and the chosen cover into the Dropbox folder on this PC (Dropbox for desktop
uploads them by itself), and writes post/metricool_post.json: the whole Metricool post (one post for YouTube Short,
Instagram Reel, TikTok and Facebook Reel; title, caption, AI labels, not made for kids) with two placeholders,
<VIDEO_LINK> and <COVER_LINK>.

Then Claude, in the chat, ONLY after the owner's explicit OK for this post ("post it at 21:00"):
  1. Dropbox get_file_metadata on both dropbox_paths until each exists with the printed size (about a minute for 35 MB);
  2. Dropbox download_link on both paths (expiration_in_sec 900): one-time links;
  3. replace the placeholders and call Metricool createScheduledPost(blogId, date, info) straight away; Metricool copies the
     files into its own storage at once, so the links may expire after that (a failed call can use them up: make new ones);
  4. check the stored copies: the response's media / videoThumbnailUrl on static.metricool.com must have the same byte sizes;
  5. tracker / JOURNEY: scheduled via Metricool, with the post's uuid.

Usage: python -I -X utf8 metricool_prep.py <episode_dir> --date YYYY-MM-DD --time HH:MM [--cover A|B|<file>] [--video <file>]
Reads the title and the description from post/POST.md (post_kit.py), the Metricool brand from config.json "metricool"."""
import argparse, datetime as dt, json, os, re, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sfconfig

PLACEHOLDER_VIDEO, PLACEHOLDER_COVER = '<VIDEO_LINK>', '<COVER_LINK>'


def dropbox_root():
    for base in (os.environ.get('LOCALAPPDATA', ''), os.environ.get('APPDATA', '')):
        p = os.path.join(base, 'Dropbox', 'info.json')
        if os.path.exists(p):
            info = json.load(open(p, encoding='utf-8'))
            acct = info.get('personal') or next(iter(info.values()))
            return acct['path']
    sys.exit('Dropbox for desktop is not installed on this PC (no Dropbox/info.json): install it and sign in first.')


def section(md, head):
    """The text under '## <head...>' up to the next '## ' heading."""
    m = re.search(r'^## ' + re.escape(head) + r'[^\n]*\n(.*?)(?=^## |\Z)', md, re.M | re.S)
    return m.group(1).strip() if m else ''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('episode'); ap.add_argument('--date', required=True); ap.add_argument('--time', required=True)
    ap.add_argument('--cover', default='A'); ap.add_argument('--video')
    ap.add_argument('--dry', action='store_true', help='check and print only: no copy into Dropbox, nothing written')
    a = ap.parse_args()
    mc = sfconfig.CFG.get('metricool') or sys.exit('config.json has no "metricool" section')
    ep = os.path.abspath(a.episode); slug = os.path.basename(ep.rstrip('/\\')); post = os.path.join(ep, 'post')
    video = a.video or os.path.join(post, f'{slug}_FINAL.mp4')
    cover = a.cover if os.path.isfile(a.cover) else os.path.join(post, f'COVER_{a.cover.upper()}.jpg')
    for f in (video, cover):
        if not os.path.isfile(f):
            sys.exit(f'missing: {f}')
    md = open(os.path.join(post, 'POST.md'), encoding='utf-8').read()
    title = section(md, 'Title').splitlines()[0].strip()
    desc = section(md, 'Description')
    if not title or not desc:
        sys.exit('POST.md needs a "## Title" and a "## Description" section (run post_kit.py first)')
    if len(title) > 100:
        sys.exit(f'title is {len(title)} characters; YouTube allows 100')

    # the slot, with this PC's UTC offset (the PC and the Metricool brand both run on the same local time)
    when = dt.datetime.strptime(f'{a.date} {a.time}', '%Y-%m-%d %H:%M')
    if when < dt.datetime.now() + dt.timedelta(minutes=15):
        sys.exit('that time is in the past or less than 15 minutes away')
    off = when.astimezone().strftime('%z'); off = off[:3] + ':' + off[3:]

    # copy into the Dropbox folder on this PC
    sub = f'{a.date} {slug}'
    local = os.path.join(dropbox_root(), mc['dropbox_folder'], sub)
    vname, cname = f'{slug}_video.mp4', f'{slug}_cover.jpg'
    if not a.dry:
        os.makedirs(local, exist_ok=True)
        shutil.copyfile(video, os.path.join(local, vname)); shutil.copyfile(cover, os.path.join(local, cname))
    dpaths = [f'/{mc["dropbox_folder"]}/{sub}/{vname}', f'/{mc["dropbox_folder"]}/{sub}/{cname}']

    info = {
        'autoPublish': True, 'descendants': [], 'draft': False, 'firstCommentText': '', 'hasNotReadNotes': False,
        'media': [PLACEHOLDER_VIDEO], 'videoThumbnailUrl': PLACEHOLDER_COVER, 'mediaAltText': [],
        'providers': [{'network': n} for n in mc['networks']],
        'publicationDate': {'dateTime': when.strftime('%Y-%m-%dT%H:%M:%S'), 'timezone': mc['timezone']},
        'shortener': False, 'smartLinkData': {'ids': []},
        'text': f'{title}\n\n{desc}',
        'youtubeData': {'title': title, 'type': 'short', 'privacy': 'public', 'tags': [], 'madeForKids': False,
                        'isAiGeneratedContent': True},
        'instagramData': {'type': 'REEL', 'showReelOnFeed': True, 'isAiGenerated': True},
        'tiktokData': {'disableComment': False, 'disableDuet': False, 'disableStitch': False,
                       'privacyOption': 'PUBLIC_TO_EVERYONE', 'commercialContentThirdParty': False,
                       'commercialContentOwnBrand': False, 'title': title, 'autoAddMusic': False, 'isAigc': True},
        'facebookData': {'type': 'REEL', 'title': title}}
    for n in ('youtube', 'instagram', 'tiktok', 'facebook'):        # only the networks this brand posts to
        if n not in mc['networks']:
            info.pop(f'{n}Data', None)
    out = {'blogId': mc['blog_id'], 'date': when.strftime('%Y-%m-%dT%H:%M:%S') + off, 'info': info,
           'dropbox_paths': dpaths, 'sizes': [os.path.getsize(video), os.path.getsize(cover)]}
    p = os.path.join(post, 'metricool_post.json')
    if a.dry:
        print(json.dumps(out, indent=1, ensure_ascii=False)); p = '(dry run: nothing copied or written)'
    else:
        json.dump(out, open(p, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'slot: {when:%A %d %B %Y, %H:%M} ({mc["timezone"]}, UTC{off}) on {", ".join(mc["networks"])}')
    print(f'title: {title}')
    print(f'dropbox: {dpaths[0]} ({out["sizes"][0]} bytes)\n         {dpaths[1]} ({out["sizes"][1]} bytes)')
    print(f'wrote {p}  (placeholders {PLACEHOLDER_VIDEO} and {PLACEHOLDER_COVER})')


if __name__ == '__main__':
    main()
