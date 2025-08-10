import spring_create_project_lib as spcr

def run(project_id, group_id):
    spcr.wsconf = spcr.Wsconf()
    spcr.wsconf.proj_template_dir = r'D:\dev\github\springmvc-createproject-templates\template'
    spcr.wsconf.workspacedir = r'D:\dev\workspace44_29'
    spcr.init_proj_group(group_id, project_id)
    spcr.create_proj_template()
    spcr.fix_pom()
    #spcr.proc_webxml()
    spcr.proj_java_directory()
    #spcr.proc_appconfig()
    #spcr.proc_webmvcconf()

if __name__ == '__main__':
    #run('hncourse', 'com.matrixglobal')
    #run('demo3', 'org.v66')
    print("done")
