# ESP: what the language does, at the level a compiler needs

Scope: the language SIMPOS is written in, as far as the held sources define it.
Each claim is marked **KNOWN** (printed in a source, cited), **MEASURED** (seen in held
binaries or source), or **UNKNOWN**. OCR-only readings, where the printed character could
not be checked against a page image, are marked *(OCR)*.

## 0. Sources and which dialect is normative

| Key | Document | Where held | Page convention |
|---|---|---|---|
| TR-044 | Chikayama, *ESP Reference Manual*, Feb 1984 | `simpos2/ocr/tr0044` | PDF page = printed + 4 |
| TM-388 | Uchida, *ESP Guide*, Aug/Sep 1987 | `simpos2/ocr/tm0388` | PDF page = printed + 12 |
| PRG | SIMPOS *ESP programming manual*, English TeX (c.1990) | `C/x/esp/program-e.tex` (`.flat` = line-numbered) | TeX line numbers |
| OVW | SIMPOS overview manual, English TeX | `C/x/esp/overview-e.tex` | TeX line numbers |
| TH | Nakashima, doctoral thesis (PSI-I/II/III) | page images `C/x/thA/` | PDF page ≈ printed/2 + 4 |
| TR-005 | 1983 pre-object ESP/KL0 report | `C/ocr/tr0005` | PDF pages |
| SRC | 83 held `.esp` files of PIMOS `paragraph` | `C/x/para/pimos/src_util/paragraph/` | file:line |

**Normative dialect: TM-388 together with PRG.** These describe the late ESP of 1987–1990, which
is the dialect of the held SRC and `.ptf` files. MEASURED: SRC uses
`add_operator((::),xfx,90).` (as_pred.esp:3, g_dev.esp:3), `remove_operator` (dev.esp), `pkg##class`
and `!slot` access. TR-044 is the 1984 dialect; its differences are listed in §11.

## 1. Lexis and terms (KNOWN, TM-388 §2.5 pp.25–27; TR-044 pp.10–14)

- **Terms** are Prolog-like: atoms, variables, integers, floats, strings, vectors and compound terms.
- **Integers** are 32-bit. 64-bit arithmetic is done by the `_extended` built-ins.
- **Floats** are 32-bit on PSI (8-bit exponent, 24-bit mantissa).
- **Vectors.** `{a,b,c}` is a vector. A compound term `f(a,b)` is the vector `{f,a,b}`.
  An operator term is the same as its compound term.
- **Lists.** `[X|Y]` is the 2-vector `{Y,X}`, **cdr first**. So `[1,2|X]` = `{{X,2},1}`, and `f(a)`
  unifies with `[a|f]` (TM-388 p.26). A compiler and any term reader must keep this layout:
  no separate list cell exists at the language level. TH App C names a `list` tag, so the machine
  may still tag 2-vectors specially (UNKNOWN whether the PSI-III builds them as `vect` or `list`).
- **Strings** have 1-, 8-, 16- or 32-bit elements (TM-388 p.27). TR-044 pp.10-14 writes them
  `bits:"..."`, `bytes:"..."`, `double_bytes:"..."`. PRG line 7131 gives the constant macros
  `word#`, `double_bytes#`, `bytes#`, `bits#` applied to a vector. The 32-bit literal spelling
  is UNKNOWN. A plain `"..."` holds 16-bit JIS characters on PSI: PRG line 7129 says `jis#` is
  unnecessary on PSI. MEASURED: SIMPOS text files are 16-bit JIS (FORMATS.md §5).
- **Character and constant macros**: `#"c"`, `Radix#"digits"`, `key#name`, `ascii#name`, and others (§7).

## 2. Source file (KNOWN, TM-388 §3.9 pp.90–93)

A source file is a sequence of statements, each ending with a period. A statement is one of:

- a class definition (§3);
- a macro bank (§7);
- `add_operator(Op,Type,Priority).` or `remove_operator(...)`;
- `use_macro(Bank).`;
- `use_package(Pkg).`;
- `include("file").`

## 3. Class definition (KNOWN, TM-388 ch.3; grammar TM-388 App A pp.137–141)

```
class Name [with_macro Bank] has
    [nature C1, C2, ..., Cn ;]          % superclasses; '*' marks self
    { class-slot declarations ; }
    { class clauses }
  [instance
    { instance-slot declarations ; }
    { instance clauses } ]
  [local
    { local clauses } ]
end.
```

