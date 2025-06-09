from enum import StrEnum

from magika.types import ContentTypeLabel


class TreeSitterLanguage(StrEnum):
    ACTIONSCRIPT = "actionscript"
    ADA = "ada"
    AGDA = "agda"
    APEX = "apex"
    ARDUINO = "arduino"
    ASM = "asm"
    ASTRO = "astro"
    BASH = "bash"
    BEANCOUNT = "beancount"
    BIBTEX = "bibtex"
    BICEP = "bicep"
    BITBAKE = "bitbake"
    C = "c"
    CAIRO = "cairo"
    CAPNP = "capnp"
    CHATITO = "chatito"
    CLARITY = "clarity"
    CLOJURE = "clojure"
    CMAKE = "cmake"
    COMMENT = "comment"
    COMMONLISP = "commonlisp"
    CPON = "cpon"
    CPP = "cpp"
    CSHARP = "csharp"
    CSS = "css"
    CSV = "csv"
    CUDA = "cuda"
    D = "d"
    DART = "dart"
    DOCKERFILE = "dockerfile"
    DOXYGEN = "doxygen"
    DTD = "dtd"
    ELISP = "elisp"
    ELIXIR = "elixir"
    ELM = "elm"
    EMBEDDEDTEMPLATE = "embeddedtemplate"
    ERLANG = "erlang"
    FENNEL = "fennel"
    FIRRTL = "firrtl"
    FISH = "fish"
    FORTRAN = "fortran"
    FUNC = "func"
    GDSCRIPT = "gdscript"
    GITATTRIBUTES = "gitattributes"
    GITCOMMIT = "gitcommit"
    GITIGNORE = "gitignore"
    GLEAM = "gleam"
    GLSL = "glsl"
    GN = "gn"
    GO = "go"
    GOMOD = "gomod"
    GOSUM = "gosum"
    GROOVY = "groovy"
    GSTLAUNCH = "gstlaunch"
    HACK = "hack"
    HARE = "hare"
    HASKELL = "haskell"
    HAXE = "haxe"
    HCL = "hcl"
    HEEX = "heex"
    HLSL = "hlsl"
    HTML = "html"
    HYPRLANG = "hyprlang"
    ISPC = "ispc"
    JANET = "janet"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    JSDOC = "jsdoc"
    JSON = "json"
    JSONNET = "jsonnet"
    JULIA = "julia"
    KCONFIG = "kconfig"
    KDL = "kdl"
    KOTLIN = "kotlin"
    LATEX = "latex"
    LINKERSCRIPT = "linkerscript"
    LLVM = "llvm"
    LUA = "lua"
    LUADOC = "luadoc"
    LUAP = "luap"
    LUAU = "luau"
    MAKE = "make"
    MARKDOWN = "markdown"
    MARKDOWN_INLINE = "markdown_inline"
    MATLAB = "matlab"
    MERMAID = "mermaid"
    MESON = "meson"
    NETLINX = "netlinx"
    NINJA = "ninja"
    NIX = "nix"
    NQC = "nqc"
    OBJC = "objc"
    OCAML = "ocaml"
    OCAML_INTERFACE = "ocaml_interface"
    ODIN = "odin"
    ORG = "org"
    PASCAL = "pascal"
    PEM = "pem"
    PERL = "perl"
    PGN = "pgn"
    PHP = "php"
    PO = "po"
    PONY = "pony"
    POWERSHELL = "powershell"
    PRINTF = "printf"
    PRISMA = "prisma"
    PROPERTIES = "properties"
    PROTO = "proto"
    PSV = "psv"
    PUPPET = "puppet"
    PURESCRIPT = "purescript"
    PYMANIFEST = "pymanifest"
    PYTHON = "python"
    QMLDIR = "qmldir"
    QMLJS = "qmljs"
    QUERY = "query"
    R = "r"
    RACKET = "racket"
    RE2C = "re2c"
    READLINE = "readline"
    REQUIREMENTS = "requirements"
    RON = "ron"
    RST = "rst"
    RUBY = "ruby"
    RUST = "rust"
    SCALA = "scala"
    SCHEME = "scheme"
    SCSS = "scss"
    SMALI = "smali"
    SMITHY = "smithy"
    SOLIDITY = "solidity"
    SPARQL = "sparql"
    SWIFT = "swift"
    SQL = "sql"
    SQUIRREL = "squirrel"
    STARLARK = "starlark"
    SVELTE = "svelte"
    TABLEGEN = "tablegen"
    TCL = "tcl"
    TERRAFORM = "terraform"
    TEST = "test"
    THRIFT = "thrift"
    TOML = "toml"
    TSV = "tsv"
    TSX = "tsx"
    TWIG = "twig"
    TYPESCRIPT = "typescript"
    TYPST = "typst"
    UDEV = "udev"
    UNGRAMMAR = "ungrammar"
    UXNTAL = "uxntal"
    V = "v"
    VERILOG = "verilog"
    VHDL = "vhdl"
    VIM = "vim"
    VUE = "vue"
    WGSL = "wgsl"
    XCOMPOSE = "xcompose"
    XML = "xml"
    YAML = "yaml"
    YUCK = "yuck"
    ZIG = "zig"
    MAGIK = "magik"


