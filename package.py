import py_compile
import zipfile
import os
import sys
import fnmatch
import shutil
import argparse
import re

WOT_VERSION          = "0.9.14.1"
SUPPORT_URL          = ""
ROOT_DIR             = os.path.dirname(os.path.realpath(__file__))
SRC_DIR              = os.path.join(ROOT_DIR, "src")
CONF_DIR             = os.path.join(ROOT_DIR, "configs")
PACKAGE_ROOT_DIR     = ""
PACKAGE_SCRIPT_DIR   = os.path.join(PACKAGE_ROOT_DIR, "res_mods", WOT_VERSION)
PACKAGE_CONF_DIR     = os.path.join(PACKAGE_ROOT_DIR, "res_mods", "configs")
BUILD_DIR            = os.path.join(os.getcwd(), "build")
BUILD_SCRIPT_DIR     = os.path.join(BUILD_DIR, "res_mods", WOT_VERSION)
BUILD_CONF_DIR       = os.path.join(BUILD_DIR, "res_mods", "configs")

MOD_BASE_DIR         = os.path.join(SRC_DIR, "scripts", "client", "gui", "mods")

DIRECT_FILES = [
    os.path.join(ROOT_DIR, "LICENSE"),
    os.path.join(ROOT_DIR, "README.md")
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
    in_file_parameters = {
        "spotmessanger.txt.in": dict(
            SUPPORT_URL = SUPPORT_URL
        ),
        "spotmessanger.xml.in": dict(
            DEBUG = args.mod_debug
        )
    }
    package_name = "{name}-{version}.zip".format(name=args.mod_name.lower(), version=args.mod_version)
    packager = Packager(
        root_dir              = ROOT_DIR,
        src_dir               = SRC_DIR,
        conf_dir              = CONF_DIR,
        direct_files          = DIRECT_FILES,
        build_dir             = BUILD_DIR,
        build_script_dir      = BUILD_SCRIPT_DIR,
        build_conf_dir        = BUILD_CONF_DIR,
        package_path          = os.path.join(os.getcwd(), package_name),
        package_root_dir      = PACKAGE_ROOT_DIR,
        package_script_dir    = PACKAGE_SCRIPT_DIR,
        package_conf_dir      = PACKAGE_CONF_DIR,
        in_file_parameters    = in_file_parameters,
        ignored_file_patterns = [".+_test.py"]
    )
    packager.create()
    print "Package file path:", packager.get_package_path()

def accepts_extensions(extensions):
    '''Decorator function which allows call to pass to the decorated function
    if passed filepath has extension in list of given 'extensions'.
    '''
    def decorator(original_function):
        def wrapper(self, src_filepath):
            for extension in extensions:
                if src_filepath.lower().endswith(extension.lower()):
                    return original_function(self, src_filepath)
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
        self.__root_dir = os.path.normpath(dict['root_dir'])
        self.__src_dir = os.path.normpath(dict['src_dir'])
        self.__conf_dir = os.path.normpath(dict['conf_dir'])
        self.__direct_files = map(os.path.normpath, dict['direct_files'])
        self.__build_dir = os.path.normpath(dict['build_dir'])
        self.__build_script_dir = os.path.normpath(dict['build_script_dir'])
        self.__build_conf_dir = os.path.normpath(dict['build_conf_dir'])
        self.__package_path = dict['package_path']
        self.__package_root_dir = dict['package_root_dir']
        self.__package_script_dir = dict['package_script_dir']
        self.__package_conf_dir = dict['package_conf_dir']
        self.__in_file_parameters = dict['in_file_parameters']
        self.__ignored_file_patterns = dict['ignored_file_patterns']
        self.__builders = CallbackList(
            self.__compile_py_file,
            self.__copy_file,
            self.__run_template_file
        )

    def get_package_path(self):
        return self.__package_path

    def get_package_root_path(self):
        return self.__package_root_dir

    def create(self):
        self.__remove_build_dir()
        self.__remove_old_package()
        self.__build_files(self.__iterate_src_filepaths(self.__src_dir))
        self.__build_files(self.__iterate_src_filepaths(self.__conf_dir))
        self.__build_files(DIRECT_FILES)
        self.__package_files()

    def __remove_build_dir(self):
        try:
            shutil.rmtree(self.__build_dir)
        except:
            pass

    def __remove_old_package(self):
        try:
            os.remove(self.__package_path)
        except:
            pass

    def __build_files(self, src_filepaths):
        for src_filepath in src_filepaths:
            self.__builders(src_filepath)

    def __iterate_src_filepaths(self, path):
        '''Returns an iterator which returns paths to all files within source dir.'''
        for root, dirs, files in os.walk(path):
            for filename in files:
                if all([not re.match(pattern, filename, re.IGNORECASE) for pattern in self.__ignored_file_patterns]):
                    yield os.path.normpath(os.path.join(root, filename))

    @accepts_extensions([".py"])
    def __compile_py_file(self, src_filepath):
        '''Compiles 'src_filepath' python source file into python bytecode file and
        saves it build dir.
        '''
        debug_filepath = src_filepath.replace(self.__src_dir, "").replace("\\", "/").strip("/")
        build_filepath = self.__src_path_to_build_path(src_filepath) + "c"
        self.__make_parent_dirs(build_filepath)
        # compile source py-file into bytecode pyc-file
        py_compile.compile(file=src_filepath, cfile=build_filepath, dfile=debug_filepath, doraise=True)

    @accepts_extensions([".swf", ".txt", ".json", ".xml", ".png"] + map(os.path.basename, DIRECT_FILES))
    def __copy_file(self, src_filepath):
        '''Simply copies file at 'src_filepath' to build dir.'''
        build_filepath = self.__src_path_to_build_path(src_filepath)
        self.__make_parent_dirs(build_filepath)
        # simply copy file from source to build dir
        shutil.copyfile(src_filepath, build_filepath)

    @accepts_extensions([".in"])
    def __run_template_file(self, src_filepath):
        build_filepath = src_filepath[:-3]
        parameters = self.__in_file_parameters[os.path.basename(src_filepath)]
        # run 'parameters' through in-template and produce temporary output file
        with open(src_filepath, "r") as in_file, open(build_filepath, "w") as out_file:
            out_file.write(in_file.read().format(**parameters))
        # further process the output file with other builders
        self.__builders(build_filepath)
        # remove the temporary output file
        os.remove(build_filepath)

    def __src_path_to_build_path(self, src_path):
        # ${SRC_DIR}/whereever/whatever --> ${BUILD_DIR}/whereever/whatever
        if self.__src_dir in src_path:
            return src_path.replace(self.__src_dir, self.__build_script_dir)
        if self.__conf_dir in src_path:
            return src_path.replace(self.__conf_dir, self.__build_conf_dir)
        if src_path in self.__direct_files:
            return src_path.replace(self.__root_dir, self.__build_dir)
        print 'warning: unknwon file, {}'.format(src_path)

    def __make_parent_dirs(self, filepath):
        '''Creates any missing parent directories of file indicated in 'filepath'.'''
        try:
            os.makedirs(os.path.dirname(filepath))
        except:
            pass

    def __package_files(self):
        paths = []
        for root, dirs, files in os.walk(self.__build_dir):
            target_dirpath = root.replace(self.__build_dir, self.__package_root_dir)
            for filename in files:
                paths.append((os.path.join(root, filename), os.path.join(target_dirpath, filename)))

        with zipfile.ZipFile(self.__package_path, "w") as package_file:
            for source, target in paths:
                package_file.write(source, target)

if __name__ == "__main__":
    sys.exit(main())
