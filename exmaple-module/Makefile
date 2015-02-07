obj-m += mykernelmod.o
KDIR = /usr/src/kernel
PWD := $(shell pwd)

all:
	make -C $(KDIR) M=$(PWD) modules
clean:
	make -C $(KDIR) M=$(PWD) clean
