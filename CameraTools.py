import maya.cmds as cmds
import random


# Global variable to store the last selected RGB color
selected_color = [1, 0, 0]  # Default color is red
button_id = None  # Global variable for button ID to use in color editor

def get_next_camera_number():  
    # Get a list of existing cameras
    camera_names = cmds.ls('CAM_*', transforms=True)
    camera_numbers = []

    for cam in camera_names:
        try:
            # Extract the number part from the camera name
            number = int(cam.split('_')[1])
            camera_numbers.append(number)
        except (ValueError, IndexError):
            continue  # Skip if we can't convert to int or if the format is unexpected

    if not camera_numbers:
        return 10  # Start at 10 if no cameras exist

    return (max(camera_numbers) // 10 + 1) * 10
    
def create_camera_text(camera_number):
    nurbs_group = cmds.textCurves(ch=False, f="Arial", t=f'CAM_{camera_number:03}')
    new_nurbs_group = cmds.rename(nurbs_group, f'CAM_{camera_number:03}'+'_Text_GRP')
    cmds.makeIdentity(new_nurbs_group, apply=True, translate=True, rotate=True, scale=True, normal=True)
    cmds.rotate(0, 90, 0, new_nurbs_group)
    cmds.scale(0.1, 0.1, 0.1, new_nurbs_group)
    cmds.move(0.2, 0.35, 1, new_nurbs_group)
    cmds.setAttr(f"{new_nurbs_group}.overrideEnabled", 1)
    cmds.setAttr(f"{new_nurbs_group}.overrideRGBColors", 1)
    cmds.setAttr(f"{new_nurbs_group}.overrideColorR", selected_color[0])
    cmds.setAttr(f"{new_nurbs_group}.overrideColorG", selected_color[1])
    cmds.setAttr(f"{new_nurbs_group}.overrideColorB", selected_color[2])
    
    return new_nurbs_group

def create_camera(scale_value):
    camera_number = get_next_camera_number()  # Get the next camera number

    # Desired camera name
    camera_name = f'CAM_{camera_number:03}'
    camera_ctrl_name = f"{camera_name}_Main"
    camera_shake_ctrl_name = f"{camera_name}_Shake_CTL"

    # Create the camera
    camera_transform, camera_shape = cmds.camera(dgm=True, dr=True, ovr=1.0)

    # Rename the camera transform and shape
    camera_new_shape = cmds.rename(camera_shape, f'{camera_name}_Cam')
    camera_new_transform = cmds.rename(camera_transform, camera_name)

    # Modify the camera settings
    cmds.setAttr(f"{camera_new_shape}.displayGateMaskOpacity", 1)
    cmds.setAttr(f"{camera_new_shape}.displayGateMaskColor", 0, 0, 0, type="double3")

    # Enable drawing overrides
    cmds.setAttr(f"{camera_new_shape}.overrideEnabled", 1)
    cmds.setAttr(f"{camera_new_shape}.overrideRGBColors", 1)
    cmds.setAttr(f"{camera_new_shape}.overrideColorR", selected_color[0])
    cmds.setAttr(f"{camera_new_shape}.overrideColorG", selected_color[1])
    cmds.setAttr(f"{camera_new_shape}.overrideColorB", selected_color[2])
    
    new_nurbs_group = create_camera_text(camera_number)  # Pass the camera number to the function

    # Create camera controls
    camera_main_ctrl = cmds.curve(d=1, p=[(-0.6, 0, 1), (0.6, 0, 1), (0.6, 0, -1), (-0.6, 0, -1), (-0.6, 0, 1)])
    camera_shake_ctrl = cmds.curve(d=1, p=[(0, 0, 0), (0.8, 0, 0), (0.8, 0, 0.8), (0, 0, 0.8),
                                           (0, 0, 0), (0, 0.8, 0), (0.8, 0.8, 0), (0.8, 0, 0),
                                           (0.8, 0.8, 0), (0.8, 0.8, 0.8), (0.8, 0, 0.8), (0.8, 0.8, 0.8),
                                           (0, 0.8, 0.8), (0, 0, 0.8), (0, 0.8, 0.8), (0, 0.8, 0)]) 
                                           
    cmds.setAttr(f"{camera_main_ctrl}.overrideEnabled", 1)
    cmds.setAttr(f"{camera_main_ctrl}.overrideRGBColors", 1)
    cmds.setAttr(f"{camera_main_ctrl}.overrideColorR", selected_color[0])
    cmds.setAttr(f"{camera_main_ctrl}.overrideColorG", selected_color[1])
    cmds.setAttr(f"{camera_main_ctrl}.overrideColorB", selected_color[2])
    
    cmds.setAttr(f"{camera_shake_ctrl}.overrideEnabled", 1)
    cmds.setAttr(f"{camera_shake_ctrl}.overrideRGBColors", 1)
    cmds.setAttr(f"{camera_shake_ctrl}.overrideColorR", selected_color[0])
    cmds.setAttr(f"{camera_shake_ctrl}.overrideColorG", selected_color[1])
    cmds.setAttr(f"{camera_shake_ctrl}.overrideColorB", selected_color[2])

    # Move camera controls
    cmds.move(0, -0.4, 0.6, camera_main_ctrl) 
    cmds.move(-0.4, -0.4, -0.3, camera_shake_ctrl)

    # Freeze transformations for each control
    cmds.makeIdentity(camera_main_ctrl, apply=True, translate=True, rotate=True, scale=True)
    cmds.makeIdentity(camera_shake_ctrl, apply=True, translate=True, rotate=True, scale=True)

    # Set the pivot for the controls based on their positions
    main_control_pos = cmds.xform(camera_main_ctrl, query=True, worldSpace=True, translation=True)
    shake_control_pos = cmds.xform(camera_shake_ctrl, query=True, worldSpace=True, translation=True)

    cmds.xform(camera_main_ctrl, piv=main_control_pos)
    cmds.xform(camera_shake_ctrl, piv=shake_control_pos)

    # Rename controls
    camera_shake_ctrl = cmds.rename(camera_shake_ctrl, camera_shake_ctrl_name)    
    camera_main_ctrl = cmds.rename(camera_main_ctrl, camera_ctrl_name)   

    # Parent the camera to the shake control, and the shake control to the main control
    cmds.parent(new_nurbs_group, camera_name)
    cmds.parent(camera_name, camera_shake_ctrl_name)
    cmds.parent(camera_shake_ctrl_name, camera_ctrl_name)

    # Check if the camera group exists; if not, create it
    if not cmds.objExists('CAM_GRP'):
        cmds.group(camera_ctrl_name, name='CAM_GRP')
    else:
        cmds.parent(camera_ctrl_name, 'CAM_GRP')

    # Scale the main control if a scale value is provided
    if scale_value:
        cmds.scale(float(scale_value), float(scale_value), float(scale_value), camera_ctrl_name)
        # Freeze transformations after scaling
        cmds.makeIdentity(camera_ctrl_name, apply=True, translate=True, rotate=True, scale=True)

    # Translate and rotate the main control to the perspective camera position and rotation if the checkbox is selected
    if cmds.checkBox("createFromPerspCheckBox", query=True, value=True):
        persp_camera_pos = cmds.xform("persp", query=True, worldSpace=True, translation=True)
        persp_camera_rot = cmds.xform("persp", query=True, worldSpace=True, rotation=True)
        cmds.xform(camera_ctrl_name, worldSpace=True, translation=persp_camera_pos)
        cmds.xform(camera_ctrl_name, worldSpace=True, rotation=persp_camera_rot)

    print(f"Camera '{camera_name}' created!")

def show_color_editor(*args):
    global button_id  # Use the global button ID
    # Open the color editor in mini mode
    cmds.colorEditor(mini=False, rgb=cmds.button(button_id, query=True, backgroundColor=True))

    # Check if the user clicked "OK" in the color editor
    if cmds.colorEditor(query=True, rgb=True):
        rgb = cmds.colorEditor(query=True, rgb=True)
        # Change the button color based on the selected color
        cmds.button(button_id, edit=True, backgroundColor=rgb)
        # Update the selected color
        global selected_color
        selected_color = rgb
        
def select_main_object(main_name):
    if cmds.objExists(main_name):
        cmds.select(main_name)

def toggle_visibility(main_name, button):
    if cmds.objExists(main_name):
        current_visibility = cmds.getAttr(main_name + ".visibility")
        new_visibility = not current_visibility
        cmds.setAttr(main_name + ".visibility", new_visibility)

        # Update button icon based on new visibility state
        icon = 'eye.png' if new_visibility else 'eyeHide.png'  # Ensure you have eyeHide.png for the hidden state
        cmds.iconTextButton(button, edit=True, image=icon)

def set_camera_focal_length(focal_length):
    selected_objects = cmds.ls(selection=True)

    if not selected_objects:
        cmds.warning("Please select a camera or an object that has a camera as a child.")
        return

    def set_focal_length(camera):
        cmds.setAttr(f"{camera}.focalLength", focal_length)
        print(f"Set focal length of camera '{camera}' to {focal_length}.")

    for obj in selected_objects:
        if cmds.nodeType(obj) == 'camera':
            set_focal_length(obj)
        else:
            children = cmds.listRelatives(obj, children=True) or []
            for child in children:
                if cmds.nodeType(child) == 'camera':
                    set_focal_length(child)
                    break
            else:
                cameras = cmds.listRelatives(obj, allDescendents=True, type='camera')
                if cameras:
                    for camera in cameras:
                        set_focal_length(camera)
                else:
                    print(f"No camera found in children of '{obj}'.")

def key_focal_length():
    selected_objects = cmds.ls(selection=True)
    if not selected_objects:
        cmds.warning("Please select a camera or an object that has a camera as a child.")
        return

    def key_focal(camera):
        cmds.setKeyframe(f"{camera}.focalLength")
        print(f"Keyframe set for camera '{camera}' at focal length.")

    for obj in selected_objects:
        if cmds.nodeType(obj) == 'camera':
            key_focal(obj)
        else:
            children = cmds.listRelatives(obj, children=True) or []
            for child in children:
                if cmds.nodeType(child) == 'camera':
                    key_focal(child)
                    break
            else:
                cameras = cmds.listRelatives(obj, allDescendents=True, type='camera')
                if cameras:
                    for camera in cameras:
                        key_focal(camera)
                else:
                    print(f"No camera found in children of '{obj}'.")


def show_custom_lens_window():
    if cmds.window("customLensWindow", exists=True):
        cmds.deleteUI("customLensWindow")

    window = cmds.window("customLensWindow", title="Custom Lens", widthHeight=(100, 100))
    cmds.columnLayout(adjustableColumn=True)

    cmds.text(label="Enter Custom Focal Length:")
    focal_length_field = cmds.intField(value=35)  # Default value

    def apply_custom_focal_length(*args):
        focal_length = cmds.floatField(focal_length_field, query=True, value=True)
        set_camera_focal_length(focal_length)
        cmds.deleteUI(window)  # Close the window after applying

    cmds.button(label="Apply", command=apply_custom_focal_length)
    cmds.showWindow(window)        
        
def lens_pack():
    if cmds.window("focalLengthWindow", exists=True):
        cmds.deleteUI("focalLengthWindow")

    window = cmds.window("focalLengthWindow", title="Lens Pack", widthHeight=(300, 150))  # Increased height

    # Create a main layout
    cmds.columnLayout(adjustableColumn=False)

    # Focal length buttons
    cmds.rowLayout(numberOfColumns=7, adjustableColumn=3, columnWidth=[(1, 50), (2, 50), (3, 50), (4, 50), (5, 50), (6, 50), (7, 50)], mar=10)

    focal_lengths = [18, 24, 35, 50, 85, 100, 135]
    for length in focal_lengths:
        cmds.button(label=str(length) + 'mm', command=lambda _, l=length: set_camera_focal_length(l), width=50)

    cmds.setParent('..')  # Go back to the main layout

    # Add a new row for the additional features
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=2)
    
    cmds.text(label='                                          ')
    cmds.button(label="Key Focal Length", command=lambda _: key_focal_length())
    cmds.button(label="Custom Lens", command=lambda _: show_custom_lens_window())

    cmds.setParent('..')  # Go back to the main layout
    cmds.showWindow(window)
    
