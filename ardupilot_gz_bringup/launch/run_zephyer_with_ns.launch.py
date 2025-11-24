# run_with_ns.launch.py
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import PushRosNamespace
from launch_ros.substitutions import FindPackageShare
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
def generate_launch_description():
    ns = LaunchConfiguration('ns', default='uav1')   # change default as you like

    # adjust package/name/path to where zephyr_city.launch.py lives
    pkg_share = FindPackageShare('ardupilot_gz_bringup')
    included = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([pkg_share, '/launch/zephyr_city.launch.py']),
        launch_arguments={
            'rviz': 'true',
            'use_gz_tf': 'true',
        }.items()
    )

	# --- image_proc node ---
    image_proc_node = Node(
        package='image_proc',
        executable='image_proc',
        name='image_proc',
        output='screen',
        remappings=[
            ('image_raw', '/uav1/camera/image'),
            ('image_mono', '/cam/image_raw')
        ]
    )

    

    return LaunchDescription([
        DeclareLaunchArgument('ns', default_value='uav1', description='namespace to push'),
        image_proc_node,
        PushRosNamespace(ns),
        included
    ])
