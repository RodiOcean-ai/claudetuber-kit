@echo off
rem Render approved styles (one graphics-card job at a time). Usage: tools\render.cmd S01 S02 ...
cd /d "%~dp0.."
py -3.13 tools\render.py %*