def bake_noise_on_selected_objects(rotation_noise_x, rotation_noise_y, rotation_noise_z, bake_steps, use_custom_range, start_frame, end_frame, ease_in_out, ease_value):
    selection = cmds.ls(selection=True)

    if not selection:
        cmds.warning("Please select one or more objects.")
        return

    scaling_factor = 0.1

    if use_custom_range:
        start_frame = int(start_frame)
        end_frame = int(end_frame)
    else:
        start_frame = int(cmds.playbackOptions(query=True, min=True))
        end_frame = int(cmds.playbackOptions(query=True, max=True))

    for frame in range(start_frame, end_frame + 1, bake_steps):
        cmds.currentTime(frame)

        for obj in selection:
            world_rot = cmds.xform(obj, query=True, rotation=True, worldSpace=True)
            local_rot = cmds.xform(obj, query=True, rotation=True, worldSpace=False)

            # Calculate noise intensity based on ease values
            noise_intensity_x = rotation_noise_x * scaling_factor
            noise_intensity_y = rotation_noise_y * scaling_factor
            noise_intensity_z = rotation_noise_z * scaling_factor

            if ease_in_out:
                if frame <= start_frame + ease_value:
                    # Ease in
                    factor = (frame - start_frame) / ease_value
                    noise_intensity_x *= factor
                    noise_intensity_y *= factor
                    noise_intensity_z *= factor
                elif frame >= end_frame - ease_value:
                    # Ease out
                    factor = (end_frame - frame) / ease_value
                    noise_intensity_x *= factor
                    noise_intensity_y *= factor
                    noise_intensity_z *= factor

            noise_rotation = [
                random.uniform(-noise_intensity_x, noise_intensity_x),
                random.uniform(-noise_intensity_y, noise_intensity_y),
                random.uniform(-noise_intensity_z, noise_intensity_z)
            ]

            new_local_rot = [local_rot[i] + noise_rotation[i] for i in range(3)]

            cmds.xform(obj, worldSpace=True, rotation=new_local_rot)
            cmds.setKeyframe(obj, attribute='rotateX', value=new_local_rot[0])
            cmds.setKeyframe(obj, attribute='rotateY', value=new_local_rot[1])
            cmds.setKeyframe(obj, attribute='rotateZ', value=new_local_rot[2])

            if ease_in_out:
                cmds.keyTangent(obj, attribute='rotateX', inTangentType='spline', outTangentType='spline', inWeight=ease_value, outWeight=ease_value)
                cmds.keyTangent(obj, attribute='rotateY', inTangentType='spline', outTangentType='spline', inWeight=ease_value, outWeight=ease_value)
                cmds.keyTangent(obj, attribute='rotateZ', inTangentType='spline', outTangentType='spline', inWeight=ease_value, outWeight=ease_value)

