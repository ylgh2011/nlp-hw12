#!/bin/bash

if [ $# -ne 2 ]; then
	echo "Usage: script.sh <local branch> <remote branch>"
	exit 1
fi

localBranch=$1
remoteBranch=$2

git checkout $remoteBranch
[ $? -ne 0 ] && exit 1
git pull
[ $? -ne 0 ] && exit 1
git checkout $localBranch
[ $? -ne 0 ] && exit 1

git rebase $remoteBranch
[ $? -ne 0 ] && exit 1
git push origin $localBranch:$remoteBranch
[ $? -ne 0 ] && exit 1

git checkout $remoteBranch
[ $? -ne 0 ] && exit 1
git pull
[ $? -ne 0 ] && exit 1
git checkout $localBranch

