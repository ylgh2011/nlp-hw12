#!/bin/bash

if [ $# -ne 2 ]; then
	echo "Usage: script.sh <remote branch> <local branch>"
	exit 1
fi

remoteBranch=$1
localBranch=$2

git checkout $localBranch
[ $? -ne 0 ] && exit 1
git stash
[ $? -ne 0 ] && exit 1

git checkout $remoteBranch
[ $? -ne 0 ] && exit 1
git pull
[ $? -ne 0 ] && exit 1
git checkout $localBranch
[ $? -ne 0 ] && exit 1

git rebase $remoteBranch
[ $? -ne 0 ] && exit 1
git stash apply --index
[ $? -ne 0 ] && exit 1
git stash drop
[ $? -ne 0 ] && exit 1

echo "OK!"
