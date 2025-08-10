import xml.etree.ElementTree as ET
from pathlib import Path
import shutil
import fileinput
import os
import tempfile

class Wsconf:
    proj_template_dir=''
    workspacedir=''
    project_name=''
    mytldmycomp=''

wsconf = None

def init_proj_group(proj_name, group_id):
    global wsconf
    if not wsconf:
        wsconf = Wsconf()
    wsconf.project_name = proj_name
    wsconf.mytldmycomp = group_id

def get_proj_template_dir():
    return wsconf.proj_template_dir
def get_mytldmycomp():
    return wsconf.mytldmycomp
def get_group_id():
    return wsconf.mytldmycomp
def get_project_name():
    return wsconf.project_name
def get_workspace_dir():
    return wsconf.workspacedir

def copy_tree(src_dir, dst_dir, ignored_names=None):
    if ignored_names is None:
        ignored_names = []
    for src_file in src_dir.glob('*'):
            if src_file.name in ignored_names:
                continue
            dst_file = dst_dir / src_file.relative_to(src_dir)
            print(f"copy {src_file} to {dst_file}")
            if src_file.is_file():
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                if not dst_file.exists():
                    shutil.copy2(src_file, dst_file)
                else:
                    print('skip: ', dst_file)
            elif src_file.is_dir():
                copy_tree(src_file, dst_file, ignored_names)

def create_proj_template(artifact_id=None):
    if not wsconf:
        return
    proj_name = get_project_name()
    group_id = get_mytldmycomp()
    if not artifact_id:
        artifact_id = proj_name
    #wsconf.project_name = proj_name
    #wsconf.mytldmycomp = group_id
    import os, tempfile
    #proj_dir = tempfile.mkdtemp(dir=wsconf.proj_template_dir)
    proj_root = os.path.join(get_workspace_dir(), proj_name)
    #shutil.copytree(os.path.join(proj_template_dir, ''), proj_root, ignore=ignore_existing_files)
    src_dir = Path(get_proj_template_dir())
    dst_dir = Path(get_workspace_dir(), proj_name)
    print("from", src_dir)
    print("to", dst_dir)
    copy_tree(src_dir, dst_dir)

def fix_pom():
    proj_name = get_project_name()
    group_id = get_mytldmycomp()
    restore_pom(proj_name)
    update_pom(proj_name, group_id)

def update_pom(project_name, groupId, artifactId=None):
    if not wsconf:
        return
    if not artifactId:
        artifactId = project_name
    parent = Path(get_workspace_dir()) / project_name
    pom = parent / 'pom.xml'
    tree = ET.parse(str(pom))
    root = tree.getroot()
    default_ns = root.tag.split('}')[0][1:]
    group_node = root.find('./{%s}groupId' % default_ns)
    arti_node = root.find('./{%s}artifactId' % default_ns)
    name_node = root.find('./{%s}name' % default_ns)
    #print("groupId", group_node.text)
    #print("artifactId", arti_node.text)
    group_node.text = groupId
    arti_node.text =  artifactId
    name_node.text =  artifactId
    tree.write(str(pom), encoding='UTF-8', xml_declaration=True, default_namespace=default_ns)
    #print(f"{str(pom)} updated!")

def restore_pom(proj_name):
    src_file = Path(get_proj_template_dir()) / 'pom.xml'
    dst_file = Path(get_workspace_dir()) / proj_name / 'pom.xml'
    print(src_file)
    print(dst_file)
    shutil.copy2(src_file, dst_file)

def proc_single_javafile(txtfile):
    with fileinput.FileInput(txtfile,encoding="utf-8",inplace=True) as f:
        print('----- ', txtfile)
        replacement_tldcompapp = get_mytldmycomp()+'.'+get_project_name()
        replacement_tldcomp = get_mytldmycomp()
        print('--repl-- ', replacement_tldcompapp)
        for line in f:
            # 使用 .replace() 方法替换文本内容
            new_line = line.replace('mytld.mycompany.myapp', replacement_tldcompapp)
            #print(new_line, end='')
            new_line2 = new_line.replace('mytld.mycompany', replacement_tldcomp)
            print(new_line2, end='')