def create_noise_window():
    if cmds.window("noiseWindow", exists=True):
        cmds.deleteUI("noiseWindow")

    cmds.window("noiseWindow", title="Shoulder Noise", widthHeight=(400, 240))

    cmds.columnLayout(columnAlign='center', adjustableColumn=True, mar=5)

    cmds.text(label="Bake Shoulder Noise", align='center')

    # Single row layout for all axes
    cmds.rowLayout(numberOfColumns=6, columnAlign=(1, 'center'))

    cmds.text(label=' X:  ')
    rotation_noise_x_field = cmds.floatField(value=0.5, step=0.1, pre=0)

    cmds.text(label='Y:  ')
    rotation_noise_y_field = cmds.floatField(value=0.5, step=0.1, pre=0)

    cmds.text(label='Z:  ')
    rotation_noise_z_field = cmds.floatField(value=0.5, step=0.1, pre=0)

    cmds.setParent('..')  # Go back to the parent layout

    cmds.text(label="Baking Steps:", align='center')
    bake_steps_field = cmds.intField(value=1, minValue=1)

    # Checkbox for setting custom frame range
    set_range_checkbox = cmds.checkBox(label="Set Frame Range", value=False, align='center')
    
    # Checkbox for Ease In/Out
    ease_in_out_checkbox = cmds.checkBox(label="Ease In/Out", value=False, align='center', enable=False)

    # Row layout for start and end frame fields
    cmds.rowLayout(numberOfColumns=6, columnAlign=(4, 'center'))

    cmds.text(label='   Start:', align='center')
    start_frame_field = cmds.intField(value=1, width=30, enable=False)

    cmds.text(label='End:', align='center')
    end_frame_field = cmds.intField(value=100, width=30, enable=False)
    
    cmds.text(label='Ease:', align='center')
    ease_frame_field = cmds.intField(value=20, width=30, enable=False)

    cmds.setParent('..')  # Go back to the parent layout

    # Function to toggle frame fields and ease in/out checkbox
    def toggle_frame_fields(*args):
        is_checked = cmds.checkBox(set_range_checkbox, query=True, value=True)
        cmds.intField(start_frame_field, edit=True, enable=is_checked)
        cmds.intField(end_frame_field, edit=True, enable=is_checked) 
        cmds.checkBox(ease_in_out_checkbox, edit=True, enable=is_checked)
    
    def toggle_ease_field(*args):
        is_checked = cmds.checkBox(ease_in_out_checkbox, query=True, value=True)
        cmds.intField(ease_frame_field, edit=True, enable=is_checked)

    # Connect checkbox state to enable/disable the frame fields and ease in/out checkbox
    cmds.checkBox(set_range_checkbox, edit=True, changeCommand=toggle_frame_fields)
    cmds.checkBox(ease_in_out_checkbox, edit=True, changeCommand=toggle_ease_field)

    def on_apply_noise(*args):
        rotation_noise_x = cmds.floatField(rotation_noise_x_field, query=True, value=True)
        rotation_noise_y = cmds.floatField(rotation_noise_y_field, query=True, value=True)
        rotation_noise_z = cmds.floatField(rotation_noise_z_field, query=True, value=True)
        bake_steps = cmds.intField(bake_steps_field, query=True, value=True)
        use_custom_range = cmds.checkBox(set_range_checkbox, query=True, value=True)
        start_frame = cmds.intField(start_frame_field, query=True, value=True)
        end_frame = cmds.intField(end_frame_field, query=True, value=True)
        ease_in_out = cmds.checkBox(ease_in_out_checkbox, query=True, value=True)
        ease_value = cmds.intField(ease_frame_field, query=True, value=True)  # Get the ease value
        
        bake_noise_on_selected_objects(rotation_noise_x, rotation_noise_y, rotation_noise_z, bake_steps, use_custom_range, start_frame, end_frame, ease_in_out, ease_value)

    cmds.button(label="Apply Noise", command=on_apply_noise)

    cmds.showWindow("noiseWindow")
    
