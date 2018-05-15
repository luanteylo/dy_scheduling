#!/bin/bash

EXEC=s1

OMEGA=25
ALPHA=120000
BETA=5200
GAMA=7000
DELTA=512
TETA=0
LAMBDA=22600

#mpicc synthetic.c -lm /usr/local/lib/libpapi.a -DPASSO=$DELTA  -DWSS=$GAMA  -DVECTOR_NUM=3 -DTETA=$TETA  -DBYTES_MSG=$LAMBDA -DBETA=$BETA -DALPHA=$ALPHA -DOMEGA=$OMEGA -DLABEL=1 -o s1

mpicc sintetico.c -lpapi -lm  -DPASSO=$DELTA  -DWSS=$GAMA  -DVECTOR_NUM=3 -DTETA=$TETA  -DBYTES_MSG=$LAMBDA -DBETA=$BETA -DALPHA=$ALPHA -DOMEGA=$OMEGA -DLABEL=1 -o $EXEC

if [ -d "bin/" ]; then
	rm -f bin/*
else
	mkdir bin
fi

mv $EXEC bin/