- **Clauses end with `;`, not `.`,** inside a class (TM-388 App A; SRC throughout, e.g.
  `:putf(W,F):-!, :putf(W!win,F);`). So a body disjunction must be written in parentheses:
  `(G1 ; G2)`. Method heads are `[before:|after:] :name(Obj, Args...)`; local heads are
  `name(Args...)`.
- **Method kinds.** A method is a class method if it appears before `instance`, otherwise an
  instance method. Locals are visible only inside the class.
- **Operators.** Priorities are the PRG table (§8).

**Grammar, transcribed from TM-388 App A pp.139-141 (pdf 151-153).** The OCR is checked against
SRC usage. The lexical part (pp.137-138) is too garbled in OCR to transcribe: read the page images.

```
class-def   ::= "class" class-name {"with_macro" bank-id} "has"
                [ "nature" inh {"," inh} ";" ]
                { slot-def ";" } { method-clause ";" }
                [ "instance" { slot-def ";" } { method-clause ";" } ]
                [ "local" { clause ";" } ]
                "end" "."
class-id    ::= class-name | package-name "##" class-name
inh         ::= class-id | "*"
method-clause ::= [ ("before"|"after") ":" ] clause
clause      ::= head [ ":-" body ]
body        ::= goal-list
goal-list   ::= goal-list "," goal-list | "(" goal-list {";" goal-list} ")" | goal
goal        ::= ":" term                      % usual method call
              | class-id ":" term             % class method of named class
              | ":" class-id ":" term         % instance method of named class
              | term                          % predicate call
slot-def    ::= ("attribute"|"component") item {"," item}
item        ::= slot-name [ ":=" term | "is" class-name ]
              | "(" slot-name ":=" term ":-" goal-list ")"
bank-def    ::= "macro_bank" name ["with_macro" bank-id] "has" ["nature" ... ";"]
                { slot-def ";" } { macro-def ";" } ["local" { clause ";" }] "end" "."
macro-def   ::= pattern "=>" expansion ["when" goals] ["where" goals]
                  ["with" { clause ";" }] ["by" Var] [":-" body]
              | pattern "==>" ...        % class-level macro (same tail)
              | ("inserta"|"insertz") "(" ("c"|"i"|"l") "," { clause ";" } ")"
```

## 4. Inheritance (KNOWN; the rule changed between dialects)

**Late rule** (TM-388 §3.2 pp.38–39), normative:

- Linearisation is depth-first over the `nature` list. The first occurrence wins.
- The class itself is placed where `*` appears, or **first** if `*` is omitted.
- Every class implicitly inherits class `class` (§6).

Worked examples (TM-388 p.39) that a test suite must reproduce:

- ex1 → ex1, a, a1, a2, b, b1, b2.
- `nature a,c` → ex2, a, a1, a2, c, b1.
- `nature a,*,c` → a, a1, a2, ex3, c, b1.

Constraints: supers must be defined first, and cycles are illegal (TR-044 IV.4 p.17).

**Where the linearisation is computed.** MEASURED: the `.ptf` template trailer stores only
`[self, declared natures...]`, for example `[self, simpos##as_graphics, reshape_notifier, ...]`
(FORMATS.md §2). KNOWN (TH App A p.244): on the PSI line, inheritance is resolved statically
at program **load** time ("a kind of dynamic link"). So the linearisation is done by the
SIMPOS loader/librarian, not by the compiler. It must be reconstructed as part of the loader.

## 5. Methods and demons (KNOWN, TR-044 pp.18–21; TM-388 §3.3–3.4 pp.40–47)

- **Predicates per name.** Each (name, arity) in a class may have one primary, one `before` and
  one `after` predicate.
- **Combination.** Over the linearised classes, a call `:m(Obj,...)` runs:
  1. every before-demon, in inheritance order, ANDed;
  2. then the primaries as **alternatives** (OR) in inheritance order;
  3. then the after-demons, ANDed.
- **After-demon order (CONFLICT, unresolved):**
  - TR-044 p.20 says reverse inheritance order.
  - TM-388's worked example `:get :- b1,b2,b3,(p1;p2;p3;fail),a3,a2,a1` (p.42) is also reverse,
    but its prose says "in the order of inheritance".
  - TH p.243 prints `a0..an` (forward).
  - The `.ptf` cannot settle this, because combination is built at load time.
  
  Recommendation: implement reverse order (two sources, one of them a worked example), and keep
  it switchable until a running SIMPOS trace or loader code settles it.

  *2026-11-23:* the TM-388 page image (PDF p.54) settles the in-TM-388 point. It continues:
  "After-demon means post-processing, and what is first inherited is executed last." So TM-388
  is consistent. The conflict is TM-388 and TR-044 against the thesis. Implemented as a switch,
  default reverse, in `pim/psi/librarian.py`.
