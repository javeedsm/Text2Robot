#!/usr/bin/env python3
"""
Text2Robot: Automated Robot Creation Script
============================================

This script demonstrates the complete pipeline for creating a quadrupedal robot:
1. Text prompt -> 3D Mesh (via Meshy AI)
2. Mesh -> CAD model (via Fusion360 scripts)
3. CAD -> URDF (robot description)
4. Train control policy using evolutionary algorithm
5. Deploy to simulation or real hardware

Author: Text2Robot Team
License: Apache 2.0
"""

import os
import sys
import argparse
import pathlib
import shutil
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET


class RobotCreator:
    """
    Main class for creating and managing robot generation pipeline
    """

    def __init__(self, robot_name: str, base_dir: str = "."):
        """
        Initialize the robot creator

        Args:
            robot_name: Name of the robot to create
            base_dir: Base directory for the project
        """
        self.robot_name = robot_name
        self.base_dir = pathlib.Path(base_dir)
        self.urdf_bank_dir = self.base_dir / "Evolutionary_Algorithm" / "URDF_Bank"
        self.stl_dir = self.base_dir / "STL_Files" / "Example_Meshes"

    def create_simple_quadruped_urdf(self, output_path: str) -> str:
        """
        Create a simple quadrupedal robot URDF programmatically

        This demonstrates the basic structure of a walking robot with:
        - 1 base link (body)
        - 4 legs (each with 2 joints: shoulder and knee)
        - Total of 8 actuated joints

        Args:
            output_path: Where to save the URDF file

        Returns:
            Path to the created URDF file
        """
        robot = ET.Element('robot', name=self.robot_name)

        # Create base link (robot body)
        base_link = ET.SubElement(robot, 'link', name='base_link')
        visual = ET.SubElement(base_link, 'visual')
        geometry = ET.SubElement(visual, 'geometry')
        box = ET.SubElement(geometry, 'box', size='0.3 0.2 0.1')

        inertial = ET.SubElement(base_link, 'inertial')
        ET.SubElement(inertial, 'mass', value='2.0')
        ET.SubElement(inertial, 'inertia',
                     ixx='0.01', ixy='0', ixz='0',
                     iyy='0.015', iyz='0', izz='0.02')

        # Define leg positions (front-left, front-right, back-left, back-right)
        leg_positions = {
            'fl': {'x': 0.12, 'y': 0.12},   # Front Left
            'fr': {'x': 0.12, 'y': -0.12},  # Front Right
            'bl': {'x': -0.12, 'y': 0.12},  # Back Left
            'br': {'x': -0.12, 'y': -0.12}  # Back Right
        }

        # Create each leg with shoulder and knee joints
        for leg_name, pos in leg_positions.items():
            # Upper leg link
            upper_leg = ET.SubElement(robot, 'link', name=f'{leg_name}_upper_leg')
            visual = ET.SubElement(upper_leg, 'visual')
            geometry = ET.SubElement(visual, 'geometry')
            ET.SubElement(geometry, 'cylinder', radius='0.02', length='0.15')

            inertial = ET.SubElement(upper_leg, 'inertial')
            ET.SubElement(inertial, 'mass', value='0.2')
            ET.SubElement(inertial, 'inertia',
                         ixx='0.001', ixy='0', ixz='0',
                         iyy='0.001', iyz='0', izz='0.00001')

            # Shoulder joint (connects body to upper leg)
            shoulder_joint = ET.SubElement(robot, 'joint',
                                          name=f'{leg_name}_shoulder',
                                          type='revolute')
            ET.SubElement(shoulder_joint, 'parent', link='base_link')
            ET.SubElement(shoulder_joint, 'child', link=f'{leg_name}_upper_leg')
            ET.SubElement(shoulder_joint, 'origin',
                         xyz=f"{pos['x']} {pos['y']} -0.05",
                         rpy='0 0 0')
            ET.SubElement(shoulder_joint, 'axis', xyz='1 0 0')
            ET.SubElement(shoulder_joint, 'limit',
                         lower='-1.57', upper='1.57',
                         effort='10', velocity='10')

            # Lower leg link
            lower_leg = ET.SubElement(robot, 'link', name=f'{leg_name}_lower_leg')
            visual = ET.SubElement(lower_leg, 'visual')
            geometry = ET.SubElement(visual, 'geometry')
            ET.SubElement(geometry, 'cylinder', radius='0.015', length='0.15')

            inertial = ET.SubElement(lower_leg, 'inertial')
            ET.SubElement(inertial, 'mass', value='0.15')
            ET.SubElement(inertial, 'inertia',
                         ixx='0.0008', ixy='0', ixz='0',
                         iyy='0.0008', iyz='0', izz='0.00001')

            # Knee joint (connects upper leg to lower leg)
            knee_joint = ET.SubElement(robot, 'joint',
                                      name=f'{leg_name}_knee',
                                      type='revolute')
            ET.SubElement(knee_joint, 'parent', link=f'{leg_name}_upper_leg')
            ET.SubElement(knee_joint, 'child', link=f'{leg_name}_lower_leg')
            ET.SubElement(knee_joint, 'origin',
                         xyz='0 0 -0.075',
                         rpy='0 0 0')
            ET.SubElement(knee_joint, 'axis', xyz='1 0 0')
            ET.SubElement(knee_joint, 'limit',
                         lower='-2.5', upper='0.5',
                         effort='10', velocity='10')

        # Write URDF to file
        tree = ET.ElementTree(robot)
        ET.indent(tree, space='  ')

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)

        print(f"✓ Created URDF file: {output_path}")
        print(f"  - 1 base link (body)")
        print(f"  - 4 legs with 2 joints each (shoulder + knee)")
        print(f"  - 8 total actuated joints")

        return output_path

    def setup_experiment(self, robot_names: List[str],
                        experiment_name: str = "Custom_Robot_Experiment") -> str:
        """
        Set up a new evolutionary algorithm experiment

        Args:
            robot_names: List of robot names in the URDF bank
            experiment_name: Name for the experiment

        Returns:
            Path to the experiment configuration file
        """
        exp_dir = self.base_dir / "Evolutionary_Algorithm" / "experiments"
        exp_file = exp_dir / f"{experiment_name}.py"

        config_content = f'''import os

# Experiment Configuration for {experiment_name}
# This file defines the parameters for evolutionary robot training

extra_configs = {{
    # Velocity command ranges for robot control
    "task.env.randomCommandVelocityRanges.linear_x": [-0.5, 0.5],  # Forward/backward speed (m/s)
    "task.env.randomCommandVelocityRanges.linear_y": [-0.5, 0.5],  # Left/right speed (m/s)
    "task.env.randomCommandVelocityRanges.yaw": [-1, 1]            # Rotation speed (rad/s)
}}

# Entry point for training
ENTRY_POINT = os.path.abspath(f"{{os.path.dirname(__file__)}}/../../legged_env/envs/train.py")

# Training and playback commands
HEAD_PLAY = f"python {{ENTRY_POINT}} task=RobotDog test=True num_envs=2 "
HEAD_TRAIN = f"python {{ENTRY_POINT}} task=RobotDog headless=True max_iterations=250 "

# Experiment settings
experiment_name = "{experiment_name}"
robot_names = {robot_names}  # List of all robot variants in URDF_Bank

# Training parameters:
# - max_iterations: Number of training steps per generation
# - headless: Run without visualization for faster training
# - num_envs: Number of parallel simulation environments
'''

        exp_dir.mkdir(parents=True, exist_ok=True)
        with open(exp_file, 'w') as f:
            f.write(config_content)

        print(f"✓ Created experiment config: {exp_file}")
        return str(exp_file)

    def print_pipeline_instructions(self):
        """
        Print detailed instructions for the complete Text2Robot pipeline
        """
        print("\n" + "="*70)
        print("TEXT2ROBOT PIPELINE - Complete Instructions")
        print("="*70)

        print("\n📝 STEP 1: Text to Mesh")
        print("-" * 70)
        print("1. Visit https://www.meshy.ai/")
        print("2. Enter your robot description (e.g., 'quadrupedal walking robot')")
        print("3. Include keywords like 'quadrupedal', 'walking', 'robot' for best results")
        print("4. Download the generated STL mesh file")
        print(f"5. Save to: {self.stl_dir}/")

        print("\n🔧 STEP 2: Mesh to CAD (Fusion360)")
        print("-" * 70)
        print("1. Open Fusion360 (free for students/educators)")
        print("2. Insert your STL mesh: Insert > Insert Mesh")
        print("3. Convert mesh to BRep: Modify > Convert Mesh")
        print("4. Add scripts from Fusion360_Scripts/ folder:")
        print("   - Install_Packages (run first)")
        print("   - Wrapper (performs geometric slicing)")
        print("5. Add 'Polyethylene Low Density' material to favorites")
        print("6. Run the Wrapper script to slice the mesh into robot parts")

        print("\n🤖 STEP 3: CAD to URDF")
        print("-" * 70)
        print("1. Uncomment URDF exporter in Wrapper script")
        print("2. Run script to generate URDF files")
        print("3. For multiple variants, uncomment the loop (creates 30 variations)")
        print("4. URDFs will be exported with morphology parameters")

        print("\n🧬 STEP 4: Evolutionary Training")
        print("-" * 70)
        print("1. Create experiment directory with URDF_Bank folder")
        print("2. Add at least 150 robot models (5 prompts × 30 variants)")
        print("3. Configure driver.py:")
        print("   - max_generations: Number of evolution cycles")
        print("   - inform_based_on_energy: Optimize for efficiency")
        print("   - inform_based_on_velocity: Optimize for speed")
        print("   - rough_terrain: Train on rough vs flat terrain")
        print("4. Adjust GPU settings (line 67 in driver.py)")
        print("5. Run: cd Evolutionary_Algorithm && python driver.py")

        print("\n🎮 STEP 5: Visualization & Testing")
        print("-" * 70)
        print("1. Navigate to legged_env/envs/")
        print("2. Run: bash run.sh example -pk")
        print("   -pk enables keyboard control:")
        print("   - ijkl: Arrow keys for movement")
        print("   - u/o: Yaw rotation")
        print("3. Create custom entry in exp.sh for your robot")

        print("\n🔄 STEP 6: Sim2Real Transfer (Optional)")
        print("-" * 70)
        print("1. 3D print robot parts (see Assembly Instructions.pdf)")
        print("2. Install PyLX-16A servo library on Raspberry Pi")
        print("3. Copy Sim2Real/receiver.py to robot")
        print("4. Configure UDP target URL in exp.sh")
        print("5. Run receiver.py on robot to receive commands")

        print("\n" + "="*70 + "\n")


