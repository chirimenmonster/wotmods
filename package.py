import py_compile
import zipfile
import os
import sys
import fnmatch
import shutil
import argparse
import re

WOT_VERSION          = "0.9.17.1"
SUPPORT_URL          = ""
ROOT_DIR             = os.path.dirname(os.path.realpath(__file__))
SRC_DIR              = os.path.join(ROOT_DIR, "src")
SCRIPT_DIR           = os.path.join(ROOT_DIR, "src", "scripts")
CONFIG_DIR           = os.path.join(ROOT_DIR, "configs")
BUILD_DIR            = os.path.join(ROOT_DIR, "build")

MOD_BASE_DIR         = os.path.join(SRC_DIR, "scripts", "client", "gui", "mods")

DOC_FILES = [
    os.path.join(ROOT_DIR, "LICENSE"),
    os.path.join(ROOT_DIR, "README.md")
]

META_FILES = [
    os.path.join(ROOT_DIR, "meta.xml.in")
]

sys.dont_write_bytecode = True
sys.path.append(MOD_BASE_DIR)
from spotmessanger.version import MOD_INFO

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mod-name',    default=MOD_INFO.NAME)
    parser.add_argument('--mod-version', default=MOD_INFO.VERSION)
    parser.add_argument('--mod-debug',   default=MOD_INFO.DEBUG)
    args = parser.parse_args()
    in_file_parameters = dict(
        SUPPORT_URL = SUPPORT_URL,
        DEBUG       = args.mod_debug,
        MOD_VERSION = args.mod_version
    )

    packager = Packager(
        src_dir               = SRC_DIR,
        in_file_parameters    = in_file_parameters,
        ignored_file_patterns = [".+_test.py"]
    )
    
    stage0 = os.path.join(BUILD_DIR, "stage0")
    stage1 = os.path.join(BUILD_DIR, "stage1")
    stage2 = os.path.join(BUILD_DIR, "stage2")
    stage3 = os.path.join(BUILD_DIR, "stage3")
    stage4 = BUILD_DIR
    
    mod_name = args.mod_name.lower()
    mod_version = args.mod_version
    pack_wotmod = "{name}-{version}.wotmod".format(name=mod_name, version=mod_version)
    zip_wotmod = "{name}-{version}-wotmod.zip".format(name=mod_name, version=mod_version)
    zip_resmod = "{name}-{version}.zip".format(name=mod_name, version=mod_version)
    
    stage = [
        [ [ stage0, "scripts"                           ], [ SCRIPT_DIR         ] ],
        [ [ stage0, "configs"                           ], [ CONFIG_DIR         ] ],
        [ [ stage0, "meta"                              ], [ META_FILES         ] ],
        [ [ stage0, "doc"                               ], [ DOC_FILES          ] ],
        [ [ stage1, "res", "scripts"                    ], [ stage0, "scripts"  ] ],
        [ [ stage1, "res", "configs"                    ], [ stage0, "configs"  ] ],
        [ [ stage1                                      ], [ stage0, "meta"     ] ],
        [ [ stage2, "mods", WOT_VERSION, pack_wotmod    ], [ stage1             ] ],
        [ [ stage2, "mods", "configs"                   ], [ stage0, "configs"  ] ],
        [ [ stage3, "res_mods", WOT_VERSION, "scripts"  ], [ stage0, "scripts"  ] ],
        [ [ stage3, "res_mods", "configs"               ], [ stage0, "configs"  ] ],
        [ [ stage3                                      ], [ stage0, "doc"      ] ],
        [ [ stage4, zip_wotmod                          ], [ stage2             ] ],
        [ [ stage4, zip_resmod                          ], [ stage3             ] ]
    ]
    
    try:
        shutil.rmtree(BUILD_DIR)
    except:
        pass

    for task in stage:
        packager.generate(os.path.join(*task[1]), os.path.join(*task[0]))

    print "build: {}".format(zip_wotmod)
    print "build: {}".format(zip_resmod)

        
def accepts_extensions(extensions):
    '''Decorator function which allows call to pass to the decorated function
    if passed filepath has extension in list of given 'extensions'.
    '''
    def decorator(original_function):
        def wrapper(self, src_filepath, dest_filepath):
            for extension in extensions:
                if src_filepath.lower().endswith(extension.lower()):
                    return original_function(self, src_filepath, dest_filepath)
        return wrapper
    return decorator