- **Cut.**
  - An after-demon may prune the remaining primary alternatives with `relative_cut(1)`.
  - `!` = `relative_cut(0)`, and cut prunes only to the enclosing OR, unlike Prolog (TM-388 ch.4).
  - TH p.244: PSI-II/III compile a method as `m :- load_choice_point(C), p(C)`, and a cut inside a
    primary becomes `method_cut(C)`. It must prune the *other classes'* primaries too.
- **Call forms.**

  | Form | Meaning |
  |---|---|
  | `:m(Obj,A...)` | Dispatch on the first argument: a class object selects class methods, an instance selects instance methods |
  | `Class:m(ClassObj,...)` | Class method of a named ancestor |
  | `:Class:m(Inst,...)` | Instance method of a named ancestor |
  | `:refute(Obj, Name, ArgVector)` | Dynamic call (TM-388 p.46) |
  
  Built-ins `method_call` and `overridden_method_call` exist (TM-388 App D).
- **Missing method or slot.** The call goes to `:undefined_method(Obj,Name,ArgVec,Addr)` or
  `:undefined_slot(Obj,Type,Name,Value,Addr)` (TM-388 §3.6).
- **Indexing** (TM-388 §5.5 pp.134–135):
  - Locals index on argument 1, methods on argument 2 (argument 1 is the object).
  - A stack vector indexes on its first element.
  - Indexing stops at the first clause with a variable in the indexed position.

## 6. Slots and class `class` (KNOWN, TM-388 §3.5–3.6 pp.48–61)

**Slot kinds.** A slot is either an `attribute` or a `component`. Initialisation forms:

- `name := Term`;
- `name is Class` (instance slots only: creates an instance);
- `(name := V :- Goals)`.

Initialisation runs as an after-demon of `new`. MEASURED: these compile to kind-0x22/0x32
predicates, e.g. `display_pos/1` in `time_graph_window` from p_tgraph.esp:81.

*2026-11-24, witnessed and run (`pim/psi/kl0.py`, `test_kl0.py`):*

- **Calling convention** (MEASURED). All 424 initialisers in the eleven packages have arity 1.
  There is no receiver argument, and the value comes back in A0.
- **Semantics** (TM-388 §3.5 pp.49-50, page images).
  - Instance slots are filled when `new` makes the instance. Class slots are filled "when the
    class is generated".
  - A failing initialiser makes `new` fail, or leaves the class not generated.
  - The order of the initialisers "is uncertain".
  - An initialiser cannot use the object being made.
  - For work that needs the object, TM-388 recommends an after-demon of `new`, whose second
    argument "has already been unified with the instance object".
  - `slot is Class` stores a new instance of Class (p.49).

**Rules:**

- Attributes of the same name collapse to one slot, and the first initial value in inheritance
  order wins.
- Components are private per class and are renamed to a class-specific identifier when written
  statically.
- A dynamic slot name reaches attributes only.
- A slot may hold atom, integer, float, string, heap vector or object. It may **not** hold an
  unbound variable or a stack vector (TM-388 p.133). Use `freeze`/`melt` to store terms.

**Access.** `Obj!slot` reads a slot and `Obj!slot := V` writes it (standard macros). They expand to
`get_slot`/`set_slot` or to the `slot`/`set_slot` built-ins. MEASURED: `blt 27` reads a slot by
atom; see KL0.md.

**Class `class` methods** (TM-388 §3.6):

- On both class and instance: `get_slot`, `set_slot`, `method`, `slot`, `is_class`, `refute`,
  `class_object`, `undefined_method`, `undefined_slot`.
- Class only: `new`, `package_name`, `class_name`, `class_id`, `super`.
- `get_slot`/`set_slot` take no principal predicate and no demons.
- `new`, `super` and `class_object` may have demons but no principal predicate.

## 7. Macros (KNOWN, TM-388 §3.7 pp.62–79; PRG lines 6972–7260; TR-044 ch.VI)

**Rule form:**

```
Pattern => Expansion [when Gen] [where Check] [with Clauses] [by Var] :- Cond
```

**Placement of the generated goals:**

- In a goal: `Gen`, then the goal, then `Check`.
- In a head: `Check` first; `Gen` goes after the last body goal. This defeats tail-recursion
  optimisation (TM-388 p.66).

**Expansion behaviour:**

- Expansion is top-down only.
- A backquote suppresses one level; a double backquote suppresses all levels.
- `==>` writes class-level macros.
- `inserta`/`insertz(c|i|l, Clauses)` add clauses to the class, instance or local part.

