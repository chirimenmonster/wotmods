import py_compile
import zipfile
import os
import sys
import shutil
import argparse
import re
import ConfigParser
from string import Template

ROOT_DIR            = os.path.dirname(os.path.realpath(__file__))
SCRIPT_DIR          = os.path.join(ROOT_DIR, "src", "scripts")
CONFIG_DIR          = os.path.join(ROOT_DIR, "configs")
BUILD_DIR           = os.path.join(ROOT_DIR, "build")
SCRIPT_DEBUG_BASE   = "scripts"

DOC_FILES = [
    os.path.join(ROOT_DIR, "LICENSE"),
    os.path.join(ROOT_DIR, "README.md")
]

META_FILES = [
    os.path.join(ROOT_DIR, "meta.in.xml")
]

sys.dont_write_bytecode = True

def main():
    inifile = ConfigParser.SafeConfigParser()
    inifile.read('config.ini')
    wot_version = inifile.get('wot', 'version')

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='show debug messages')
    parser.add_argument('-k', '--keep-tmpfile', action='store_true', help='keep tempfile')
    parser.add_argument('--mod-debug', default=inifile.getboolean('mod', 'debug'),
            metavar='DEBUG', help='specify mod debug mode, True/False')
    args = parser.parse_args()
    
    in_file_parameters = dict(
        DEBUG               = args.mod_debug,
        MOD_ID              = inifile.get('mod', 'id'),
        MOD_NAME            = inifile.get('mod', 'name'),
        MOD_VERSION         = inifile.get('mod', 'version'),
        MOD_VERSION_LONG    = inifile.get('mod', 'version_long'),
        DESCRIPTION         = inifile.get('mod', 'description').replace('\n', ' '),
        SUPPORT_URL         = inifile.get('mod', 'support_url')
    )

    packager = Packager(
        args                    = args,
        in_file_parameters      = in_file_parameters,
        ignored_file_patterns   = [".+_test.py"]
    )
    
    stage0 = os.path.join(BUILD_DIR, "stage0")
    stage1 = os.path.join(BUILD_DIR, "stage1")
    stage2 = os.path.join(BUILD_DIR, "stage2")
    stage3 = BUILD_DIR
    
    mod_name = in_file_parameters['MOD_NAME'].lower()
    mod_version = in_file_parameters['MOD_VERSION'].lower()
    pack_wotmod = "{name}-{version}.wotmod".format(name=mod_name, version=mod_version)
    zip_wotmod = "{name}-{version}.zip".format(name=mod_name, version=mod_version)
    
    stage = [
        [ [ stage0, "scripts"                           ], [ SCRIPT_DIR         ] ],
        [ [ stage0, "configs"                           ], [ CONFIG_DIR         ] ],
        [ [ stage0, "meta"                              ], [ META_FILES         ] ],
        [ [ stage0, "doc"                               ], [ DOC_FILES          ] ],
        [ [ stage1, "res", "scripts"                    ], [ stage0, "scripts"  ] ],
        [ [ stage1                                      ], [ stage0, "meta"     ] ],
        [ [ stage2, "mods", wot_version, pack_wotmod    ], [ stage1             ] ],
        [ [ stage2, "mods", "configs"                   ], [ stage0, "configs"  ] ],
        [ [ stage2, "mods", "configs", mod_name         ], [ stage0, "doc"      ] ],
        [ [ stage2                                      ], [ stage0, "doc"      ] ],
        [ [ stage3, zip_wotmod                          ], [ stage2             ] ]
    ]
    
    try:
        shutil.rmtree(BUILD_DIR)
    except:
        pass

    for task in stage:
        packager.generate(os.path.join(*task[1]), os.path.join(*task[0]))

    print "build: {}".format(zip_wotmod)

        
def accepts_extensions(extensions):
    '''Decorator function which allows call to pass to the decorated function
    if passed filepath has extension in list of given 'extensions'.
    '''
    def decorator(original_function):
        def wrapper(self, src_filepath, dest_filepath, **kwargs):
            for extension in extensions:
                if src_filepath.lower().endswith(extension.lower()):
                    return original_function(self, src_filepath, dest_filepath, **kwargs)
            return False
        return wrapper
    return decorator


