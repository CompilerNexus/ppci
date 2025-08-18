import io

from ppci.api import asm, cc, link
from ppci.format.hunk import write_hunk
from ppci.format.srecord import write_srecord

source = """
int add(int x, int y) {
  return x + y;
}

"""

obj = cc(io.StringIO(source), "m68k")
obj = link([obj])
print(obj)

print(
    f"""
Please now open the online disassembler:

https://onlinedisassembler.com/odaweb/

Select m68k:68000

and paste:
{obj.get_section("code").data.hex()}

"""
)

# TODO:
with open("demo.srec", "w") as f:
    write_srecord(obj, f)


obj = asm("amiga_hello_world.asm", "m68k")
obj = link([obj])
print(obj)

print(obj.get_section("code").data.hex())

write_hunk("demo", obj.get_section("code").data)
