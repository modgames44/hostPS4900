@echo off
setlocal enabledelayedexpansion

for %%A in (PS3HEN.BIN_CEX_4??) do (
set a=%%A
set b=!a:~16,3!
xcopy /Y PS3HEN.BIN_CEX_4!b! C:\PS3HEN\Make_PKG\4.!b!\dev_rewrite\hen\PS3HEN.BIN
)