class CallbackList(object):

    def __init__(self, *callbacks):
        self.__callbacks = callbacks

    def __call__(self, *args, **kwargs):
        for callback in self.__callbacks:
            if callback(*args, **kwargs):
                return


class Packager(object):

    def __init__(self, **dict):
        self.__args = dict['args']
        self.__in_file_parameters = dict['in_file_parameters']
        self.__ignored_file_patterns = dict['ignored_file_patterns']
        self.__builders = CallbackList(
            self.__run_template_file,
            self.__compile_py_file,
            self.__copy_file
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
                dest_dir = os.path.dirname(item.replace(src, dest))
                self.__builders(item, dest_dir)
        else:
            dest_dir = os.path.dirname(src.replace(os.path.dirname(src), dest))
            self.__builders(src, dest_dir)

    def __iterate_src_filepaths(self, path):
        '''Returns an iterator which returns paths to all files within source dir.'''
        for root, dirs, files in os.walk(path):
            for filename in files:
                if all([not re.match(pattern, filename, re.IGNORECASE) for pattern in self.__ignored_file_patterns]):
                    yield os.path.normpath(os.path.join(root, filename))

    @accepts_extensions([".py"])
    def __compile_py_file(self, src_filepath, dest_dir, orig_filepath=None, **kwargs):
        '''Compiles 'src_filepath' python source file into python bytecode file and saves it dest_filepath.'''
        rel_filepath = os.path.relpath(orig_filepath or src_filepath, SCRIPT_DIR)
        debug_filepath = os.path.join(SCRIPT_DEBUG_BASE, rel_filepath)
        dest_filepath = os.path.join(dest_dir, os.path.splitext(os.path.basename(src_filepath))[0] + ".pyc")
        self.__make_parent_dirs(dest_filepath)
        # compile source py-file into bytecode pyc-file
        if self.__args.debug:
            print "compile: {} -> {} ({})".format(os.path.relpath(src_filepath, ROOT_DIR),
                    os.path.relpath(dest_filepath, ROOT_DIR), debug_filepath)
        py_compile.compile(file=src_filepath, cfile=dest_filepath, dfile=debug_filepath, doraise=True)
        return True

    @accepts_extensions([".swf", ".txt", ".json", ".xml", ".png", ".pyc", ".md", "LICENSE"])
    def __copy_file(self, src_filepath, dest_dir, **kwargs):
        '''Simply copies file at 'src_filepath' to 'dest_filepath'.'''
        dest_filepath = os.path.join(dest_dir, os.path.basename(src_filepath))
        self.__make_parent_dirs(dest_filepath)
        # simply copy file from source to build dir
        if self.__args.debug:
            print "copy: {} -> {}".format(os.path.relpath(src_filepath, ROOT_DIR), os.path.relpath(dest_filepath, ROOT_DIR))
        shutil.copyfile(src_filepath, dest_filepath)
        return True

    @accepts_extensions([".in", "in.txt", ".in.xml", ".in.py"])
    def __run_template_file(self, src_filepath, dest_dir, **kwargs):
        parameters = self.__in_file_parameters
        src_dir, src_file = os.path.split(src_filepath)
        build_dir = os.path.join(BUILD_DIR, 'tmp')
        i = src_file.rfind('.in')
        filename = src_file[:i] + src_file[i+3:]
        build_filepath = os.path.join(build_dir, filename)
        self.__make_parent_dirs(build_filepath)
        # run 'parameters' through in-template and produce temporary output file
        if self.__args.debug:
            print "template: {} -> {}".format(os.path.relpath(src_filepath, ROOT_DIR), os.path.relpath(build_filepath, ROOT_DIR))
        with open(src_filepath, "r") as in_file, open(build_filepath, "w") as out_file:
            out_file.write(Template(in_file.read()).substitute(**parameters))
        # further process the output file with other builders
        self.__builders(build_filepath, dest_dir, orig_filepath=os.path.join(src_dir, filename))
        # remove the temporary output file
        if not self.__args.keep_tmpfile:
            os.remove(build_filepath)
            os.rmdir(build_dir)
        return True

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
