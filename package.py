import py_compile
import zipfile
import os
import sys
import fnmatch
import shutil
import argparse
import re

WOT_VERSION          = "0.9.17.1 Common Test"
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

    try:
        shutil.rmtree(BUILD_DIR)
    except:
        pass

    packager = Packager(
        src_dir               = SRC_DIR,
        in_file_parameters    = in_file_parameters,
        ignored_file_patterns = [".+_test.py"]
    )
        
    os.makedirs(BUILD_DIR)

    src_script_dir = SCRIPT_DIR
    src_config_dir = CONFIG_DIR
    stage0_root = os.path.join(BUILD_DIR, "stage0")
    stage0_script_dir = os.path.join(stage0_root, "scripts")
    stage0_config_dir = os.path.join(stage0_root, "config")
    stage0_meta_dir = os.path.join(stage0_root, "meta")
    stage0_doc_dir = os.path.join(stage0_root, "doc")
    packager.gen_recursive(src_script_dir, stage0_script_dir)
    packager.gen_recursive(src_config_dir, stage0_config_dir)
    for file in META_FILES:
        packager.gen_file(file, stage0_meta_dir)
    for file in DOC_FILES:
        packager.gen_file(file, stage0_doc_dir)
    print "build: stage0"
    
    stage1_root = os.path.join(BUILD_DIR, "stage1")
    stage1_script_dir = os.path.join(stage1_root, "res", "scripts")
    stage1_config_dir = os.path.join(stage1_root, "res", "configs")
    packager.gen_recursive(stage0_script_dir, stage1_script_dir)
    packager.gen_recursive(stage0_config_dir, stage1_config_dir)
    packager.gen_recursive(stage0_meta_dir, stage1_root)
    print "build: stage1"

    stage2_root = os.path.join(BUILD_DIR, "stage2")
    stage2_config_dir = os.path.join(stage2_root, "res_mods", "configs")
    packager.gen_recursive(stage0_config_dir, stage2_config_dir)
    packager.gen_recursive(stage0_doc_dir, stage2_root)
    package_name = "{name}-{version}.wotmod".format(name=args.mod_name.lower(), version=args.mod_version)
    createPackage(stage1_root, os.path.join(stage2_root, "mods", WOT_VERSION, package_name), zipfile.ZIP_STORED)
    print "build: stage2"
    
    stage3_root = os.path.join(BUILD_DIR, "stage3")
    stage3_script_dir = os.path.join(stage3_root, "res_mods", WOT_VERSION, "scripts")
    stage3_config_dir = os.path.join(stage3_root, "res_mods", "config")
    packager.gen_recursive(stage0_script_dir, stage3_script_dir)
    packager.gen_recursive(stage0_config_dir, stage3_config_dir)
    packager.gen_recursive(stage0_doc_dir, stage3_root)
    print "build: stage3"
    
    package_name = "{name}-{version}.wotmod.zip".format(name=args.mod_name.lower(), version=args.mod_version)
    createPackage(stage2_root, os.path.join(BUILD_DIR, package_name), zipfile.ZIP_DEFLATED)
    print "create package: " + package_name

    package_name = "{name}-{version}.zip".format(name=args.mod_name.lower(), version=args.mod_version)
    createPackage(stage3_root, os.path.join(BUILD_DIR, package_name), zipfile.ZIP_DEFLATED)
    print "create package: " + package_name

    
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

    def gen_recursive(self, src_dir, dest_dir):
        for src_filepath in self.__iterate_src_filepaths(src_dir):
            dest_filepath = src_filepath.replace(src_dir, dest_dir)
            self.__builders(src_filepath, dest_filepath)

    def gen_file(self, src_filepath, dest_dir):
        dest_filepath = os.path.join(dest_dir, os.path.basename(src_filepath))
        self.__builders(src_filepath, dest_filepath)

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


def createPackage(src, name, compression):
    try:
        os.remove(name)    
    except:
        pass
            
    paths = []
    for root, dirs, files in os.walk(src):
        target_dirpath = root.replace(src, "")
        if target_dirpath:
            paths.append((root, target_dirpath))
        for filename in files:
            paths.append((os.path.join(root, filename), os.path.join(target_dirpath, filename)))

    try:
        os.makedirs(os.path.dirname(name))
    except:
        pass

    with zipfile.ZipFile(name, "w", compression) as package_file:
        for source, target in paths:
            package_file.write(source, target, compression)

                
if __name__ == "__main__":
    sys.exit(main())
