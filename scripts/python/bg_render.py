import hou
import subprocess
import platform

def getRenderNodes(node):
    """
    returns renderable nodes found in children of specified node
    """
    render_nodes = ("rop_geometry", "geometry", "Redshift_ROP", "ifd", "arnold", "opengl", "baketexture::3.0", "rib", "ris", "ribarchive", "wren", "ifdarchive", "render", "rop_alembic", "brickmap", "merge", "channel", "comp", "dsmmerge", "fetch", "wedge", "shell", "null", "dop", "alembic", "filmboxfbx", "agent", "mdd")

    node_type_name = node.type().name()
    node_children = node.allSubChildren()

    node_list = []

    if node_type_name in render_nodes:
        node_list.append(node)
        return node_list
    elif len(node_children) > 0:
        for n in node_children:
            if n.type().name() in render_nodes:
                node_list.append(n)
    else:
        print("No render node was found.\n")
        return None

    return node_list

def bg_render(kwargs):
    """
    starts a separate houdini process rendering selected node, if multiple nodes were found, then asks user to choose one
    """
    nodes = hou.selectedNodes()

    if not bool( nodes ):
        print("No nodes selected.\n")
        return

    file_path = hou.hipFile.path()
    file_name = hou.hipFile.basename()

    for node in nodes:
        top_node = node

        node_list = getRenderNodes(node)
        if len(node_list) == 0:
            return
        elif len(node_list) == 1:
            node = node_list[0]
        else:
            node_names = [n.name() for n in node_list]
            selected = hou.ui.selectFromList(choices=node_names, message="Multiple ROPs found, choose one to be rendered", title="Choose ROP")
            if len(selected) == 0:
                print("No ROP was selected.")
                return
            else:
                node = node_list[ selected[0] ]

        rop_path = node.path()
        top_node_path = top_node.path()

        frame_by_frame = ""
        if kwargs["altclick"]:
            frame_by_frame = "I"

        hscript_cmd = "render -Va{0} {1}; quit".format(frame_by_frame, rop_path)
        intro = "Rendering {0} in {1}".format(top_node_path, file_name)
        finish = "Rendering was finished, press [enter] to close terminal."

        bash_render_cmd = 'hbatch -c \\"{0}\\" {1}'.format(hscript_cmd, file_path)
        
        if platform.system() == "Linux":
            p = subprocess.Popen(["x-terminal-emulator", "-t", intro, "-e", 'bash -c "printf \\"{0}\\" && {1} && printf \\"{2}\\" && read"'.format(intro + "\\n\\n\\n", bash_render_cmd, "\\n\\n" + finish) ], stdout=subprocess.PIPE)
        elif platform.system() == "Windows":
            p = subprocess.Popen('start cmd /c "title {0} &&^echo {0} &&^echo. &&^echo. &&^{1} &&^pause "'.format(intro, bash_render_cmd.replace("\\","")), stdout=subprocess.PIPE, shell=True)
