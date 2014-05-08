## MIPS Simulator

### Steps to Run:

```
$ make
```
OR

```
$ python simulator.py inst.txt data.txt reg.txt config.txt result.txt
```
OR

```
$ ./make.sh inst.txt data.txt reg.txt config.txt result.txt
```
If you do not specify any parameters to ```make.sh``` it will take the default files in the folder.
Also, you might have to give the ```make.sh``` executbale permissions if they are not present.
Run the following command for the same:
```
$ chmod +x make.sh
```


### To clean the executables from the project directory, run:

```
$ make clean
```
