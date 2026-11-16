# Your brand (optional)

The author's RodiOcean brand files are not included. The kit works without them; the edit and the 3D lab simply show no
name or logo. To brand your own videos, start with your brand sheet: ask Claude to "brand my channel" (skill `yt-branding`). It
writes `BRAND.md` here (name, handle, niche, colours, fonts, mascot, voice) and saves your logo, banner and fonts next to
it; the thumbnail and edit skills read it, and Claude takes your colours, fonts and voice from it for every video. Then add your files here with these names:
- `world_prints/`: badge.png, buoy_ring.png, crate_name.png, crate_sub.png, cylinder.png, floor_paint.png, hull.png
  (your channel name printed on props in the 3D lab; transparent PNGs);
- `templates/`: plain backgrounds for title cards, `bg_<A-D>_<name>_tall.jpg` and `..._wide.jpg`.
For the edit's sound logo and wave transition, put your own `sonar_ping_short.wav`, `sonar_ping_echo.wav`, `sea_wave.wav`
and `sea_wave_1080x1920.webm` in `templates/edit/public/brand/`, or switch them off in `edit/src/brand.json`.