magika_labels = [
    ContentTypeLabel._3DS,
    ContentTypeLabel._3DSM,
    ContentTypeLabel._3DSX,
    ContentTypeLabel._3GP,
    ContentTypeLabel._3MF,
    ContentTypeLabel.ABNF,
    ContentTypeLabel.ACE,
    ContentTypeLabel.ADA,
    ContentTypeLabel.AFF,
    ContentTypeLabel.AI,
    ContentTypeLabel.AIDL,
    ContentTypeLabel.ALGOL68,
    ContentTypeLabel.ANI,
    ContentTypeLabel.APK,
    ContentTypeLabel.APPLEBPLIST,
    ContentTypeLabel.APPLEDOUBLE,
    ContentTypeLabel.APPLEPLIST,
    ContentTypeLabel.APPLESINGLE,
    ContentTypeLabel.AR,
    ContentTypeLabel.ARC,
    ContentTypeLabel.ARJ,
    ContentTypeLabel.ARROW,
    ContentTypeLabel.ASC,
    ContentTypeLabel.ASD,
    ContentTypeLabel.ASF,
    ContentTypeLabel.ASM,
    ContentTypeLabel.ASP,
    ContentTypeLabel.AU,
    ContentTypeLabel.AUTOHOTKEY,
    ContentTypeLabel.AUTOIT,
    ContentTypeLabel.AVI,
    ContentTypeLabel.AVIF,
    ContentTypeLabel.AVRO,
    ContentTypeLabel.AWK,
    ContentTypeLabel.AX,
    ContentTypeLabel.BATCH,
    ContentTypeLabel.BAZEL,
    ContentTypeLabel.BCAD,
    ContentTypeLabel.BIB,
    ContentTypeLabel.BMP,
    ContentTypeLabel.BPG,
    ContentTypeLabel.BPL,
    ContentTypeLabel.BRAINFUCK,
    ContentTypeLabel.BRF,
    ContentTypeLabel.BZIP,
    ContentTypeLabel.BZIP3,
    ContentTypeLabel.C,
    ContentTypeLabel.CAB,
    ContentTypeLabel.CAD,
    ContentTypeLabel.CAT,
    ContentTypeLabel.CDF,
    ContentTypeLabel.CHM,
    ContentTypeLabel.CLOJURE,
    ContentTypeLabel.CMAKE,
    ContentTypeLabel.COBOL,
    ContentTypeLabel.COFF,
    ContentTypeLabel.COFFEESCRIPT,
    ContentTypeLabel.COM,
    ContentTypeLabel.CPL,
    ContentTypeLabel.CPP,
    ContentTypeLabel.CRT,
    ContentTypeLabel.CRX,
    ContentTypeLabel.CS,
    ContentTypeLabel.CSPROJ,
    ContentTypeLabel.CSS,
    ContentTypeLabel.CSV,
    ContentTypeLabel.CTL,
    ContentTypeLabel.DART,
    ContentTypeLabel.DEB,
    ContentTypeLabel.DEX,
    ContentTypeLabel.DEY,
    ContentTypeLabel.DICOM,
    ContentTypeLabel.DIFF,
    ContentTypeLabel.DIRECTORY,
    ContentTypeLabel.DJANGO,
    ContentTypeLabel.DLL,
    ContentTypeLabel.DM,
    ContentTypeLabel.DMG,
    ContentTypeLabel.DMIGD,
    ContentTypeLabel.DMSCRIPT,
    ContentTypeLabel.DOC,
    ContentTypeLabel.DOCKERFILE,
    ContentTypeLabel.DOCX,
    ContentTypeLabel.DOSMBR,
    ContentTypeLabel.DOTX,
    ContentTypeLabel.DSSTORE,
    ContentTypeLabel.DWG,
    ContentTypeLabel.DXF,
    ContentTypeLabel.DYLIB,
    ContentTypeLabel.EBML,
    ContentTypeLabel.ELF,
    ContentTypeLabel.ELIXIR,
    ContentTypeLabel.EMF,
    ContentTypeLabel.EML,
    ContentTypeLabel.EMPTY,
    ContentTypeLabel.EPUB,
    ContentTypeLabel.ERB,
    ContentTypeLabel.ERLANG,
    ContentTypeLabel.ESE,
    ContentTypeLabel.EXE,
    ContentTypeLabel.EXP,
    ContentTypeLabel.FLAC,
    ContentTypeLabel.FLUTTER,
    ContentTypeLabel.FLV,
    ContentTypeLabel.FORTRAN,
    ContentTypeLabel.FPX,
    ContentTypeLabel.GEMFILE,
    ContentTypeLabel.GEMSPEC,
    ContentTypeLabel.GIF,
    ContentTypeLabel.GITATTRIBUTES,
    ContentTypeLabel.GITMODULES,
    ContentTypeLabel.GLEAM,
    ContentTypeLabel.GO,
    ContentTypeLabel.GPX,
    ContentTypeLabel.GRADLE,
    ContentTypeLabel.GROOVY,
    ContentTypeLabel.GZIP,
    ContentTypeLabel.H,
    ContentTypeLabel.H5,
    ContentTypeLabel.HANDLEBARS,
    ContentTypeLabel.HASKELL,
    ContentTypeLabel.HCL,
    ContentTypeLabel.HEIF,
    ContentTypeLabel.HFS,
    ContentTypeLabel.HLP,
    ContentTypeLabel.HPP,
    ContentTypeLabel.HTA,
    ContentTypeLabel.HTACCESS,
    ContentTypeLabel.HTML,
    ContentTypeLabel.HVE,
    ContentTypeLabel.HWP,
    ContentTypeLabel.ICC,
    ContentTypeLabel.ICNS,
    ContentTypeLabel.ICO,
    ContentTypeLabel.ICS,
    ContentTypeLabel.IGNOREFILE,
    ContentTypeLabel.IMG,
    ContentTypeLabel.INI,
    ContentTypeLabel.INTERNETSHORTCUT,
    ContentTypeLabel.IOSAPP,
    ContentTypeLabel.IPYNB,
    ContentTypeLabel.ISO,
    ContentTypeLabel.JAR,
    ContentTypeLabel.JAVA,
    ContentTypeLabel.JAVABYTECODE,
    ContentTypeLabel.JAVASCRIPT,
    ContentTypeLabel.JINJA,
    ContentTypeLabel.JNG,
    ContentTypeLabel.JNLP,
    ContentTypeLabel.JP2,
    ContentTypeLabel.JPEG,
    ContentTypeLabel.JSON,
    ContentTypeLabel.JSONC,
    ContentTypeLabel.JSONL,
    ContentTypeLabel.JSX,
    ContentTypeLabel.JULIA,
    ContentTypeLabel.JXL,
    ContentTypeLabel.KO,
    ContentTypeLabel.KOTLIN,
    ContentTypeLabel.KS,
    ContentTypeLabel.LATEX,
    ContentTypeLabel.LATEXAUX,
    ContentTypeLabel.LESS,
    ContentTypeLabel.LHA,
    ContentTypeLabel.LICENSE,
    ContentTypeLabel.LISP,
    ContentTypeLabel.LITCS,
    ContentTypeLabel.LNK,
    ContentTypeLabel.LOCK,
    ContentTypeLabel.LRZ,
    ContentTypeLabel.LUA,
    ContentTypeLabel.LZ,
    ContentTypeLabel.LZ4,
    ContentTypeLabel.LZX,
    ContentTypeLabel.M3U,
    ContentTypeLabel.M4,
    ContentTypeLabel.MACHO,
    ContentTypeLabel.MAFF,
    ContentTypeLabel.MAKEFILE,
    ContentTypeLabel.MARKDOWN,
    ContentTypeLabel.MATLAB,
    ContentTypeLabel.MHT,
    ContentTypeLabel.MIDI,
    ContentTypeLabel.MKV,
    ContentTypeLabel.MP2,
    ContentTypeLabel.MP3,
    ContentTypeLabel.MP4,
    ContentTypeLabel.MPEGTS,
    ContentTypeLabel.MSCOMPRESS,
    ContentTypeLabel.MSI,
    ContentTypeLabel.MSIX,
    ContentTypeLabel.MST,
    ContentTypeLabel.MUI,
    ContentTypeLabel.MUM,
    ContentTypeLabel.MUN,
    ContentTypeLabel.NIM,
    ContentTypeLabel.NPY,
    ContentTypeLabel.NPZ,
    ContentTypeLabel.NULL,
    ContentTypeLabel.NUPKG,
    ContentTypeLabel.OBJECT,
    ContentTypeLabel.OBJECTIVEC,
    ContentTypeLabel.OCAML,
    ContentTypeLabel.OCX,
    ContentTypeLabel.ODEX,
    ContentTypeLabel.ODIN,
    ContentTypeLabel.ODP,
    ContentTypeLabel.ODS,
    ContentTypeLabel.ODT,
    ContentTypeLabel.OGG,
    ContentTypeLabel.OLE,
    ContentTypeLabel.ONE,
    ContentTypeLabel.ONNX,
    ContentTypeLabel.OOXML,
    ContentTypeLabel.OTF,
    ContentTypeLabel.OUTLOOK,
    ContentTypeLabel.PALMOS,
    ContentTypeLabel.PARQUET,
    ContentTypeLabel.PASCAL,
    ContentTypeLabel.PBM,
    ContentTypeLabel.PCAP,
    ContentTypeLabel.PDB,
    ContentTypeLabel.PDF,
    ContentTypeLabel.PEBIN,
    ContentTypeLabel.PEM,
    ContentTypeLabel.PERL,
    ContentTypeLabel.PGP,
    ContentTypeLabel.PHP,
    ContentTypeLabel.PICKLE,
    ContentTypeLabel.PNG,
    ContentTypeLabel.PO,
    ContentTypeLabel.POSTSCRIPT,
    ContentTypeLabel.POWERSHELL,
    ContentTypeLabel.PPT,
    ContentTypeLabel.PPTX,
    ContentTypeLabel.PRINTFOX,
    ContentTypeLabel.PROLOG,
    ContentTypeLabel.PROTEINDB,
    ContentTypeLabel.PROTO,
    ContentTypeLabel.PROTOBUF,
    ContentTypeLabel.PSD,
    ContentTypeLabel.PUB,
    ContentTypeLabel.PYTHON,
    ContentTypeLabel.PYTHONBYTECODE,
    ContentTypeLabel.PYTHONPAR,
    ContentTypeLabel.PYTORCH,
    ContentTypeLabel.QOI,
    ContentTypeLabel.QT,
    ContentTypeLabel.R,
    ContentTypeLabel.RANDOMASCII,
    ContentTypeLabel.RANDOMBYTES,
    ContentTypeLabel.RANDOMTXT,
    ContentTypeLabel.RAR,
    ContentTypeLabel.RDF,
    ContentTypeLabel.RDP,
    ContentTypeLabel.RIFF,
    ContentTypeLabel.RLIB,
    ContentTypeLabel.RLL,
    ContentTypeLabel.RPM,
    ContentTypeLabel.RST,
    ContentTypeLabel.RTF,
    ContentTypeLabel.RUBY,
    ContentTypeLabel.RUST,
    ContentTypeLabel.RZIP,
    ContentTypeLabel.SCALA,
    ContentTypeLabel.SCHEME,
    ContentTypeLabel.SCR,
    ContentTypeLabel.SCRIPTWSF,
    ContentTypeLabel.SCSS,
    ContentTypeLabel.SEVENZIP,
    ContentTypeLabel.SGML,
    ContentTypeLabel.SH3D,
    ContentTypeLabel.SHELL,
    ContentTypeLabel.SMALI,
    ContentTypeLabel.SNAP,
    ContentTypeLabel.SO,
    ContentTypeLabel.SOLIDITY,
    ContentTypeLabel.SQL,
    ContentTypeLabel.SQLITE,
    ContentTypeLabel.SQUASHFS,
    ContentTypeLabel.SRT,
    ContentTypeLabel.STLBINARY,
    ContentTypeLabel.STLTEXT,
    ContentTypeLabel.SUM,
    ContentTypeLabel.SVD,
    ContentTypeLabel.SVG,
    ContentTypeLabel.SWF,
    ContentTypeLabel.SWIFT,
    ContentTypeLabel.SYMLINK,
    ContentTypeLabel.SYMLINKTEXT,
    ContentTypeLabel.SYS,
    ContentTypeLabel.TAR,
    ContentTypeLabel.TCL,
    ContentTypeLabel.TEXTPROTO,
    ContentTypeLabel.TGA,
    ContentTypeLabel.THUMBSDB,
    ContentTypeLabel.TIFF,
    ContentTypeLabel.TMDX,
    ContentTypeLabel.TOML,
    ContentTypeLabel.TORRENT,
    ContentTypeLabel.TROFF,
    ContentTypeLabel.TSV,
    ContentTypeLabel.TSX,
    ContentTypeLabel.TTF,
    ContentTypeLabel.TWIG,
    ContentTypeLabel.TXT,
    ContentTypeLabel.TXTASCII,
    ContentTypeLabel.TXTUTF16,
    ContentTypeLabel.TXTUTF8,
    ContentTypeLabel.TYPESCRIPT,
    ContentTypeLabel.UDF,
    ContentTypeLabel.UNDEFINED,
    ContentTypeLabel.UNIXCOMPRESS,
    ContentTypeLabel.UNKNOWN,
    ContentTypeLabel.VBA,
    ContentTypeLabel.VBE,
    ContentTypeLabel.VCARD,
    ContentTypeLabel.VCS,
    ContentTypeLabel.VCXPROJ,
    ContentTypeLabel.VERILOG,
    ContentTypeLabel.VHD,
    ContentTypeLabel.VHDL,
    ContentTypeLabel.VISIO,
    ContentTypeLabel.VTT,
    ContentTypeLabel.VUE,
    ContentTypeLabel.WAD,
    ContentTypeLabel.WASM,
    ContentTypeLabel.WAV,
    ContentTypeLabel.WEBM,
    ContentTypeLabel.WEBP,
    ContentTypeLabel.WEBTEMPLATE,
    ContentTypeLabel.WIM,
    ContentTypeLabel.WINREGISTRY,
    ContentTypeLabel.WMA,
    ContentTypeLabel.WMF,
    ContentTypeLabel.WMV,
    ContentTypeLabel.WOFF,
    ContentTypeLabel.WOFF2,
    ContentTypeLabel.XAR,
    ContentTypeLabel.XCF,
    ContentTypeLabel.XLS,
    ContentTypeLabel.XLSB,
    ContentTypeLabel.XLSX,
    ContentTypeLabel.XML,
    ContentTypeLabel.XPI,
    ContentTypeLabel.XSD,
    ContentTypeLabel.XZ,
    ContentTypeLabel.YAML,
    ContentTypeLabel.YARA,
    ContentTypeLabel.ZIG,
    ContentTypeLabel.ZIP,
    ContentTypeLabel.ZLIBSTREAM,
    ContentTypeLabel.ZST,
]

