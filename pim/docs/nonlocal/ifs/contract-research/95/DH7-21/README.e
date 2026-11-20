
Copyright(C)1996 Shigeki Mitaku

SOSUI: Secondary Structure Prediction System
of Membrane Proteins.

[Required Environment]

A Unix workstation with HTTP Daemon and WWW browser on internet environment.

[File Configurarion]

Expanded directory of "sosui.tar" has the following directories and files.
 
    README.j
    README.e
    copyright
    sample.seq: Sample sequences
    doc/: Document of SOSUI system
    man/: User manual of SOSUI system
    html/: Interface programs for SOSUI (HTML format)
    gif/: Interface programs for SOSUI (GIF format)
    src/: SOSUI main programs
    script/: SOSUI executive script

[Compiling and Installing SOSUI]

1. Compiling of SOSUI main program.

Change directory to src/ and execute a command as following,

	cc -o sosui main.c readAA.c toHPI.c identSH.c 
	identFH.c assTMcore.c regionPred.c memcalc.c -lm

2. Set up of GUI

Copy both html/index.html and gif/sosui.gif files to the your internet home directory.

3. Set up to Script

Copy script/sosui.script, src/sosui and src/parameter.txt to the "cgi-bin" available directory.

4. Changing a line of index.html

Input a your Domain or IP address.

	<form method="POST" action="http://(your domain or IP address)/cgi-bin/sosui.script">

5. Changing a line of sosui.script

Input a your Domain or IP address.

	echo '<center><A HREF="http://(your domain or IP address)/index.html">