**Macro banks:** `macro_bank N [with_macro M] has [nature...;] ... end.` Every bank inherits
`esp_macro_expander`, which provides `expand_clause/5` and `expand_goals/3`.

**Standard macros** (TM-388 App C pp.143–144):

| Group | Macros |
|---|---|
| Slot access | `Obj!S`, `Obj!S := V` |
| Class object | `#Class`, `#pkg##Class` |
| Comparison | `=`/`is` → unify; `==` → equal; `=:=` → identical; `\==`, `=\=`, `<`, `=<`, `>`, `>=` |
| Arithmetic (in `is`) | `+ - * / mod div xor /\ \/ \ << >>`; `div`/`mod` use `divide_with_remainder` |
| Constants | `key#`, `pf#`, `mouse#`, `control#`, `meta#`, `ascii#`, `words#`, `double_bytes#`, `bytes#`, `bits#` |
| Other | `unique_atom`, `standard#input`/`output`/`message` |

PRG lines 6972-7200 give the expansions. A macro in a goal becomes the generating predicate:
`Z = X + Y` gives `add(X,Y,Z)`, `X = Obj!elem` gives `slot(Obj,elem,X)`. Arithmetic maps to
`add`, `subtract`, `multiply`, `divide`, `divide_with_remainder(X,Y,Q,_)`/`(X,Y,_,R)` and
`minus`; the bit operators map to `and`, `or` and so on.

Comparison mappings, as printed in PRG lines 7161-7168:

| Source | Predicate |
|---|---|
| `X == Y` | `equal` |
| `X \== Y` | `not_equal` |
| `X =:= Y` | `identical` |
| `X =\= Y` | `not_identical` |
| `X < Y` | `less_than(X,Y)` |
| `X =< Y` | `not_less_than(X,Y)` |
| `X > Y` | `less_than(Y,X)` |
| `X >= Y` | `not_less_than(Y,X)` |

The `=<`/`>=` rows look swapped. They are recorded as printed. **Settled against compiled code
(2026-11-24): the print is swapped.** `X =< Y` compiles to `not_less_than(Y,X)` (blt 67 with Y
first) and `X >= Y` to `not_less_than(X,Y)`. The witness is p_icon.esp `Y =< Icon!height/2`: the held
cells of `paragraph##predicate_num_switch_icon` are `67 03 01`, with A3 = height/2 and A1 = Y
(`../../../psi/kl0_opcodes.tsv`, row blt 67). `psi/espc.py` compiles it that way. Its cells for
that `$or$` run to the answers the source predicts (228 → inc, 229 → dec;
`psi/test_espc.py`). An injection that drops the swap fails those tests. `<` and `>` agree with
the print.

The compiler also follows TM-388 p.66 on head macros, quoted above: a slot or arithmetic
expression in a head becomes a fresh variable, unified after the last body goal. Held
`paragraph##list_index_buffer count/2` (`:count(Obj,Obj!count):-!;`: the neck cut, then the slot read and the unification) is compiled that way, and
`espc.py` matches its cells exactly.

Collation rules are in PRG lines 7173-7179. The key names are `abort`, `help`,
`bell`, `cr`, `del`, `esc` (line 7117), and pf keys are 1-18. The full special-key code values
are **UNKNOWN**.

## 8. Operators (KNOWN, PRG lines 7816-7853; registration lines 7857-7903)

Prolog-style types, priorities 0-1200. Decoded from the raw TeX: JIS escapes by hand, and
`\(<\)` is math-mode `<`. The table ends with `\cline` at line 7852, so it is complete as printed.

| Op | Type | Pri | Op | Type | Pri |
|---|---|---|---|---|---|
| class | fx | 1180 | spy, cspy, nospy | fy | 900 |
| has | xfx | 1160 | `\+` | fy | 900 |
| instance | fx, xfx | 1155 | `=..` | xfx | 700 |
| local | fx | 1154 | `@<` `@>` `@=<` `@>=` | xfx | 700 |
| `;` | xfy, xf | 1150 | `+` `-` | yfx, fx | 500 |
| `\|` | xfx | 1150 | `/\` `\/` xor | yfx | 500 |
| with_macro | xfx | 1140 | `*` | yfx | 400 |
| before, after | fx | 1140 | `/` `<<` `>>` div | yfx | 400 |
| nature, component, attribute | fx | 1120 | mod | xfx | 400 |
| `:-` | fx, xfx | 1100 | `^` | xfy | 200 |
| `?-` | fx | 1100 | `!` | yfx | 200 |
| `-->` | xfx | 1100 | `:` | fy, xfx | 100 |
| `=>` `==>` | xfx | 1099 | `#` | fy, xfx | 90 |
| when, where | yfx | 1098 | `##` | xfx | 50 |
| with, by | fx, yfx | 1098 | backquote | fx | 999 |
| mode, public | fx | 1080 | `->` | xfy | 1040 |
| `,` | xfy | 1000 | | | |

