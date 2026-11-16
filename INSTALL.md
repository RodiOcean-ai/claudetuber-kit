# Installing the kit (instructions for Claude)

The person typed "install" (or asked to set up the kit). Work through these steps in order. Talk in plain English, one
short line per step, and ask before installing or downloading anything. Never spend money, never enter passwords, and
never start a paid generation. `<kit>` below means this folder (the one holding this file).
**The place to begin is `/start-claudetube`:** the guided start runs this install as its step 1, then takes the person
through the other six steps; point anyone new there (typing "install" still works on its own).

1. **Look first.** Check what is already on the PC: Python 3.11+, Node.js 20+, FFmpeg, Blender 4.2+ (only needed for the
   3D world), Git (optional). Say in one short list what is there and what is missing.
2. **Tools.** Offer to install what is missing and wait for a yes. On Windows use `winget`, for example
   `winget install Python.Python.3.12`, `winget install OpenJS.NodeJS.LTS`, `winget install Gyan.FFmpeg`,
   `winget install BlenderFoundation.Blender`. On a Mac use Homebrew; on Linux the system package manager.
3. **Python packages.** Make a virtual environment in `<kit>/short-factory/.venv` and install
   `<kit>/short-factory/requirements.txt` into it. The heavy optional packages at the bottom of that file (speech
   recognition) are only needed for channel studies and voice checks: say so, and install them only if the person agrees.
4. **Node packages.** Run `npm install` in `<kit>/short-factory/templates/edit` (the Shorts edit) and, if the person wants
   the sandwich project, in `<kit>/eleven-styles-sandwich` (about 2.4 GB).
5. **Folders.** Ask where channel studies and episodes should live; suggest `Documents/short-factory/studies` and
   `Documents/short-factory/episodes`, and create them.
6. **Settings.** Copy `<kit>/short-factory/config.example.json` to `<kit>/short-factory/config.json` and fill in real full
   paths: `home` (the `short-factory` folder itself), `python` (the `.venv` Python), `ffmpeg_dir`, `blender`,
   `studies_root`, `episodes_root`, `edit_node_modules` (`templates/edit/node_modules`) and `sound_library`
   (`assets/house_sound`). Fonts: Arial Black and Arial Bold exist on every Windows PC; on a Mac or Linux pick similar
   bold fonts. Leave the `metricool` and `voice_inhouse` sections as they are until the person wants those features.
   Do this BEFORE step 8: the plugin is copied into Claude Code's own folder when it is installed.
7. **Tracker.** Run `"<the .venv python>" -I "<kit>/short-factory/scripts/tracker.py" init` (it creates the empty tracker
   workbook in `short-factory/data/`).
8. **Plugin.** Run `claude plugin marketplace add "<kit>/short-factory"` and then
   `claude plugin install short-factory@rodiocean`. If the `claude` command is not available in the shell, ask the
   person to type these two lines in Claude Code instead: `/plugin marketplace add <kit>/short-factory` and
   `/plugin install short-factory@rodiocean`. Then ask them to restart Claude Code.
9. **Optional extras** (ask about each one, never install them silently):
   - real instrument recordings for Claude-composed music: `scripts/get_instruments.py` (free CC0, about 740 MB);
   - the free local voice: Chatterbox and ClearerVoice, each in its own virtual environment, plus two voice samples
     (see `short-factory/assets/voice/README.md`); then fill the `voice_inhouse` section of `config.json`;
   - a local picture maker (for example ComfyUI) for the picture-based styles;
   - Metricool and Dropbox for scheduled posting (the person's own accounts; they sign in themselves).
10. **Done.** Tell them what to try first: "make a 15-second explainer in whiteboard style", `/study-channel @somechannel`,
    `/make-short`, "set up the review page" (in any Remotion project), or "open the sandwich project"
    (`npx remotion studio` in `<kit>/eleven-styles-sandwich`).

Words used in the skills: `${CLAUDE_PLUGIN_ROOT}` is the plugin folder (`short-factory`); `<python>`, `<studies_root>`
and `<episodes_root>` are the values in `config.json`; `<projects>` is the folder that holds the studies and episodes
folders; `<your-picture-maker>`, `<your-sound-library>`, `<your-voice-sample.wav>` and `<tools>` are the person's own
tools and files. "The owner" in the skills means the person using the kit.
