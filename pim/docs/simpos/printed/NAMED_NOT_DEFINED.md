# Named in the reports but never defined there (deliverable 4)

Part 1 is a synthesis grouped by subsystem; each entry carries the report and PDF page where the name occurs.
Part 2 gives each report's raw list as its transcriber wrote it (from parts/*.undefined.txt), unedited.
"Not defined" means no held report prints a body, an interface or a format for it. Names that one report leaves
undefined but another defines are not listed here (for example `stream` and `channel`: TR-056 uses them, TM-100 prints them).
Caution: a definition in one report may not match usage in another. `semaphore` is the clearest case. TM-100 p17 uses
`:create(#semaphore, S, Limit)`, `:p_operation` and `:v_operation`, and its Fig. 3.9 has it inherit `waiting_queue`.
TR-056 p13 prints `:p`, `:v`, `:init` and `:init(S, Count)` over a stream of `token` atoms. The method names differ
(VARIANT), so TM-100's `semaphore` interface is effectively undefined.

## Part 1 -- synthesis

### Kernel and hardware interface
- `context` (hardware process context): `:create(#context, N, Stack, Ctx)`, `:get_number`, `:set_entry_point`,
  `:activate`, `:set_priority` (TM-100 p8-9). Its comment reads "Hardware PC«?»".
- `processor`, `area`, `disk`, `keyboard` (TM-065 p10, hardware/device classes, names only); the memory manager
  (TR-055 p6, TR-057 p5); the `collect-garbage/1` built-in, firmware only (TR-213 p4).
- Interrupt-process internals: the "%TRAP TO PROCESS ...", "%RELEASE PROCESSOR ...", "%ALLOCATE PROCESSOR ..."
  steps are elided in the print (TM-100 p12-13).
- `:inhibit_interrupt/:allow_interrupt(#process)`, `:clear_masks`, `:status/2`, `:entry_of_invoke`, `:die`,
  `:terminate` (TM-100 p8-11): called, but no body is printed (`:terminate(Process)` signature printed p5).
- `set_vector_element/3` and other KL0 built-ins (TM-100 p8).
- Device handlers (bitmap, mouse, keyboard, disk): interrupt processes with handler channels (TR-059 p30;
  TM-125 p4, p20-21). No interface is given.
- The PCB and "System Area" layout (TM-444 p35, OCR only).

### Supervisor
- Dispatcher and scheduler: "The dispatcher and the scheduler controls the states of processes" (TR-056 p18).
  Neither class is given, and the priority and sub_priority semantics are not stated.
- `with_link`, `waiting_frame`, `waiting_queue`, `post_queue`, `post_queue_for_message`, `message`
  (TM-100 p10-16): roles are stated, bodies are not.
- `list` operations `:add_last`, `:remove`, `:clear`, `:count`, `:get_first`, `:stick_tap` (TM-100). Pool and
  sequence interfaces are partly given in TR-056 p6-12.
- `process_clock`, Timer/clock management ("supports clocks and watches", TR-056 p31; TM-143 p2).
- `boot_process` / `as_boot_program`: prose only (TM-100 p13, TR-056 p21).
- The priority-stream mixin (TM-100 p7, TR-056 p14).
- `situation`, `event` (as exceptions), `error`, `warning`, `fatal error`, `normal error`, `help`
  (TR-087 p9-10, TR-285 p10). No methods are named.
- `user`, `group` ("must be defined", TR-056 p26); user management (TM-229 p3); password holder and ranks
  (TR-524 p16).
- `as_global_object` protection, profile, versions and lock ("still under consideration", TR-056 p26-27).
- `wildcard` (TM-229 p3), the system tracer (TM-143 p2, TR-087 p11), kana-kanji conversion (TM-143 p2,
  TM-229 p3).
- `as_resource`, `with_lock` (natures of the real `file`, TM-065 p13). The process `resources` list and the
  cleanup method called on each resource at termination (TR-285 p11): the method name is not given.

