#!/bin/zsh

tag=$1

[ -z "$1" ] && { echo "I want a tag." ; exit 1 }

cd /tmp

rm -rf grantor-$1
git clone -b "$1" http://gitlab.virtual-expo.com/sql/grantor.git grantor-$1

rm -rf grantor-$1/.git

tar czf ../grantor_$1.orig.tar.gz grantor-$1
