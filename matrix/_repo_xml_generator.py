""" downloaded from http://xbmc-addons.googlecode.com/svn/addons/ """
""" This is a modded version of the original addons.xml generator """

""" Put this version in the root folder of your repo and it will """
""" zip up all add-on folders, create a new zip in your zips folder """
""" and then update the md5 and addons.xml file """

""" Recoded by whufclee (info@totalrevolution.tv) """

import re
import os
import shutil
import hashlib
import zipfile

class Generator:
    """
        Generates a new addons.xml file from each addons addon.xml file
        and a new addons.xml.md5 hash file. Must be run from the root of
        the checked-out repo. Only handles single depth folder structure.
    """
    def __init__(self):
# Create the zips folder if it doesn't already exist
        zips_path = ('zips')
        if not os.path.exists(zips_path):
            os.makedirs(zips_path)

# Comment out this line if you have .pyc or .pyo files you need to keep
        self._remove_binaries()

        self._generate_addons_file()
        self._generate_md5_file()
        print("Finished updating addons xml and md5 files")

    def _create_zips(self, addon_id, version):
        xml_path = os.path.join(addon_id, 'addon.xml')
        addon_folder = os.path.join('zips', addon_id)
        if not os.path.exists(addon_folder):
            os.makedirs(addon_folder)

        final_zip = os.path.join('zips', addon_id, '{0}-{1}.zip'.format(addon_id, version))
        if not os.path.exists(final_zip):
            print("NEW ADD-ON - Creating zip for: {0} v.{1}".format(addon_id, version))
            zip = zipfile.ZipFile(final_zip, 'w', compression=zipfile.ZIP_DEFLATED )
            root_len = len(os.path.dirname(os.path.abspath(addon_id)))
            
            ignore = ['.git', '.github', '.gitignore', '.DS_Store', 'thumbs.db', '.idea', 'venv']
            
            for root, dirs, files in os.walk(addon_id):
                # remove any unneeded git artifacts
                for i in ignore:
                    if i in dirs:
                        try:
                            dirs.remove(i)
                        except:
                            pass
                    for f in files:
                        if f.startswith(i):
                            try:
                                files.remove(f)
                            except:
                                pass
                
                archive_root = os.path.abspath(root)[root_len:]

                for f in files:
                    fullpath = os.path.join(root, f)
                    archive_name = os.path.join(archive_root, f)
                    zip.write(fullpath, archive_name, zipfile.ZIP_DEFLATED)
            
            zip.close()
            
            # Copy over the icon, fanart and addon.xml to the zip directory
            copyfiles = ['icon.png', 'fanart.jpg', 'addon.xml']
            files = os.listdir(addon_id)
            for file in files:
                if file in copyfiles:
                    shutil.copy(os.path.join(addon_id, file), addon_folder)

# Remove any instances of pyc or pyo files
    def _remove_binaries(self):
        for parent, dirnames, filenames in os.walk('.'):
            for fn in filenames:
                if fn.lower().endswith('pyo') or fn.lower().endswith('pyc'):
                    compiled = os.path.join(parent, fn)
                    py_file = compiled.replace('.pyo', '.py').replace('.pyc', '.py')
                    if os.path.exists(py_file):
                        try:
                            os.remove(compiled)
                            print("Removed compiled python file:")
                            print(compiled)
                            print('-----------------------------')
                        except:
                            print("Failed to remove compiled python file:")
                            print(compiled)
                            print('-----------------------------')
                    else:
                        print("Compiled python file found but no matching .py file exists:")
                        print(compiled)
                        print('-----------------------------')

    def _generate_addons_file(self):
        # addon list
        addons = os.listdir('.')

        # final addons text
        addons_xml = u"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<addons>\n"

        # loop thru and add each addons addon.xml file
        for addon in addons:
            try:
                if not os.path.isdir(addon) or addon == "zips" or addon.startswith('.'):
                    continue
                _path = os.path.join(addon, "addon.xml")
                xml_lines = open(_path, "r", encoding='utf-8').read().splitlines()
                addon_xml = ""

                # loop thru cleaning each line
                ver_found = False
                for line in xml_lines:
                    if line.find( "<?xml" ) >= 0:
                        continue
                    if 'version="' in line and not ver_found:
                        version = re.compile('version="(.+?)"').findall(line)[0]
                        ver_found = True
                    addon_xml += line.rstrip() + "\n"
                addons_xml += addon_xml.rstrip() + "\n\n"

                # Create the zip files                
                self._create_zips(addon, version)

            except Exception as e:
                print("Excluding {0} for {1}".format(_path, e))

        # clean and add closing tag
        addons_xml = addons_xml.strip() + u"\n</addons>\n"
        self._save_file(addons_xml.encode('utf-8'), file=os.path.join('zips', 'addons.xml'), decode=True)

    def _generate_md5_file(self):
        try:
            m = hashlib.md5(open(os.path.join('zips', 'addons.xml'), 'r', encoding='utf-8').read().encode('utf-8')).hexdigest()
            self._save_file(m, file=os.path.join('zips', 'addons.xml.md5'))
        except Exception as e:
            print("An error occurred creating addons.xml.md5 file!\n{0}".format(e))

    def _save_file(self, data, file, decode=False):
        try:
            if decode:
                open(file, 'w', encoding='utf-8').write(data.decode('utf-8'))
            else:
                open(file, 'w').write(data)
        except Exception as e:
            print("An error occurred saving {0} file!\n{1}".format(file, e))


if __name__ == "__main__":
    Generator()
