#!/bin/bash
cryptsetup benchmark -c aes-cbc --key-size 128

cryptsetup benchmark -c aes-cbc --key-size 256

cryptsetup benchmark -c aes-xts --key-size 256

cryptsetup benchmark -c aes-xts --key-size 512
