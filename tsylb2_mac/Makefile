CC = gcc
CFLAGS = -Wall -O2

SRCS = tsylb2.c addstres.c mpron3.c no_wbndl.c no_wbndr.c
OBJS = $(SRCS:.c=.o)
TARGET = tsylb2

$(TARGET): $(OBJS)
	$(CC) $(OBJS) -o $(TARGET)

%.o: %.c
	$(CC) $(CFLAGS) -c $<

clean:
	rm -f $(OBJS) $(TARGET)