### Environment and library
- The `library` class API. Its class slots hold global objects (TR-056 p22); there is no method list. The
  methods known from usage are in `pim/docs/simpos/required/old_regex_census.tsv (superseded by simpos/required/)` (applications, not reports).
- File formats for the class template file, the class object file and the package template file
  (TR-057 p10, TM-143 p4, TM-785 p3).
- The external (public) class declaration syntax, and the package environment storage (TM-388 p93-94, OCR).
- `world` implementation (TR-056 p24-25; aliases, TR-524 p9); `universe` (TR-057 p5, TM-079 p11).
- The logical-name mechanism `me:` beyond its default (TM-143 p3).

### File system
- On-disk formats: volume descriptor, VTOC entry, region/page table, directory entry, free map. The
  page-table "last few entries" are next-level tables (TR-059 p6-10; TR-524 p9). The page size is 1 KB
  only per TR-524 p9.
- Physical file, physical directory and volume classes (TR-524 p10-11, unnamed); file manager internals;
  the disk cache ("simple LRU", TR-524 p9-10).
- `io_port`, the manager channel request/reply message format (TR-059 p29); the device port (TR-059 p31).
- `table_file` and permanent object file classes (TR-524 p9, one sentence each); `heap file` / `index file`
  bodies (TR-059 p17-20, interfaces only).
- The floppy disk file (TR-059 p32); magnetic tape (TM-229 p3); the binder (TR-059 p33).
- `:probe` (TR-524 p12); `with_retrieval`, `p_binary_file`, `p_logical_file` (natures in TR-524 App. A,
  not defined).
- `#binary_file_tap` (TM-065 p13); file version semantics beyond "latest on open" (TR-524 p9).

### Window system
- Which class defines each of the roughly 45 chapter-5 methods (TM-125 p13-19).
- The natures, slots and methods of 67 of the 69 catalogue classes (TM-125 p8-13).
- `window_manager`, `display`, `screen`, `status_line`, `logical_mouse`, `window_message`
  (format absent), `single_object` (TM-125 p8-13).
- The value sets for Line_type / Alu, menu item kinds, and `:create(#menu_item, Name, common, Kind, _, Item)`
  arguments (TM-125 p17; TR-046 p27).
- `with_display`, `as_inside`, `as_label` (natures used, TM-065 p15); `:get_size`, `:clear_rectangle`,
  `:start` (TM-065 p15).
- Key-code notation `control#"k"`, `mouse#l`/`mouse#1`, `mouse#rr` (TR-046 p28), and `:get_e_process`
  (TR-046 p26, p28).
- The window save area (TM-225 p14-15); the parent/child window part classes (TM-126 p5).

### Network
- 14 of the 16 ROAM classes (TR-283 p9); the controller-process protocol; the virtual line / stream
  interface; the status object class; the names of the redefinable proxy/freeze/extra methods (TR-283
  p8-9).
- Field widths and byte order; the meaning of `*`/`#` in the tag codes; GOID encoding (TR-283 p20-21).
- The network manager and session layer (TR-283 p10, TR-524 p18); node, socket, plug, cable, remote
  channel (TR-055 p20-21, TR-057 p7); `as_pervasive_object` (TR-056 p28-31).
- LIA and NCP protocols, the 32-bit process-address layout, the process symbolic-name file format, the
  "message object" class (TM-401 p5-8).
- TELNET and FTP: TM-430 p3 (status "fetched", not "held") says ftp and telnet were being prototyped as SIMPOS
  extensions on a TCP/IP socket interface that "provides each TCP/IP function in the form of methods". It gives
  no class or method names. No other report found names them, judging from a grep of all OCR text plus the eyed
  pages. IPSJ papers on TELNET and FTP are held in `nonlocal/lit/ipsj/` (psi_acquisition.md section 5), but they
  are outside the trtm/ scope of this pass and were not read. File transfer (PSI-PSI, PSI-VAX), the DDX gateway and mail
  are prose only (TM-181 p5, TM-401 p9-10).

