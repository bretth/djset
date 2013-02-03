#!/bin/sh 

function dexport() {
	export $@;
	SETTINGS=`djs_locate_settings`;
	if [ "$SETTINGS" != '' ]; then
		touch $SETTINGS
	fi
}

function dunset() {
	unset $@;
	SETTINGS=`djs_locate_settings`;
	if [ "$SETTINGS" != '' ]; then
		touch $SETTINGS
	fi
}