# gitfuse: mount read only checkouts

I am working quite a bit on repositories where there are different branches for
different versions. Regularly, I need to compare stuff between branches. This
requires more git techniques than I care for. Moreover, when I am working on a
changing a branch, it is annoying to check out things in other branches.

Enter `gitfuse`.

This daemon mounts a readonly FUSE file system locally with predefined
branches in different directories. You can only look at the contents of the
files. There is no concept of editing and history.

`gitfuse` expects a configfile in `~/.config/gitfuse/config.yaml`. An
alternative location can be specified with `-c path/to/file`.

## Installation

```console
$ git clone https://github.com/joepvd/gitfuse.git
$ cd gitfuse
$ pip3 install --user .
```

There is a systemd service file included that can be copied into
`~/.config/systemd/user`. Test with:

```console
$ systemctl start --user gitfuse.service
$ systemctl enable --user gitfuse.service
```

## TODOs
This script does not notice of the base branch has been updated, and will serve
stale information after a fetch.
