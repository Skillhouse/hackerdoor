

KERNEL_DIR=/usr/src/kernel
obj-m := wiegand-gpio.o
PWD := $(shell pwd)

all: wiegand-gpio.c
	$(MAKE) -C $(KERNEL_DIR) SUBDIRS=$(PWD) modules

clean:
	make -C $(KERNEL_DIR) SUBDIRS=$(PWD) clean



