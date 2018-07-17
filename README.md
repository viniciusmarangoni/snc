SNC
---

SNC is a simple script that automatically sets the environment when you get a reverse shell.
It has **the same syntax of netcat** (since it's actually a wrapper to nc)

This program was inspired by [SuperTTY](https://github.com/bad-hombres/supertty)


##### Listen for a reverse shell
```
snc -lnvp 2222
```

When the client connects, it will automatically spawn a python pty and will make you shell interactive, with a 
working tab auto-complete and the right size of terminal. It will also create a folder in /tmp/ to be your home
directory. It will put your personal files there. It's really helpful when performing a penetration test or when
playing some CTF.


##### Automatically upload your files
To automatically upload your tools to the server, just put your tools inside my_home directory. If you prefer,
you can put just a symlink to your tools.

```
ln -s ~/Tools/LinEnum/LinEnum.sh ~/Tools/snc/my_home/LinEnum.sh
```


#### How To Install

Clone this repository into some directory. Then, add this directory to your PATH.
I already have the dir ```~/.local/bin/``` in my PATH, so I just made a symbolic link to snc.

```
ln -s ~/Tools/snc/snc ~/.local/bin/snc
```

#### DEMO
![Demo](https://github.com/{user}/{repo}/raw/master/static/demo.gif)
