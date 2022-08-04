#!/usr/bin/env python

import csv
import sys
import socket
import math

# Dewpoint algorithm by http://www.wetterochs.de/wetter/feuchte.html

def RHtoDP(T, r):
  dd = DD(T, r);
  a = 0;
  b = 0;
  if (T>0):
    a = 7.5;
    b = 237.3;
  else:
    a = 7.6;
    b = 240.7;
  c = math.log10(dd/6.1078);
  dewpoint = (b*c) / (a-c);
  return dewpoint;

def DD(T,r):
  sdd = SDD(T);
  dd  = float(r/100.0) * sdd;
  return dd;

def SDD(T):
  a = 0;
  b = 0;
  if (T>=0):
    a = 7.5;
    b = 237.3;
  else:
    a = 7.6;
    b = 240.7;

  sdd = 6.1078 * 10**((a*T)/(b+T))
  return sdd;

def main():
    if len(sys.argv) != 3:
        print("Usage: dewpoint.py [temperature field] [humidity field]")
        sys.exit(1)

    temperatureField = sys.argv[1]
    humidityField = sys.argv[2]

    infile = sys.stdin
    outfile = sys.stdout

    r = csv.DictReader(infile)
    header = r.fieldnames

    w = csv.DictWriter(outfile, fieldnames=header)
    w.writeheader()


    for result in r:
        result["dewpoint"] = str(RHtoDP(float(result[temperatureField]),float(result[humidityField])))
        w.writerow(result)

main()
