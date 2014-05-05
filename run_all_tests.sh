#!/bin/bash

tests=(
 "TestCases/InstructionTest/BackwardBEQ"
 "TestCases/InstructionTest/BackwardBNE"
 "TestCases/InstructionTest/BackwardUnconditionalJump"
 "TestCases/InstructionTest/ForwardBEQ"
 "TestCases/InstructionTest/ForwardBNE"
 "TestCases/InstructionTest/ForwardUnconditionalJump"
 "TestCases/InstructionTest/LoadInstructions"
 "TestCases/InstructionTest/StoreInstructions"
 "TestCases/CacheTest/BusCompetition"
 "TestCases/CacheTest/StoreAndLoad"
 "TestCases/HazardTest/RAW"
 "TestCases/HazardTest/Struct/FU"
 "TestCases/HazardTest/Struct/WB"
 "TestCases/HazardTest/WAW"
 "TestCases/ComplexTest/FirstTest"
 "TestCases/ConfigErrorTest/CaseSensitive"
 "TestCases/ConfigErrorTest/MultipleSpace"
 "TestCases/ConfigErrorTest/InvalidConfigFile"
 "TestCases/ConfigErrorTest/MissingLabel"
 )


for name in "${tests[@]}"
	do
    echo -e "\n=============== Start of $name ===============\n"

    instFile=$name"/inst.txt"
    dataFile=$name"/data.txt"
    regFile=$name"/reg.txt"
    configFile=$name"/config.txt"
    resultFile=$name"/result.txt"

    python simulator.py  "$instFile" "$dataFile" "$regFile" "$configFile" "result.txt"
    echo -e "=======================================================================\n"
    cat "$name/result.txt"

    echo -e "\n=============== End of $name ==============="

    read
  done