class CallbackList(object):

    def __init__(self, *callbacks):
        self.__callbacks = callbacks

    def __call__(self, *args, **kwargs):
        for callback in self.__callbacks:
            callback(*args, **kwargs)


class Packager(object):

    def __init__(self, **dict):
        self.__src_dir = os.path.normpath(dict['src_dir'])
        self.__in_file_parameters = dict['in_file_parameters']
        self.__ignored_file_patterns = dict['ignored_file_patterns']
        self.__builders = CallbackList(
            self.__compile_py_file,
            self.__copy_file,
            self.__run_template_file
        )

    def generate(self, src, dest, **kwargs):
        dest_ext = os.path.splitext(dest.lower())[1]
        if dest_ext in [".zip"]:
            self.__zip_file(src, dest, compression=zipfile.ZIP_DEFLATED)
            return
        if dest_ext in [".wotmod"]:
            self.__zip_file(src, dest, compression=zipfile.ZIP_STORED)
            return
        if os.path.isfile(dest):
            print "file {} is exist.".format(dest)
            raise
        if isinstance(src, tuple) or isinstance(src, list):
            for item in src:
                self.generate(item, dest)
        elif os.path.isdir(src):
            for item in self.__iterate_src_filepaths(src):
                dest_file = item.replace(src, dest)
                self.__builders(item, dest_file)
        else:
            dest_file = src.replace(os.path.dirname(src), dest)
            self.__builders(src, dest_file)

    def __iterate_src_filepaths(self, path):
        '''Returns an iterator which returns paths to all files within source dir.'''
        for root, dirs, files in os.walk(path):
            for filename in files:
                if all([not re.match(pattern, filename, re.IGNORECASE) for pattern in self.__ignored_file_patterns]):
                    yield os.path.normpath(os.path.join(root, filename))

    @accepts_extensions([".py"])
    def __compile_py_file(self, src_filepath, dest_filepath):
        '''Compiles 'src_filepath' python source file into python bytecode file and
        saves it dest_filepath.
        '''
        debug_filepath = src_filepath.replace(self.__src_dir, "").replace("\\", "/").strip("/")
        build_filepath = dest_filepath + "c"
        self.__make_parent_dirs(build_filepath)
        # compile source py-file into bytecode pyc-file
        py_compile.compile(file=src_filepath, cfile=build_filepath, dfile=debug_filepath, doraise=True)

    @accepts_extensions([".swf", ".txt", ".json", ".xml", ".png", ".pyc", ".md", "LICENSE"])
    def __copy_file(self, src_filepath, dest_filepath):
        '''Simply copies file at 'src_filepath' to 'dest_filepath'.'''
        build_filepath = dest_filepath
        self.__make_parent_dirs(build_filepath)
        # simply copy file from source to build dir
        shutil.copyfile(src_filepath, build_filepath)

    @accepts_extensions([".in"])
    def __run_template_file(self, src_filepath, dest_filepath):
        build_filepath = src_filepath[:-3]
        parameters = self.__in_file_parameters
        # run 'parameters' through in-template and produce temporary output file
        with open(src_filepath, "r") as in_file, open(build_filepath, "w") as out_file:
            out_file.write(in_file.read().format(**parameters))
        # further process the output file with other builders
        self.__builders(build_filepath, dest_filepath[:-3])
        # remove the temporary output file
        os.remove(build_filepath)

    def __make_parent_dirs(self, filepath):
        '''Creates any missing parent directories of file indicated in 'filepath'.'''
        try:
            os.makedirs(os.path.dirname(filepath))
        except:
            pass


    def __zip_file(self, src, dest, compression=None):
        try:
            os.remove(dest)  
        except:
            pass
            
        paths = []
        for root, dirs, files in os.walk(src):
            target_dirpath = root.replace(src, "")
            if target_dirpath:
                paths.append((root, target_dirpath))
            for filename in files:
                paths.append((os.path.join(root, filename), os.path.join(target_dirpath, filename)))

        self.__make_parent_dirs(dest)

        with zipfile.ZipFile(dest, "w", compression) as package_file:
            for source, target in paths:
                package_file.write(source, target, compression)

                
if __name__ == "__main__":
    sys.exit(main())