def __proj_java_srcfiles():
    '''deprecated, not used anymore'''
    prj_basedir = Path(get_workspace_dir()) / get_project_name()
    directory = prj_basedir / Path("src/main/java")# 获取目录的路径
    #directory = Path('./src/main/java')
    # 迭代目录下的所有文件和子目录
    for file_path in directory.glob('**/*'):
        # 如果是文件，打印它的路径
        if file_path.is_file():
            print(file_path)
            proc_single_javafile(str(file_path))
        else:
            continue

def remove_common_prefix(tp1, tp2):
    # 查找 tp2 中与 tp1 相同的部分的索引位置
    index = len(tp1)
    for i, item in enumerate(tp2):
        if i >= len(tp1) or item != tp1[i]:
            index = i
            break

    # 提取 tp2 中的剩余部分
    new_tp2 = tp2[index:]
    
    return new_tp2

def change_package_and_move(parent_dir, src, dst):
    global wsconf
    if not wsconf:
        print("wsconf is not initialized.")
        return
    stripval_tuple = tuple(src.split('.'))
    # Get the absolute path of the parent directory
    parent_dir = os.path.abspath(parent_dir)

    # Create a Path object for the parent directory
    parent_path = Path(parent_dir)

    # Iterate through all Java files in the parent directory and its subdirectories
    proclist = []
    for file_path in parent_path.glob('**/*.java'):
        proclist.append(file_path)

    #for file_path in parent_path.glob('**/*.java'):
    for file_path in proclist:
        # Read the source file content
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Update the package declaration in the source file content if necessary
        tobe_replace = f'package {src};\n'
        package_line = f'package {dst};\n'
        updated_content = []
        for line in lines:
            if line.startswith('package '):
                if line.rstrip() == tobe_replace.rstrip():
                    line = package_line
            if line.startswith('@ComponentScan'):
                if "mytld.mycompany.myapp" in line:
                    app_package = f'{get_mytldmycomp()}.{get_project_name()}'
                    line = line.replace("mytld.mycompany.myapp", app_package)
            updated_content.append(line)

        # Write the updated content to the source file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(updated_content)

        # Get the relative file path within the parent directory
        relative_path = file_path.relative_to(parent_dir)
        print('file_path', file_path)
        print('relative_path', relative_path)

        # Rename the parent package directories if the source package matches
        if str(relative_path).startswith(src.replace('.', os.sep)):
            #new_relative_path = relative_path.parts[0:len(src.split('.'))] + dst.split('.') + relative_path.parts[len(src.split('.')):]
            new_relative_path_tuple = tuple(relative_path.parts[0:len(src.split('.'))]) + tuple(dst.split('.')) + tuple(relative_path.parts[len(src.split('.')):])
            new_rel_path_tp = remove_common_prefix(stripval_tuple, new_relative_path_tuple)
            new_relative_path = os.sep.join(new_rel_path_tp)
            print('new_relative_path', new_relative_path)
            # Get the new absolute file path
            new_file_path = parent_path / new_relative_path
            print('new_file_path', new_file_path)
            # Create any missing parent directories if needed
            new_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Move the file to the new absolute path
            os.rename(file_path, new_file_path)

def clean_empty_java_packages(root_dir):
    """
    删除 root_dir 下所有空的子目录（递归）。
    如果删除子目录导致父目录变为空，则继续删除父目录。
    root_dir 本身不会被删除，即使它是空的。
    """
    print("---->>>>>check_empty_packages dir: ", root_dir)
    root = Path(root_dir)

    if not root.is_dir():
        return  # 如果根目录不存在或不是目录，直接返回

    def is_empty(directory):
        """判断目录是否为空（不包含任何文件或子目录）"""
        return not any(directory.iterdir())

    # 使用 post-order 遍历：先处理子目录，再处理父目录
    # 获取所有子目录并排序（深度优先，子目录优先）
    all_subdirs = sorted(root.rglob('*'), key=lambda p: -len(p.parts))  # 按路径长度倒序，先处理深层目录

    for path in all_subdirs:
        if path.is_dir() and is_empty(path):
            print(f"Removing empty directory: {path}")
            path.rmdir()  # 删除空目录

