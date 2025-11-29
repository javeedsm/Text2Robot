# Robot Creation Guide

## What Was Created

I've created two powerful scripts to help you build robots with the Text2Robot system:

### 1. `create_robot.py` - Main Robot Creation Tool

A comprehensive command-line tool for creating robots programmatically.

**Features:**
- Creates URDF files for quadrupedal robots from scratch
- Sets up evolutionary experiment configurations
- Displays complete Text2Robot pipeline instructions
- Fully customizable robot parameters

**Usage:**

```bash
# Create a simple quadruped URDF
python create_robot.py --name MyRobot --create-urdf

# Show complete pipeline instructions
python create_robot.py --show-pipeline

# Set up an experiment configuration
python create_robot.py --name MyRobot --setup-experiment

# Do everything at once
python create_robot.py --name MyRobot --create-urdf --setup-experiment --show-pipeline

# Specify custom output directory
python create_robot.py --name MyRobot --create-urdf --output-dir ./my_robots
```

### 2. `quick_robot_demo.py` - Quick Demo Script

Creates a complete demo robot with all files in seconds.

**Features:**
- Generates a fully functional quadruped (DemoBot)
- Creates URDF with proper physics properties
- Includes training configuration
- Generates comprehensive documentation

**Usage:**

```bash
# Simply run it - no arguments needed!
python quick_robot_demo.py
```

**Output:**
- `demo_robot_output/DemoBot.urdf` - Complete robot description
- `demo_robot_output/train_config.yaml` - Training parameters
- `demo_robot_output/README.md` - Detailed documentation

## Robot Specifications

Both scripts create quadrupedal walking robots with:

- **4 legs** (Front Left, Front Right, Back Left, Back Right)
- **2 joints per leg** (Shoulder + Knee)
- **8 total actuated joints**
- **Proper physics properties** (mass, inertia, collision)
- **Compatible with** IsaacGym, PyBullet, and ROS

### Robot Structure

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

## Quick Start Examples

### Example 1: Create Your First Robot

```bash
# Create a robot named "Cheetah"
python create_robot.py --name Cheetah --create-urdf

# View the generated URDF
cat robot_output/Cheetah.urdf
```

### Example 2: Run the Demo

```bash
# Create demo robot
python quick_robot_demo.py

# Check the output
ls -lh demo_robot_output/
cat demo_robot_output/README.md
```

### Example 3: Set Up Full Experiment

```bash
# Create robot and experiment setup
python create_robot.py --name SpiderBot --create-urdf --setup-experiment

# This creates:
# - robot_output/SpiderBot.urdf
# - Evolutionary_Algorithm/experiments/SpiderBot_Experiment.py
```

## Integration with Text2Robot Pipeline

### Step 1: Use Generated URDF in Training

```bash
# Copy URDF to assets directory
mkdir -p legged_env/assets/urdf/MyRobot
cp robot_output/MyRobot.urdf legged_env/assets/urdf/MyRobot/

# Train the robot
cd legged_env/envs
bash run.sh myrobot
```

### Step 2: Visualize the Robot

```bash
# Using PyBullet (if installed)
python -c "import pybullet as p; p.connect(p.GUI); p.loadURDF('robot_output/MyRobot.urdf')"
```

### Step 3: Evolutionary Training

```bash
# Set up URDF bank with variants
mkdir -p Evolutionary_Algorithm/MyExperiment/URDF_Bank

# Run evolutionary algorithm
cd Evolutionary_Algorithm
python driver.py
```

## Customization

### Modify Robot Dimensions

Edit the scripts to change robot parameters:

```python
# In create_robot.py or quick_robot_demo.py

# Change body size
box = ET.SubElement(geometry, 'box', size='0.5 0.3 0.15')  # larger body

# Change leg positions
leg_positions = {
    'fl': {'x': 0.20, 'y': 0.18},  # wider stance
    # ... etc
}

# Change joint limits
ET.SubElement(shoulder, 'limit',
             lower='-2.0', upper='2.0',  # more range
             effort='15', velocity='20')  # stronger/faster
```

### Modify Number of Joints

Currently creates 2 joints per leg (shoulder + knee). You can add:
- Hip abduction/adduction joints
- Ankle joints
- Toe joints

## Text2Robot Complete Pipeline

1. **Text → Mesh** (Meshy AI)
   - Visit https://www.meshy.ai/
   - Generate STL from text description

2. **Mesh → CAD** (Fusion360)
   - Use `Fusion360_Scripts/Wrapper`
   - Geometric slicing and assembly

3. **CAD → URDF** (Fusion360 Export)
   - Export robot description
   - Create 30 variants

4. **URDF → Trained Robot** (These Scripts!)
   - Use `create_robot.py` or `quick_robot_demo.py`
   - Train with IsaacGym

5. **Evolution** (Evolutionary Algorithm)
   - Run `driver.py`
   - Evolve morphology and control

6. **Sim2Real** (Optional)
   - 3D print robot
   - Deploy to hardware

## Robot Physics Properties

The generated URDFs include:

- **Mass distribution**: Realistic for each component
- **Inertia tensors**: Proper rotational dynamics
- **Collision geometry**: For physics simulation
- **Joint limits**: Realistic range of motion
- **Joint dynamics**: Damping and friction
- **Materials**: Visual appearance properties

## Troubleshooting

### URDF won't load in simulator

Check that:
- All masses are > 0
- Inertia matrices are positive definite
- Joint limits are valid (lower < upper)
- Parent/child links are correctly specified

### Robot falls over immediately

Adjust:
- Initial joint positions
- PD controller gains (stiffness, damping)
- Base link mass distribution

### Joints move erratically

Tune:
- Joint damping values
- Action scaling factors
- Control frequency

## Resources

- **Text2Robot Paper**: https://arxiv.org/abs/2406.19963
- **Project Website**: http://www.generalroboticslab.com/blogs/blog/2024-06-28-text2robot/
- **IsaacGym**: https://developer.nvidia.com/isaac-gym
- **URDF Tutorial**: http://wiki.ros.org/urdf/Tutorials

## Next Steps

1. Run `python quick_robot_demo.py` to see a working example
2. Inspect the generated URDF to understand the structure
3. Create your own robot with `create_robot.py`
4. Integrate with the Text2Robot training pipeline
5. Evolve your robot using the evolutionary algorithm

## Contributing

Feel free to modify and extend these scripts for your own robot designs!

## License

Apache 2.0 (same as Text2Robot project)
