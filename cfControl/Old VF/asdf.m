clc; clear all; close all;

rrin = 0:0.01:5;
A = 1;
Ra = 1;

G = A * (tanh(2 * pi * (Ra - rrin)));

plot(rrin,G)


figure;

decayR = 1;
decay = @(r) - ((tanh(2*pi*r/decayR-pi))+1)/2 + 1;
f = decay(rrin);

plot(rrin,f)