def proj_java_directory():
    prj_basedir = Path(get_workspace_dir()) / get_project_name()
    src_root_dir = prj_basedir / Path("src/main/java")# 获取目录的路径

    org_v66_demo2 = get_mytldmycomp()+'.'+get_project_name()
    org_v66 = get_mytldmycomp()
    org_v66_demo2_dir = org_v66_demo2.replace('.','/')
    org_v66_dir = org_v66.replace('.','/')
    print("org_v66_demo2_dir",org_v66_demo2_dir)
    print("org_v66_dir",org_v66_dir)
    print('parent_dir', src_root_dir)
    print('source_package', 'mytld.mycompany.myapp')
    print('destination_package', org_v66_demo2)

    change_package_and_move(src_root_dir, 'mytld.mycompany.myapp', org_v66_demo2)
    #change_package_and_move(src_root_dir, 'mytld.mycompany.config', f'{org_v66}.config')
    change_package_and_move(src_root_dir, 'com.sh4008.wctl.myapp', 'com.sh4008.wctl'+'.'+get_project_name())
    print("-----------------")
    clean_empty_java_packages(src_root_dir)
    src_test_root_dir = prj_basedir / Path("src/test/java")
    change_package_and_move(src_test_root_dir, 'mytld.mycompany.myapp', org_v66_demo2)
    clean_empty_java_packages(src_test_root_dir)

def utf8_openhook(filename, mode):
        return open(filename, mode, encoding='utf-8')

def content_replace(relpath, searchfor, replacement):
    fileForUpdate = Path(get_workspace_dir()) / get_project_name() / relpath
    with fileinput.FileInput(fileForUpdate, inplace=True) as f:
        for line in f:
            # 使用 .replace() 方法替换文本内容
            new_line = line.replace(searchfor, replacement)
            print(new_line, end='')

def content_replace2(relpath, searchfor, replacement):
    fileForUpdate = Path(get_workspace_dir()) / get_project_name() / relpath
    tempfile_path = ''
    with open(fileForUpdate, encoding='utf-8') as r:
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as temp_file:
            tempfile_path = temp_file.name
            #print('tempfile_path', tempfile_path)
            for line in r.readlines():
                #print(line)
                repline = line.rstrip().replace(searchfor, replacement)
                temp_file.write(f"{repline}\n")
            temp_file.flush()
    
    shutil.copy(temp_file.name, fileForUpdate)
    os.remove(temp_file.name)

# def proc_webxml():
#     relpath = "src/main/webapp/WEB-INF/web.xml"
#     webxml = Path(get_workspace_dir()) / get_project_name() / relpath
#     with fileinput.FileInput(webxml, inplace=True) as f:
#         for line in f:
#             # 使用 .replace() 方法替换文本内容
#             new_line = line.replace('mytld.mycompany', get_mytldmycomp())
#             print(new_line, end='')

def proc_webxml():
    relpath = "src/main/webapp/WEB-INF/web.xml"
    searchfor = 'mytld.mycompany'
    replacement = get_mytldmycomp()
    content_replace(relpath, searchfor, replacement)

def proc_servlet_context():
    relpath = "src/main/webapp/WEB-INF/spring/appServlet/servlet-context.xml"
    searchfor = 'com.sh4008.wctl.myapp'
    replacement = f'com.sh4008.wctl.{get_project_name()}'
    content_replace(relpath, searchfor, replacement)

def proc_appconfig():
    relpath = "src/main/java/com/sh4008/config/AppConfig.java"
    searchfor = 'mytld.mycompany.myapp'
    replacement = f'{get_mytldmycomp()}.{get_project_name()}'
    content_replace2(relpath, searchfor, replacement)

def proc_webmvcconf():
    relpath = "src/main/java/com/sh4008/config/WebMvcConfiguration.java"
    searchfor = 'mytld.mycompany.myapp'
    replacement = f'{get_mytldmycomp()}.{get_project_name()}'
    content_replace2(relpath, searchfor, replacement)

def get_xmlns(xmlfile):
    tree = ET.parse(xmlfile)
    root = tree.getroot()
    default_ns = root.tag.split('}')[0][1:]
    return default_ns