def main():
    """
    Main entry point for robot creation
    """
    parser = argparse.ArgumentParser(
        description='Text2Robot: Create quadrupedal robots from text descriptions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Create a simple robot URDF
  python create_robot.py --name MyRobot --create-urdf

  # Show full pipeline instructions
  python create_robot.py --show-pipeline

  # Create experiment configuration
  python create_robot.py --name MyRobot --setup-experiment

  # Full setup
  python create_robot.py --name MyRobot --create-urdf --setup-experiment --show-pipeline
        '''
    )

    parser.add_argument('--name', type=str, default='CustomRobot',
                       help='Name of the robot to create')
    parser.add_argument('--create-urdf', action='store_true',
                       help='Create a simple quadrupedal URDF')
    parser.add_argument('--setup-experiment', action='store_true',
                       help='Set up evolutionary experiment configuration')
    parser.add_argument('--show-pipeline', action='store_true',
                       help='Show complete Text2Robot pipeline instructions')
    parser.add_argument('--output-dir', type=str, default='./robot_output',
                       help='Output directory for generated files')

    args = parser.parse_args()

    # If no flags provided, show help
    if not any([args.create_urdf, args.setup_experiment, args.show_pipeline]):
        parser.print_help()
        return

    # Initialize robot creator
    creator = RobotCreator(args.name)

    print(f"\n🤖 Text2Robot Creator")
    print(f"Robot Name: {args.name}\n")

    # Create URDF if requested
    if args.create_urdf:
        output_path = os.path.join(args.output_dir, f"{args.name}.urdf")
        creator.create_simple_quadruped_urdf(output_path)

    # Set up experiment if requested
    if args.setup_experiment:
        robot_names = [f'{args.name}Bot{i}' for i in range(1, 6)]
        creator.setup_experiment(robot_names, f"{args.name}_Experiment")

    # Show pipeline instructions if requested
    if args.show_pipeline:
        creator.print_pipeline_instructions()

    print("✅ Robot creation complete!\n")


if __name__ == "__main__":
    main()
