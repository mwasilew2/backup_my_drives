- tools necessary to mount a truecrypt volume:
    - truecrypt binary
    - yum install ntfs-3g
    - yum install fuse-libs

- Run TrueCrypt from the drive where OS runs. If you store your container on a USB drive, on the same drive you have a portable TrueCrypt binary and you run TrueCrypt binary from that drive to mount that container you won't be able to unmount it - you will get an error message saying the drive is busy.

- preferences: iocharset=utf8

- file system:
	- depends where the drive will be used, e.g. if you know it will be only used on a linux machine you can use ext4
	- for windows ntfs (fat32 does not support links, Windows cannot moutn anything else)

- truecrypt requires a kernel module called loop
    - rhel 7.2, /etc/sysconfig/modules/loop.modules:
```
#!/bin/sh
/usr/sbin/lsmod | grep -q "loop"
if [ $? -ne 0 ] ; then
    exec /usr/sbin/modprobe loop > /dev/null 2>&1
fi

```
    - create devices (modern kernels don't create any devices when they load loop module), /etc/modprobe.d/eightloop.conf:
```
options loop max_loop=8


```
- permissions on a newly created volume: top directory might be owned by root, just chmod to your user


virtualbox
==========

If you're mounting a container on a USB drive, you need to mount the usb drive as yourself, i.e. you might also need to add yourself to the vboxsf user group: `usermod -a -G vboxsf your_username` and mount the folder as yourself, i.e. `sudo mount -t vboxsf -o uid=xxxxx,gid=xxxxx mount_name_here /path/to/mount/folder`. At the moment of writing vboxsf mount options do not include SELinux settings, so you cannot change the file context for the mount.

Then mount the truecrypt volume with the right SELinux options:

truecrypt --mount container --fs-options='iocharset=utf8,context=system_u:object_r:user_home_t:s0' mountpoint

to allow non root mount of truecrypt containers:
- create a group truecrypt
- add your user to this group
- add to sudoers with visudo:
# Users in the truecrypt group are allowed to run TrueCrypt as root.
%truecrypt ALL=(root) NOPASSWD:/usr/bin/truecrypt