### Boot and programming system
- The IPL module list and format, the floppy layout, and the CSP boot region (TR-059 p32-33, TR-087 p11,
  TR-086 p10, TM-143 p6-7).
- The order in which subsystems are instantiated during boot (TR-059 p30, p32 say only "during a system
  boot-up procedure").
- The debugger, interpreter, editor (Edips, PMACS), transducer, symbolizer, librarian, listener/shell,
  spooler, font editor, inspector, call counter and window/file/network manipulators: named and
  described, but no classes are printed (TR-057 p8-10, TM-143, TM-181, TM-229).
- `e_process_pool`, `e_program`, `e_window`, `e_port`, `whiteboard`, `coordinator`: the class graph only
  (TR-061 p12).

## Part 2 -- per-report raw lists

### ESP-manuals
```
ESP-manuals	package environment with_simpos	PROSE	semantics given; storage format absent
ESP-manuals	external (public) class declaration syntax	PROSE	named, syntax not captured in OCR
misc	System Area / PCB layout	ABSENT	TM-444 says PCBs live there
misc	PSI/UX interface memory protocol	PROSE	TR-714
```

### TM-009
```
TM-009	fork/join (!!) and remote call (@)	PROSE	not seen in any later report (others to confirm)
TM-009	surrogate process	PROSE	implicit process created for a remote call
TM-009	source/sink port	PROSE	later "i/o port" (TR-055)
```

### TM-143
```
TM-143	clock management (時計管理)	PROSE	date/time/alarm/stopwatch; no class names
TM-143	kanji processing (漢字処理)	PROSE	kana-kanji conversion; no interface
TM-143	call counter (コール・カウンタ)	NAMED	per-predicate call counting tool
TM-143	me: logical name	PROSE	logical-name mechanism for directories; syntax beyond "me:" absent
TM-143	generalist?, terminal?, shell?	NAMED	system-menu screenshot items, low-confidence reading
TM-143	floppy load format	ABSENT	LSI-11 writes floppies, PSI loads them
```

### TM-153
```
TM-153	netcp	NAMED	network tool in menu
TM-153	ncp_manipulator	NAMED	network manipulator
TM-153	component (slot keyword)	PRINTED	older ESP keyword, semantics vs attribute not stated
```

### TM-181
```
TM-181	spooler	NAMED	expert in system menu; no description
TM-181	kanakan initiate	NAMED	media-system menu item
TM-181	garbage collection (menu item)	NAMED	media-system menu item; GC algorithm not described
TM-181	user process list	NAMED	menu item
TM-181	file version numbers name.type.N	SCREENSHOT	semantics not described
TM-181	DDX gateway	PROSE	protocol absent
```

### TM-225
```
TM-225	window save area	FIGURE	per-window save area in Fig. 5; structure absent
TM-225	user / clock management	NAMED	supervisor components
```

### TM-229
```
TM-229	wildcard function	NAMED	supervisor component, no interface
TM-229	user management	NAMED	supervisor component
TM-229	magnetic tape, printer subsystems	NAMED	I/O media, no interface
TM-229	text buffer	NAMED	figure label only
TM-229	system debug tool, inspector	NAMED	figure label only
TM-229	Escher, Oekaki, Queens, Squares, Bounce	NAMED	demo programs in system menu
```

### TM-401
```
TM-401	LIA protocol	CITED	ICOT LIA interface spec 1985 (ref [3]); not given
TM-401	NCP protocol	ABSENT	frame/packet formats not given
TM-401	32-bit process address layout	ABSENT	-
TM-401	process symbolic name file	PROSE	format absent
TM-401	message object	PROSE	class name/slots absent
```

### TM-785
```
TM-785	package_template_file	NAMED	librarian file kind; format absent
TM-785	fdd/1 librarian command	PRINTED	command only; .com file format absent
TM-785	list_index	NAMED	system class used by application (OCR)
```

### tm0061
```
# TM-061: names used in the printed listings but not defined in the report
:new/1 (class method, called as :new(Class,Obj))       PDF p6, p8   -- built-in object creation (ESP; INFERENCE)
:retrieve/2 (class, called :retrieve(Class,File,Pathname)) PDF p6
:get-size/2 (printed :ge«?»-size)  (:get-size(Window,Width,Height))           PDF p8
:clear-rectangle/4                                       PDF p8
:start/0                                                 PDF p8
#binary-file-tap  (class)                                PDF p7
with-display, as-inside, as-label  (natures)             PDF p8
as-permanent-object, as-resource, with-lock (natures of real file) PDF p6 (listing comment)
bodies of :create-file, :open/0, :close, :dispose, :read, :write, :draw-border, :draw-label, :clear-label  ('...' in original)
```

### tm0065
```
# TM-065: names used in the printed listings but not defined in the report
:new/1 (class method, called as :new(Class,Obj))       PDF p12, p15   -- built-in object creation (ESP; INFERENCE)
:retrieve/2 (class, called :retrieve(Class,File,Pathname)) PDF p12
:get_size/2  (:get_size(Window,Width,Height))           PDF p15
:clear_rectangle/4                                       PDF p15
:start/0                                                 PDF p15
#binary_file_tap  (class)                                PDF p13
with_display, as_inside, as_label  (natures)             PDF p15
as_permanent_object, as_resource, with_lock (natures of real file) PDF p13
bodies of :create_file, :open/0, :close, :dispose, :read, :write, :draw_border, :draw_label, :clear_label  ('...' in original)
```

### tm0079
```
# TM-079: concepts named, no interface given (all TRANSLATION of handwritten Japanese)
program class / main goal instance predicate      p10
pool tap; stream; channel; port; world; universe; directory   p10-11
node / socket / plug / cable network classes (identifiers not given)  p13
remote object / remote channel                     p13
e_window, e_port, whiteboard (coordinator)         p14-15
key commands / special commands of coordinator     p14
class template file / class object file formats    p17
transducer (parser + pretty printer)               p16
IPL bootstrap; firmware GC support                 p9-10
```

### tm0100

# TM-100: names used but never defined in the report (PDF page)
with_link (p7,p10) -- role stated, no definition
waiting_frame (p7,p10,p14) -- role stated
waiting_queue (p14) -- "doubly-linked list"; methods :hook :unhook :empty used, not defined
post_queue (p14) -- :add_object :remove_object used
post_queue_for_message (p15)
message (p16) -- :set_sender :get_sender :copy used
semaphore (p17) -- :p_operation :v_operation, :create(#semaphore, S, Limit) used
context (p8) -- :create(#context, Context_number, Stack_number, Context), :get_number, :set_entry_point, :activate, :set_priority
list (p8) -- :add_last :remove :empty :clear :count :get_first :stick_tap; and the "tap" object it returns (:get(Tap, A_port))
process_clock (p8)
window (p10) -- :create :activate :read :write; etx character
boot_process (p13), as_boot_program (p13) -- prose only
Pool, World, Timer, Printer, Network subsystems (p5, Figure 2.1)
process methods called but not printed: :status/2 ":status(Process, dormant, on_activate)", :entry_of_invoke/1,
  :clear_masks/0, :inhibit_interrupt/0, :allow_interrupt/0 (class methods on #process), :self(#process, P),
  :add_child/1, :add_program/1, :remove_program/1, :no_program/0, :die/0 (arity excludes receiver).
  :terminate(Process): signature printed p5, body not printed
set_vector_element/3 (p8; plain predicate, all args) -- a built-in (no colon), not defined
port :connect/:disconnect (p7) -- signatures printed p7, bodies not printed; p16 port class has no connect body
"priority control" stream variation (p7)

### tm0430

TM-430	ftp, telnet (SIMPOS extensions)	PROSE	prototyped; no design given (p3)
TM-430	socket interface class and methods	PROSE	names absent (p3)
TM-430	CIOP, XVLAN, C bus	PROSE	hardware named only

### tm0125
```
# TM-125: names referenced but not defined (no source/definition in the report)
All 69 catalogue classes: role sentence only, no natures/slots/methods (except as_relation->as_superior, logical_mouse->single_object).
Which class defines each chapter-5 method                              PDF p13-19
:select/0 (:select(Window), receiver only)  -- named in 6.2 prose only                PDF p22
Table 1 option semantics beyond one-line descriptions                  PDF p13-14
Line_type, Alu value sets for draw_line/draw_rectangle/draw_string     PDF p17
item_type values for menu/choice items (on_off named via as_on«?»off_menu) PDF p12, p14
window_message format (inter-process message between user process and window manager) PDF p13
kana-kanji translation module interface (Fig 1)                        PDF p4
device handler interfaces (bitmap display, mouse, keyboard handlers)   PDF p4, p20-21
fact example: :stick_index_t«…», #list_«…», :add_«?»t, stack_vector, first, make_list (hidden/undefined) PDF p23
```

### tm0126
```
# TM-126: named but not defined
parent-window / child-window part classes (no identifiers)              PDF p5
rectangle-partition data structure (only Fig 2 worked example)         PDF p5
fully-visible state flag (name/representation)                         PDF p7
session-management (saved debugger command sequences) interface       PDF p7-8
Debugger Menu items' semantics (Change State, Control Menu, From/To Whiteboard, From Last Input)  PDF p6
file_manipulator menu items' semantics (undelete, expunge, purge ...)  PDF p6
debugger ports unify/pick/next/miss (meaning not given here; cf. TM-079 p15 box model)  PDF p6
```

### TR-046
```
# Names used in TR-046 but never defined there (PDF page)
:get_e_process/1 (method on Window returning the expert process) -- called in every translation-table clause, p26, p28
make_from_to/2 (local predicate; Directory -> Experts_list) -- p27
:get_invariant_part/1 body shown only partly (elided) -- p27
#coordinator (destination object/class of meta-commands) -- p26, p28
control#"k", mouse#1/mouse#l, mouse#rr (key-code notation; encoding of control#, mouse# not given) -- p26, p28
:create(#menu_item, Name, common, Kind, _, Item) -- meaning of 'common' and the 5th argument not given -- p27
#multi_column_menu, #list (:add_first, :add_last) -- p27
System_menu!window slot (not declared in the printed class; only menu_list is) -- p27
e_window, e_program, e_process, e_process_pool, whiteboard (prose only) -- p14-16
"the menu classes" -- p15
move_window, select_window, reshape_window -- p09
window manager (as distinct from window system) -- p16
```

### TR-055
```
TR-055	VTOC	PROSE	volume table of contents built as an instance file; layout absent
TR-055	region page map	PROSE	per-region logical->physical page map; layout absent
TR-055	manager message protocol	ABSENT	request/reply through manager port; no formats
TR-055	remote object encoding	ABSENT	"each class knows how to encode and decode"
TR-055	listeners, analyzers	NAMED	experts named only
TR-055	Fifth generation kernel language version 0	CITED	ICOT internal document June 1983 (ref [2])
```

### TR-056
```
# Names used in TR-056 but never defined there (PDF page)
:next/2 on pools (only its signature) -- p12
:position/1, :pool/1, :set_position/1 on tap (used in the :get body only) -- p12
token (atom put into semaphore streams) -- p13
dispatcher, scheduler, ready queue (no policy, no priorities) -- p18
hardware process environment: register set, stack group, heap memory -- p19
trap handlers, device handlers, garbage collector (as interrupt processes) -- p20
library class/operations (only "holds a collection of classes") -- p22
user, group ("must be defined") -- p26
protection seals, profile, version, object lock -- p26
instance file, record pointer, directory file, file marker (deferred to the file system report) -- p27-28
node, network manager, object table, object number, operation identifier -- p29
timer: clocks and watches (11 classes, 600 lines, "not discussed") -- p31
i/o medium systems (window, file) -- p04, p17
```

### TR-057
```
TR-057	list	NAMED	class named only as an example of a pool
TR-057	array	NAMED	same
TR-057	node, socket, cable, plug	NAMED	network classes, no definition
TR-057	binder mechanism	PROSE	"will be supported": virtual file of many data and index files
TR-057	table file, heap file, index file, instance file, directory file	PROSE	file types named without class names or interfaces
TR-057	universe	PROSE	system directory tree held in a class slot of class directory; slot name not given
TR-057	Customisable Assembler	CITED	S. Takagi 1983
```

### TR-059
```
# Names used in TR-059 but never defined there (PDF page)
disk (object; "responsible to the device management of the kernel") -- p06
volume descriptor, VTOC entry, region descriptor, file descriptor -- formats not given -- p06-08
page size / page table entry count / "the last few entries" -- p09
KL0 integer vector and string (buffer contents) -- p11
:decode/1, :encode/1, :instance_file/1 (per-class conversion) -- p22
:object_class/1 on instance file; :file/1, :file_marker/1 on record pointer; #record_pointer :create -- p22
io_port ("a special type of port") -- p29
manager channel / handler channel message formats -- p29-31
device handler (interrupt process) internals -- p30
system boot-up region, CSP programs, PSI firmware programs, IPL -- p32-33
floppy disk files -- p32
file manipulator, binder, file class coercion -- p33
user and node objects -- p04
```

### TR-061
```
# Names used in TR-061 but never defined there (PDF page)
:get_e_process/1 -- p13
with_goal_demon, e_program_core, help_info_dictionary, inter_process_port -- named only in Fig.1, p12
list_index, cascade_index -- p05
e_program_directory -- p05
'key-command_table-change' command -- p09
history table (memorize/remember) -- p08
"special port maintained by the window manager" -- p06
read_from_whiteboard, write_to_whiteboard, system_menu_invoke (meta-command names differ from table atoms read/write/invoke_system_menu) -- p06 vs p13
create meta-command (no key binding in the printed table) -- p07
```

### TR-086
```
TR-086	bind-hook, exception-hook	PROSE	KL0 operations named, not specified here
TR-086	IPL module list	ABSENT	"included many modules of the kernel operating system and also run-time support routines of ESP"
TR-086	ICOT-Net	NAMED	LAN; protocol not given
```

### TR-087
```
TR-087	event/situation methods	PROSE	no method names printed
TR-087	read_console, display_console	NAMED	KL0 built-ins used by the runtime support; signatures not given
TR-087	system tracer	PROSE	Sato et al. 1984 cited
TR-087	IPL flexible-disk format	ABSENT	Ueda et al. 1984 cited
```

### TR-213
```
TR-213	collect-garbage/1 ProcessTable format	ABSENT	built-in argument structure not described
TR-213	real-page management stack	PROSE	kernel structure; layout absent
```

### TR-285
```
TR-285	situation stack operations	PROSE	no method names
TR-285	resource-release method	PROSE	name not given
TR-285	CIL	CITED	situational-semantics language using bind_hook
```

### tr0283
```
# TR-283: names used but never defined in the report (PDF page / folio)
remote_object, as_remote_object      p9/f7   (kernel classes; prose only)
the other 14 of the 16 ROAM classes  p9/f7   (categories only: remote object kernel, message, process-related, others)
controller process                   p4/f2   (protocol not given)
server process / client process      p4/f2
virtual line object                  p5/f3   ("external stream with the synchronization function", from the communication system)
status object                        p8/f6
packet pool                          p6/f4
library subsystem                    p5/f3   (Table 4: class library :get_class_object/c2)
package, class complete name         p5/f3
class symbolizer                     p18/f16 (:get_atom_string/c2, :get_atom/c2, :enter_atom/c2)
network manager, handler             p10/f8  (process levels)
LIA/LIB hardware controller          p10/f8
built-in predicate method_call       p12/f10
:g_call, :l_call, :r_call            p9/f7   (prose; bodies not printed)
proxy object creating method; internal state freezing/melting methods; extra field handling methods   p9/f7 (no names)
object_category slot                 p4/f2   (declaring class not stated)
GOID encoding                        p6/f4   (components only; printed as "N2T1P21" in figures)
GMID format                          p6/f4, p20
tag codes with '*' and '#'           p20/f18 (X'0*0#, X'0*60, X'0*80 -- meaning of * and # not defined)
short vs long tag forms              p20/f18
"exhausted GC" (mark and sweep)      p12/f10
DDX global network                   p3/f1
:make/c2 :write/i2 :read :size/i1 :close/i0 ; :expunge/i0 :find/i2 :delete/i2 :undelete/i2 :add/i2   p18/f16 (Table 3; classes not named)
```

### tr0524
```
# TR-524: names used but never defined in the report (PDF page / folio)
# Classes / natures named without any definition
p_binary_file                 p37/f36  (nature of binary_file)
with_retrieval                p37/f36  (nature of binary_file)
p_logical_file                p37/f36  (nature of logical_file)
as_agent_of_physical_file     p37/f36
as_resource                   p37/f36
as_file                       p37/f36
with_file_capability          p37/f36
as_agent_of_physical_object   p37/f36  (nature of logical_object)
with_capability               p37/f36
with_internal_communication   p37/f36
with_access_status            p37/f36
remote_object                 p37/f36  (ROAM kernel class; prose only p20)
as_remote_object              p38/f37  (ROAM kernel class; prose only p20)
#pathname                     p37/f36  (:remote_or_local/5 called on it)
#directory                    p37/f36  (:retrieve/3 called on it; method list in Table 3 p36)
#table_file                   p11/f10
process / file manager process / network manager / device handler   p8,p11,p20,p29 (prose)
physical file / physical directory / physical volume objects        p10-18 (prose and figures; no class names)
user management system        p10/f9
world (alias set)             p9/f8, p22/f21
# Methods called but never defined
:g_call/2,/3 (Lfile, Name, {Args}[, Node])   p37  -- ROAM, defined only in prose
:r_call, :x_call              p20-21 (prose, Fig.4)
:send_receive/4 (Lfile, OpType, InternalMethod, {Args}, RequestMode)   p37
:submit/5 (Lfile, OpType, InternalMethod, {Args}, RequestMode, MsgID)  p37
:wait/2 (Lfile, MsgID, {Buffer,Marker})   p37   (low level; distinct from binary_file :wait/3)
:probe                        p12 (prose only)
:interface/2 (Lfile, Pfile, Status)       p37
:mode_type/2                  p37
:set_full_pathname/1          p37
:remote_or_local/5            p37
:retrieve/3 on #directory     p37
:open/3 on Pfile (Pfile, OpenMode, Lfile, Status)    p37
:add/3, :read/3 on Pfile (with AccessStatus)          p37
:set_accessor/1               p38
:buffer/1, :file_marker/1     p38 (presumably slot accessors of file, file_marker, buffer -- INFERENCE)
:get_io_buffer/2, :set_io_buffer/2, :copy_data_buffer/2, :get_data/1 on buffer   p38
:set_data_element/1, :get_data_element/1 on Packet   p38
:new/1 (built-in instance creation)      p38
unbound/1 (built-in predicate)           p38
:close, :make on logical files           p12 (no body)
# Concepts
request_input / reply_input (attribute delivery types)   p38
message identifier / MsgID format        p12
GOID ([node#, creationtime])             p35 Table 2
express / normal message priority (encoding)   p15
abort message                            p15
I/O bus memory, LRU cache                p9
super_U / super_A / super_N / general ranks; user mode   p16-17 (semantics given, storage not)
password holder (storage format)         p16
```
