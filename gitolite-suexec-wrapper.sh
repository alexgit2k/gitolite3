#!/bin/bash
#
# Suexec wrapper for gitolite-shell
#

export GITOLITE_HTTP_HOME=@@GITOLITE_HOMEDIR@@
export GIT_PROJECT_ROOT=@@GITOLITE_HOMEDIR@@/repositories
export GIT_HTTP_EXPORT_ALL=

exec @@GITOLITE_SHELL@@