def set_camera_aim():
    # Check if any objects are selected
    selected_objects = cmds.ls(selection=True, type='transform')
    if not selected_objects:
        cmds.warning("No objects selected.")
        return
    
    for obj in selected_objects:
        # Check if the selected object has a child camera
        camera_shapes = cmds.listRelatives(obj, allDescendents=True, type='camera', fullPath=True)
        if not camera_shapes:
            cmds.warning(f"No camera shape nodes found in {obj}.")
            continue
        
        # Get the transform node of the camera
        cam_transform = cmds.listRelatives(camera_shapes[0], parent=True, fullPath=True)[0]
        
        # Get camera position and rotation
        cam_pos = cmds.xform(cam_transform, query=True, translation=True, worldSpace=True)
        cam_rot = cmds.xform(cam_transform, query=True, rotation=True, worldSpace=True)

        # Get the transform node of the camera
        cam_transform = cmds.listRelatives(camera_shapes[0], parent=True, fullPath=False)[0]
        
        # Create a locator and name it after the camera (use the short name of the transform)
        locator_name = cmds.spaceLocator(name=f"{cam_transform}_Loc")[0]
        
        # Move locator to camera position
        cmds.xform(locator_name, translation=cam_pos, worldSpace=True)
        
        # Rotate locator to match camera rotation
        cmds.xform(locator_name, rotation=cam_rot, worldSpace=True)

        # Move locator forward along the camera's Z axis
        forward_vector = om.MVector(0, 0, 1)
        cam_matrix = cmds.getAttr(f"{cam_transform}.wm")
        cam_matrix = om.MMatrix(cam_matrix)
        forward_vector = forward_vector * cam_matrix
        
        # Calculate new position for the locator (+20 in the Z direction)
        new_loc_pos = [cam_pos[0] + forward_vector.x * -5,
                       cam_pos[1] + forward_vector.y * -5,
                       cam_pos[2] + forward_vector.z * -5]

        # Move the locator to the new position
        cmds.xform(locator_name, translation=new_loc_pos, worldSpace=True)
                
        # Set the locator size
        cmds.setAttr(f"{locator_name}.localScaleX", 15)
        cmds.setAttr(f"{locator_name}.localScaleY", 15)
        cmds.setAttr(f"{locator_name}.localScaleZ", 15)

        # Aim constraint the camera to the locator
        cmds.aimConstraint(locator_name, cam_transform, aim=[1, 0, 0], upVector=[0, 1, 0], worldUpType="vector", maintainOffset=True)
        
        # Check if the camera group exists; if not, create it
        if not cmds.objExists('LOC_GRP'):
            cmds.group(locator_name, name='LOC_GRP')
            cmds.parent('LOC_GRP', 'CAM_GRP')
        else:
            cmds.parent(locator_name, 'LOC_GRP')
        
        # Sample the camera's override color and apply it to the locator
        camera_shape = camera_shapes[0]
        
        # Check if the camera override is enabled and query the color
        override_enabled = cmds.getAttr(f"{camera_shape}.overrideEnabled")
        if override_enabled:
            # Sample the camera's override color attributes
            color_r = cmds.getAttr(f"{camera_shape}.overrideColorR")
            color_g = cmds.getAttr(f"{camera_shape}.overrideColorG")
            color_b = cmds.getAttr(f"{camera_shape}.overrideColorB")
            
            # Apply the same color to the locator
            locator_shape = cmds.listRelatives(locator_name, shapes=True)[0]
            cmds.setAttr(f"{locator_shape}.overrideEnabled", 1)
            cmds.setAttr(f"{locator_shape}.overrideRGBColors", 1)
            cmds.setAttr(f"{locator_shape}.overrideColorR", color_r)
            cmds.setAttr(f"{locator_shape}.overrideColorG", color_g)
            cmds.setAttr(f"{locator_shape}.overrideColorB", color_b)
    
    
