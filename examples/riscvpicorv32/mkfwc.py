import argparse
import logging
import os
from glob import glob

from ppci.api import asm, cc, get_arch, link, objcopy
from ppci.binutils.objectfile import merge_memories
from ppci.lang.c import COptions
from ppci.utils.reporting import html_reporter


def get_sources(folder, extension):
    resfiles = []
    resdirs = []
    for x in os.walk(folder):
        for y in glob(os.path.join(x[0], extension)):
            resfiles.append(y)
        resdirs.append(x[0])
    return (resdirs, resfiles)


with html_reporter("report.html") as reporter:
    arch = get_arch("riscv")
    o1 = asm("start.s", arch)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "folder", help="folder inside the csrc directory to use"
    )
    parser.add_argument(
        "-v",
        help="increase verbosity of output",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()
    if args.v:
        logging.basicConfig(level=logging.DEBUG)
    path = os.path.join(".", "csrc", args.folder)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path not found: {path}")
    dirs, srcs = get_sources(path, "*.c")
    srcs += [os.path.join(".", "csrc", "bsp.c")] + [
        os.path.join(".", "csrc", "lib.c")
    ]
    dirs += [os.path.join(".", "csrc")]
    obj = []
    coptions = COptions()
    for dir in dirs:
        coptions.add_include_path(dir)
    for src in srcs:
        with open(src) as f:
            obj.append(
                cc(
                    f,
                    "riscv",
                    coptions=coptions,
                    debug=True,
                    reporter=reporter,
                )
            )
    obj = link(
        [o1] + obj,
        "firmware.mmap",
        use_runtime=True,
        reporter=reporter,
        debug=True,
    )

    with open("firmware.oj", "w") as of:
        obj.save(of)

    objcopy(obj, "flash", "elf", "firmware.elf")
    objcopy(obj, "flash", "bin", "code.bin")
    objcopy(obj, "ram", "bin", "data.bin")
    size = 0x8000
    cimg = obj.get_image("flash")
    dimg = obj.get_image("ram")
    img = merge_memories(cimg, dimg, "img")
    imgdata = img.data

with open("firmware.hex", "w") as f:
    for i in range(size):
        if i < len(imgdata) // 4:
            w = imgdata[4 * i : 4 * i + 4]
            print(f"{w[3]:02x}{w[2]:02x}{w[1]:02x}{w[0]:02x}", file=f)
        else:
            print("00000000", file=f)
