This directory contains the previous version of phphphphphphp challenge.
Getting diff between this and the newer challenge might give you some hints.
The intended solution to that challenge shouldn't help you with the newer challenge but just for your information:
- use chroot to to change root to /tmp/
- create directory "/var/www/sbx/usr/local/lib/php/extensions/no-debug-non-zts-20230831" 
- write a malicious library at "/no-debug-non-zts-20230831/lib.so"
- chroot to "/var/www/sbx"
- dl("lib")
- chdir to a directory and then chroot(..) back to / to escape chroot jail 