def show_camera_ui():
    global button_id  # Make the button ID global

    # Check if the window already exists
    if cmds.window("cameraUI", exists=True):
        cmds.deleteUI("cameraUI")

    # Create a new window
    window = cmds.window("cameraUI", title="Camera Tools", widthHeight=(200, 300))

    # Create a row layout for the left and right columns
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)

    # Left column
    cmds.columnLayout(adjustableColumn=True)

    cmds.rowLayout(numberOfColumns=8, mar=5, cal=[1, 'left'])
    cmds.text(l="      ")  # Spacer
    button_id = cmds.button(label="    ", command=show_color_editor, backgroundColor=[1, 0, 0])
    cmds.text(l="  ")  # Spacer
    cmds.button(width=100, label="Create Camera", command=lambda x: create_camera(cmds.textField(scale_text_field, query=True, text=True)))
    cmds.text(label="  Scale:")
    cmds.text(l=" ")  # Spacer
    scale_text_field = cmds.textField("scaleTextField", w=30, tx='20')

    cmds.setParent('..')  # End of row layout

    cmds.rowLayout(numberOfColumns=5, mar=5, cal=[1, 'left'])
    cmds.text(l="      ")  # Spacer
    cmds.checkBox("createFromPerspCheckBox", label="Create from Persp")
    cmds.text(l="       ")  # Spacer
    cmds.button(label="Lens Pack", command=lambda x: lens_pack(), width=80, height=30)
    cmds.setParent('..')  # End of row layout
    
    cmds.rowLayout(numberOfColumns=4, cal=[1, 'left'])
    cmds.text(l="       ")  # Spacer
    cmds.button(label="Shoulder Noise", command=lambda x: create_noise_window(), width=80, height=30)
    cmds.text(l="                 ")  # Spacer
    cmds.button(label="Add Aim", command=lambda x: set_camera_aim(), width=80, height=30)
    cmds.setParent('..')  # Go back to the row layout
    

    cmds.setParent('..')  # Go back to the row layout

    # Right column
    cmds.columnLayout(adjustableColumn=True)

    # List all cameras excluding 'persp'
    all_cameras = cmds.listCameras()
    for cam in all_cameras:
        if cam != 'persp':
            # Get the transform node for the camera
            transform_node = cmds.listRelatives(cam, parent=True)
            if transform_node:
                transform_name = transform_node[0]
                main_name = transform_name + '_Main'

                # Create a row layout for each camera with Select and Toggle Visibility buttons
                cmds.rowLayout(numberOfColumns=5, mar=3)
                cmds.text(label='                  ')
                cmds.text(label=transform_name)
                cmds.text(label='   ')
                cmds.button(label='Select', command=lambda _, main_name=main_name: select_main_object(main_name))

                # Create an icon button for toggling visibility
                button = cmds.iconTextButton(style='iconOnly', image='eye.png')
                cmds.iconTextButton(button, edit=True, command=lambda *args, main_name=main_name, button=button: toggle_visibility(main_name, button))

                cmds.setParent('..')  # Go back to the column layout

    cmds.setParent('..')  # Go back to the row layout
    cmds.showWindow(window)

# Call the function to show the UI
show_camera_ui()