**Conflict.** PRG lists only five operators at 700 and has no `=`, `is`, `==`, `<`, `:=`. TM-388
App B (pdf 154, OCR scrambled) shows **about twelve** rows at 700. So the 1987 table includes the
comparison operators, and the PRG table either omits them or relies on built-in defaults. The
priority of `=`, `is`, `==`, `=:=`, `<`, `=<`, `:=` is therefore **UNKNOWN as printed**. 700 (as in
Prolog) is the working assumption. Read the TM-388 pdf 154 image to settle it.

## 9. Packages (KNOWN, PRG lines 5250–5936; TM-388 §3.8 pp.80–89)

- **Package names.** A package is a class name space. The name space is flat inside a package, and
  `pkg##class` names a class in another package.
- **Package environment.** Each package holds at most one, created by the librarian. It inherits
  other packages and environments.
- **Unqualified names** resolve, in order:
  1. the local package;
  2. classes **externally declared** in packages reached through the environment, with the
     priority rule of PRG lines 5496–5501.
- **Binding time.** Names are bound statically at catalogue (compile) time (TM-388 §3.8).
  MEASURED (`C/tools/deps.py`): template trailers mostly name foreign classes fully qualified
  (`simpos##as_graphics`).
  - Unqualified nature names are nearly always classes of the same package.
  - Exceptions: two pimmcsp classes (`kl1_remote_abortion_device`, `as_physical_device`) list
    natures `my_node_manager` / `node_manager`, which are in no held package. These are left
    unqualified, so they are resolved through the package environment.
  - So qualification is **not** complete in the `.ptf`, and the loader must also implement
    environment lookup.
  - *Corrected 2026-11-23 (`pim/psi/README.md`):* those two names are slot names
    (`node_manager 16 self my_node_manager 16 none`), read by the probe as natures. All 1,455
    held nature vectors are fully qualified. The loader still does environment lookup for
    unqualified names (own package first, then the loaded packages), but no held nature needs it.

## 10. What the compiler must emit (for a compatible ESP compiler)

| Item | Status |
|---|---|
| KL0 code per predicate, in the class/instance/local and demon kinds of FORMATS.md §2 | MEASURED |
| `$or$N` predicates for body disjunctions (cut is OR-local) | MEASURED |
| Slot-init predicates | MEASURED |
| Template trailer: name, id, method vectors, slot vectors, `[self, natures]`, referenced classes, constants | MEASURED, partly |
| Object descriptor = method-table base/mask plus slot-table base/mask. Method key `n·2^24 + a + n` (a = atom number, n = arity); slot key = slot-name atom number. Direct-chained hash tables (TH App A pp.241–242) | KNOWN; built by the **loader**, not stored in `.ptf` |
| Method entry as `load_choice_point` + primaries, with `method_cut` (TH p.244) | KNOWN in principle; the KL0 opcodes are UNKNOWN |
| Exception handlers: a built-in error becomes `exception_handler(Pred,Type,ErrArg,ArgsVector,Addr)`; 32 system types (TH pp.246–249) | KNOWN |

## 11. TR-044 (1984) differences

| Area | TR-044 | Late ESP |
|---|---|---|
| Operators | Precedence relations (precedes / is_preceded_by) in banks (ch.V) | `add_operator` with 0–1200 priorities |
| Strings | bits, bytes, double_bytes | Also words (32-bit) |
| `nature` and self | With no nature the class "inherits only itself"; with natures, self appears where `*` is written. Whether an omitted `*` means self is excluded is not stated in the OCR (IV.4 p.17; read the image) | Self first when `*` is omitted |
| Macros | `=>`, `when`, `where` | Adds `with`, `by`, `==>`, inserta/insertz, macro-bank inheritance |
| Packages, class `class` | Absent | Present |
| Built-ins | App A pp.34–39 | TM-388 App D adds those listed in KL0.md §4 |

TR-005 (1983) is an even earlier, module-based ESP and is not normative.

## 12. Open items for the language

- After-demon order (§5).
- The full operator table (§8).
- Standard-macro constant tables.
- The exact library-lookup semantics of `include` and `use_macro`.
- The meaning of the template qualifier 1/2/3 on primaries (FORMATS.md §2).
