#!/usr/bin/env python3
"""
Quick Robot Demo
================
A simple demonstration script that creates a robot and shows how to use it
with the Text2Robot pipeline.

Usage:
    python quick_robot_demo.py
"""

import os
import sys
import pathlib
import xml.etree.ElementTree as ET
import shutil


def create_demo_robot():
    """
    Create a complete demo robot with all necessary files
    """
    print("🤖 Creating Demo Robot...")
    print("=" * 60)

    # Robot parameters
    robot_name = "DemoBot"
    output_dir = pathlib.Path("./demo_robot_output")
    output_dir.mkdir(exist_ok=True)

    # Create URDF
    urdf_path = output_dir / f"{robot_name}.urdf"

    robot = ET.Element('robot', name=robot_name)

    # Base link - the robot's body
    print("\n📦 Creating robot body (base_link)...")
    base = ET.SubElement(robot, 'link', name='base_link')

    visual = ET.SubElement(base, 'visual')
    geometry = ET.SubElement(visual, 'geometry')
    ET.SubElement(geometry, 'box', size='0.4 0.25 0.12')
    material = ET.SubElement(visual, 'material', name='blue')
    ET.SubElement(material, 'color', rgba='0 0 1 1')

    collision = ET.SubElement(base, 'collision')
    geometry = ET.SubElement(collision, 'geometry')
    ET.SubElement(geometry, 'box', size='0.4 0.25 0.12')

    inertial = ET.SubElement(base, 'inertial')
    ET.SubElement(inertial, 'mass', value='3.5')
    ET.SubElement(inertial, 'inertia',
                 ixx='0.02', ixy='0', ixz='0',
                 iyy='0.03', iyz='0', izz='0.04')

    # Define leg configurations
    legs = {
        'front_left': {'x': 0.15, 'y': 0.15, 'name': 'FL'},
        'front_right': {'x': 0.15, 'y': -0.15, 'name': 'FR'},
        'back_left': {'x': -0.15, 'y': 0.15, 'name': 'BL'},
        'back_right': {'x': -0.15, 'y': -0.15, 'name': 'BR'}
    }

    print(f"🦵 Creating 4 legs with 2 joints each...")

    for leg_id, config in legs.items():
        x, y = config['x'], config['y']
        name = config['name']

        # Upper leg (thigh)
        upper_link = ET.SubElement(robot, 'link', name=f'{name}_upper_leg')

        visual = ET.SubElement(upper_link, 'visual')
        ET.SubElement(visual, 'origin', xyz='0 0 -0.08', rpy='0 0 0')
        geometry = ET.SubElement(visual, 'geometry')
        ET.SubElement(geometry, 'cylinder', radius='0.025', length='0.16')
        material = ET.SubElement(visual, 'material', name='gray')
        ET.SubElement(material, 'color', rgba='0.5 0.5 0.5 1')

        collision = ET.SubElement(upper_link, 'collision')
        ET.SubElement(collision, 'origin', xyz='0 0 -0.08', rpy='0 0 0')
        geometry = ET.SubElement(collision, 'geometry')
        ET.SubElement(geometry, 'cylinder', radius='0.025', length='0.16')

        inertial = ET.SubElement(upper_link, 'inertial')
        ET.SubElement(inertial, 'mass', value='0.3')
        ET.SubElement(inertial, 'inertia',
                     ixx='0.002', ixy='0', ixz='0',
                     iyy='0.002', iyz='0', izz='0.00001')

        # Shoulder joint
        shoulder = ET.SubElement(robot, 'joint',
                                name=f'{name}_shoulder_joint',
                                type='revolute')
        ET.SubElement(shoulder, 'parent', link='base_link')
        ET.SubElement(shoulder, 'child', link=f'{name}_upper_leg')
        ET.SubElement(shoulder, 'origin', xyz=f'{x} {y} -0.06', rpy='0 0 0')
        ET.SubElement(shoulder, 'axis', xyz='1 0 0')
        ET.SubElement(shoulder, 'limit',
                     lower='-1.57', upper='1.57',
                     effort='12', velocity='15')
        ET.SubElement(shoulder, 'dynamics', damping='0.1', friction='0.05')

        # Lower leg (shin)
        lower_link = ET.SubElement(robot, 'link', name=f'{name}_lower_leg')

        visual = ET.SubElement(lower_link, 'visual')
        ET.SubElement(visual, 'origin', xyz='0 0 -0.09', rpy='0 0 0')
        geometry = ET.SubElement(visual, 'geometry')
        ET.SubElement(geometry, 'cylinder', radius='0.018', length='0.18')
        material = ET.SubElement(visual, 'material', name='dark_gray')
        ET.SubElement(material, 'color', rgba='0.3 0.3 0.3 1')

        collision = ET.SubElement(lower_link, 'collision')
        ET.SubElement(collision, 'origin', xyz='0 0 -0.09', rpy='0 0 0')
        geometry = ET.SubElement(collision, 'geometry')
        ET.SubElement(geometry, 'cylinder', radius='0.018', length='0.18')

        inertial = ET.SubElement(lower_link, 'inertial')
        ET.SubElement(inertial, 'mass', value='0.2')
        ET.SubElement(inertial, 'inertia',
                     ixx='0.0015', ixy='0', ixz='0',
                     iyy='0.0015', iyz='0', izz='0.00001')

        # Knee joint
        knee = ET.SubElement(robot, 'joint',
                            name=f'{name}_knee_joint',
                            type='revolute')
        ET.SubElement(knee, 'parent', link=f'{name}_upper_leg')
        ET.SubElement(knee, 'child', link=f'{name}_lower_leg')
        ET.SubElement(knee, 'origin', xyz='0 0 -0.16', rpy='0 0 0')
        ET.SubElement(knee, 'axis', xyz='1 0 0')
        ET.SubElement(knee, 'limit',
                     lower='-2.8', upper='0.2',
                     effort='12', velocity='15')
        ET.SubElement(knee, 'dynamics', damping='0.1', friction='0.05')

        # Foot (end effector)
        foot_link = ET.SubElement(robot, 'link', name=f'{name}_foot')

        visual = ET.SubElement(foot_link, 'visual')
        geometry = ET.SubElement(visual, 'geometry')
        ET.SubElement(geometry, 'sphere', radius='0.025')
        material = ET.SubElement(visual, 'material', name='black')
        ET.SubElement(material, 'color', rgba='0 0 0 1')

        collision = ET.SubElement(foot_link, 'collision')
        geometry = ET.SubElement(collision, 'geometry')
        ET.SubElement(geometry, 'sphere', radius='0.025')

        inertial = ET.SubElement(foot_link, 'inertial')
        ET.SubElement(inertial, 'mass', value='0.05')
        ET.SubElement(inertial, 'inertia',
                     ixx='0.0001', ixy='0', ixz='0',
                     iyy='0.0001', iyz='0', izz='0.0001')

        # Fixed joint for foot
        foot_joint = ET.SubElement(robot, 'joint',
                                   name=f'{name}_foot_joint',
                                   type='fixed')
        ET.SubElement(foot_joint, 'parent', link=f'{name}_lower_leg')
        ET.SubElement(foot_joint, 'child', link=f'{name}_foot')
        ET.SubElement(foot_joint, 'origin', xyz='0 0 -0.18', rpy='0 0 0')

    # Write URDF
    tree = ET.ElementTree(robot)
    ET.indent(tree, space='  ')
    tree.write(urdf_path, encoding='utf-8', xml_declaration=True)

    print(f"\n✅ URDF created: {urdf_path}")

    # Create a simple training configuration
    config_path = output_dir / "train_config.yaml"
    config_content = """# Training Configuration for DemoBot
task:
  name: RobotDog
  physics_engine: physx

  env:
    numEnvs: 256
    envSpacing: 3.0

    urdfAsset:
      file: DemoBot.urdf

    randomCommandVelocityRanges:
      linear_x: [-0.6, 0.6]
      linear_y: [-0.4, 0.4]
      yaw: [-1.0, 1.0]

    control:
      stiffness: 30.0
      damping: 0.5
      actionScale: 0.5

    rewards:
      scales:
        tracking_lin_vel: 1.5
        tracking_ang_vel: 0.8
        lin_vel_z: -2.0
        ang_vel_xy: -0.05
        orientation: -1.0
        torques: -0.0001
        action_rate: -0.01

training:
  max_iterations: 500
  save_interval: 100
  learning_rate: 0.001
"""

    with open(config_path, 'w') as f:
        f.write(config_content)

    print(f"✅ Config created: {config_path}")

    # Create usage instructions
    readme_path = output_dir / "README.md"
    readme_content = f"""# {robot_name} - Demo Robot

## Robot Specifications

- **Type**: Quadrupedal walking robot
- **Legs**: 4 (Front Left, Front Right, Back Left, Back Right)
- **Joints per leg**: 2 (Shoulder + Knee)
- **Total actuated joints**: 8
- **Body dimensions**: 0.4m × 0.25m × 0.12m
- **Total mass**: ~5.0 kg

## Joint Configuration

Each leg has:
1. **Shoulder Joint** (revolute)
   - Range: -90° to +90°
   - Connects body to upper leg
   - Controls leg abduction/adduction

2. **Knee Joint** (revolute)
   - Range: -160° to +11°
   - Connects upper leg to lower leg
   - Controls leg extension/flexion

## Files Generated

- `{robot_name}.urdf` - Robot description file
- `train_config.yaml` - Training configuration
- `README.md` - This file

## Next Steps

### 1. Visualize the Robot

You can visualize this URDF using various tools:

```bash
# Using ROS (if installed)
roslaunch urdf_tutorial display.launch model:={urdf_path}

# Using PyBullet
python -c "import pybullet as p; import pybullet_data; p.connect(p.GUI); p.setAdditionalSearchPath(pybullet_data.getDataPath()); p.loadURDF('{urdf_path}')"
```

### 2. Train with IsaacGym

To train this robot using the Text2Robot pipeline:

1. Copy the URDF to the appropriate location:
   ```bash
   mkdir -p legged_env/assets/urdf/{robot_name}
   cp {urdf_path} legged_env/assets/urdf/{robot_name}/
   ```

2. Create an experiment entry in `legged_env/envs/exp.sh`

3. Run training:
   ```bash
   cd legged_env/envs
   bash run.sh {robot_name.lower()}
   ```

### 3. Evolutionary Optimization

To evolve this robot's morphology and control:

1. Create multiple variants (30 recommended)
2. Set up URDF_Bank directory
3. Configure and run `Evolutionary_Algorithm/driver.py`

## Robot Kinematics

```
         Base Link (Body)
              |
    +---------+---------+
    |         |         |
   FL        FR        BL        BR
    |         |         |         |
  Shoulder  Shoulder  Shoulder  Shoulder
    |         |         |         |
 Upper Leg Upper Leg Upper Leg Upper Leg
    |         |         |         |
   Knee     Knee      Knee      Knee
    |         |         |         |
 Lower Leg Lower Leg Lower Leg Lower Leg
    |         |         |         |
   Foot     Foot      Foot      Foot
```

## Control Interface

The robot expects 8 joint position/torque commands:
1. FL_shoulder
2. FL_knee
3. FR_shoulder
4. FR_knee
5. BL_shoulder
6. BL_knee
7. BR_shoulder
8. BR_knee

## References

- [Text2Robot Paper](https://arxiv.org/abs/2406.19963)
- [Project Website](http://www.generalroboticslab.com/blogs/blog/2024-06-28-text2robot/index.html)
"""

    with open(readme_path, 'w') as f:
        f.write(readme_content)

    print(f"✅ README created: {readme_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("📊 ROBOT SUMMARY")
    print("=" * 60)
    print(f"Robot Name: {robot_name}")
    print(f"Output Directory: {output_dir}")
    print(f"\nStructure:")
    print(f"  - 1 base link (body)")
    print(f"  - 4 legs × 2 joints = 8 actuated joints")
    print(f"  - 4 feet (end effectors)")
    print(f"\nFiles created:")
    print(f"  1. {urdf_path}")
    print(f"  2. {config_path}")
    print(f"  3. {readme_path}")
    print("\n✅ Demo robot created successfully!")
    print("=" * 60 + "\n")

    return output_dir


def print_next_steps():
    """
    Print next steps for using the demo robot
    """
    print("\n🚀 NEXT STEPS")
    print("=" * 60)
    print("\n1️⃣  Inspect the URDF:")
    print("   cat demo_robot_output/DemoBot.urdf")

    print("\n2️⃣  Test with Text2Robot pipeline:")
    print("   python create_robot.py --show-pipeline")

    print("\n3️⃣  Create your own robot:")
    print("   python create_robot.py --name MyRobot --create-urdf")

    print("\n4️⃣  Set up evolutionary training:")
    print("   cd Evolutionary_Algorithm")
    print("   python driver.py")

    print("\n📚 For full documentation, see:")
    print("   - README.md (main project)")
    print("   - demo_robot_output/README.md (demo robot)")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  TEXT2ROBOT - Quick Demo")
    print("=" * 60 + "\n")

    output_dir = create_demo_robot()
    print_next_steps()

    print("💡 TIP: You can customize this script to create different")
    print("   robot morphologies by adjusting the parameters!\n")
