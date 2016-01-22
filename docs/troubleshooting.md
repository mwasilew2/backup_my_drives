tools necessary to mount a truecrypt volume:
- truecrypt binary
- yum install ntfs-3g
- yum install fuse-libs

Run TrueCrypt from the drive where OS runs. If you store your container on a USB drive, on the same drive you have a portable TrueCrypt binary and you run TrueCrypt binary from that drive to mount that container you won't be able to unmount it - you will get an error message saying the drive is busy.

preferences: iocharset=utf8

why ntfs not ext3 - cause windows is having difficulties mounting ext 3 drives

to allow non root mount of truecrypt containers:
- create a group truecrypt
- add your user to this group
- add to sudoers with visudo:
# Users in the truecrypt group are allowed to run TrueCrypt as root.
%truecrypt ALL=(root) NOPASSWD:/usr/bin/truecrypt
