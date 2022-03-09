#!/bin/bash
echo "print data size GB :"
read GB
a=${GB}
let L=a
java -jar pdgf.jar -l demo-schema.xml -l demo-generation.xml -c -s -sf $L
