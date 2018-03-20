import sys
import os
import time

import core
import tools
import idc

reload(core)
reload(tools)

from core.objects import *
from core.project import *

print "Ready to rock!"

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

load_til(os.path.join(BASE_DIR, "behemoth.til"))

start_time = time.time()

# Turn any known GUIDs found into GUID structures
print "Updating GUIDs..."
tools.update_guids(os.path.join(BASE_DIR, "guids-db.ini"))

# At one point had EFI_SYSTEM_TABLE structure created outside the argument in
# an attempt to fix some error; not sure if that was actually needed.
print "Performing initial structure updates starting at entry point..."
tools.update_structs_from_regs(idc.GetEntryOrdinal(
    0), rdx=Structure("EFI_SYSTEM_TABLE"))

print "Updating structures from xrefs..."
tools.update_structs_from_xrefs()

print "Searching for EFI protocols..."
tools.update_protocols()

print "Updating structures from xrefs..."
tools.update_structs_from_xrefs()

print "Searching for EFI protocols..."
tools.update_protocols()

print "Updating structures from lvars..."
for protocol in filter(lambda x: x.interface is not None, protocols):
    if isinstance(protocol.interface.storage, StructureMember):
        start = protocol.introduced_at
        lvar = protocol.interface.storage
        struc = protocol.struc
        print "Working on %s %s at 0x%X" % (struc, lvar, start)
        tools.update_struct_from_lvar(start, lvar, struc)

for protocol in protocols:
    print protocol.name
    print "  GUID          : %s" % protocol.guid.as_uuid()
    print "  Interface     : %s" % protocol.interface
    print "  Introduced at : 0x%X" % protocol.introduced_at
    print "  Class         : %s" % str(protocol.__class__).split(".")[-1]

print "Finished in %f seconds" % (time.time() - start_time)
