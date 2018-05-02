#! /bin/bash

rm ~/.ssh/*

# generate key
ssh-keygen -t rsa

ssh-add 

# copy key
ssh-copy-id eagles 
ssh-copy-id clash  
ssh-copy-id motorhead 
ssh-copy-id sunlight  
ssh-copy-id blur   
