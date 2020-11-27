# gitfuse: mount read only checkouts

I am working quite a bit on repositories where there are different branches for
different versions. Regularly, I need to compare stuff between branches. This
requires more git techniques than I care for. Moreover, when I am working on a
changing a branch, it is annoying to check out things in other branches.

Enter `gitfuse`.

This little script mounts a readonly FUSE file system locally with some predefined
branches in different directories. You can only look at the contents of the
files. There is no concept of commits.

At this moment, only a single branch from a single repository can be mounted.

Configuration is in the code, in the `main()` function. I plan to add a
configuration parser.
