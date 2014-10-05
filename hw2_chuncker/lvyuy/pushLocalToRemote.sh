#!/bin/bash

if [ "$#" -ne 2 ]; then
	echo "Usage: scriptname <local branch> <remote branch>"
	exit 1
fi

localBranch="$1"
remoteBranch="$2"

git checkout $remoteBranch
git pull
git checkout $localBranch

git rebase $remoteBranch
git push origin $localBranch:$remoteBranch

git checkout $remoteBranch
git pull
git checkout $localBranch