text_mappings: dict[ContentTypeLabel, TreeSitterLanguage | None] = {
    ContentTypeLabel.MARKDOWN: TreeSitterLanguage.MARKDOWN,
    ContentTypeLabel.TXT: None,
}

data_mappings: dict[ContentTypeLabel, TreeSitterLanguage | None] = {
    ContentTypeLabel.CSV: TreeSitterLanguage.CSV,
    ContentTypeLabel.JSON: TreeSitterLanguage.JSON,
    ContentTypeLabel.JSONL: TreeSitterLanguage.JSON,
    ContentTypeLabel.TOML: TreeSitterLanguage.TOML,
    ContentTypeLabel.XML: TreeSitterLanguage.XML,
    ContentTypeLabel.YAML: TreeSitterLanguage.YAML,
}

code_mappings: dict[ContentTypeLabel, TreeSitterLanguage | None] = {
    ContentTypeLabel.ADA: TreeSitterLanguage.ADA,
    ContentTypeLabel.ASM: TreeSitterLanguage.ASM,
    ContentTypeLabel.C: TreeSitterLanguage.C,
    ContentTypeLabel.CPP: TreeSitterLanguage.CPP,
    ContentTypeLabel.CS: TreeSitterLanguage.CSHARP,
    ContentTypeLabel.CSS: TreeSitterLanguage.CSS,
    ContentTypeLabel.DART: TreeSitterLanguage.DART,
    ContentTypeLabel.DOCKERFILE: TreeSitterLanguage.DOCKERFILE,
    ContentTypeLabel.ELIXIR: TreeSitterLanguage.ELIXIR,
    ContentTypeLabel.ERLANG: TreeSitterLanguage.ERLANG,
    ContentTypeLabel.FORTRAN: TreeSitterLanguage.FORTRAN,
    ContentTypeLabel.GO: TreeSitterLanguage.GO,
    ContentTypeLabel.HASKELL: TreeSitterLanguage.HASKELL,
    ContentTypeLabel.JAVA: TreeSitterLanguage.JAVA,
    ContentTypeLabel.JAVASCRIPT: TreeSitterLanguage.JAVASCRIPT,
    ContentTypeLabel.KOTLIN: TreeSitterLanguage.KOTLIN,
    ContentTypeLabel.LUA: TreeSitterLanguage.LUA,
    ContentTypeLabel.MATLAB: TreeSitterLanguage.MATLAB,
    ContentTypeLabel.PHP: TreeSitterLanguage.PHP,
    ContentTypeLabel.PYTHON: TreeSitterLanguage.PYTHON,
    ContentTypeLabel.R: TreeSitterLanguage.R,
    ContentTypeLabel.RUBY: TreeSitterLanguage.RUBY,
    ContentTypeLabel.RUST: TreeSitterLanguage.RUST,
    ContentTypeLabel.SCALA: TreeSitterLanguage.SCALA,
    ContentTypeLabel.SCHEME: TreeSitterLanguage.SCHEME,
    ContentTypeLabel.SQL: TreeSitterLanguage.SQL,
    ContentTypeLabel.SWIFT: TreeSitterLanguage.SWIFT,
    ContentTypeLabel.TYPESCRIPT: TreeSitterLanguage.TYPESCRIPT,
    ContentTypeLabel.VERILOG: TreeSitterLanguage.VERILOG,
    ContentTypeLabel.VHDL: TreeSitterLanguage.VHDL,
    ContentTypeLabel.VUE: TreeSitterLanguage.VUE,
    ContentTypeLabel.ZIG: TreeSitterLanguage.ZIG,
}

script_mappings: dict[ContentTypeLabel, TreeSitterLanguage | None] = {
    ContentTypeLabel.SHELL: TreeSitterLanguage.BASH,
    ContentTypeLabel.MAKEFILE: TreeSitterLanguage.MAKE,
    ContentTypeLabel.POWERSHELL: TreeSitterLanguage.POWERSHELL,
}
