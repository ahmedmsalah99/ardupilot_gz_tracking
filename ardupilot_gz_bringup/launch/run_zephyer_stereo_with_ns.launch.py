# run_with_ns.launch.py
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import PushRosNamespace
from launch_ros.substitutions import FindPackageShare
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode

def generate_launch_description():
    ns = LaunchConfiguration('ns', default='uav1')   # change default as you like

    # adjust package/name/path to where zephyr_city.launch.py lives
    pkg_share = FindPackageShare('ardupilot_gz_bringup')
    included = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([pkg_share, '/launch/zephyr_city_stereo.launch.py']),
        launch_arguments={
            'rviz': 'true',
            'use_gz_tf': 'true',
        }.items()
    )

    image_processing_container = ComposableNodeContainer(
    name='image_proc_container',
    namespace='uav1',
    package='rclcpp_components',
    executable='component_container',
    composable_node_descriptions=[
        # --- Right Camera Rectification ---
        ComposableNode(
            package='image_proc',
            plugin='image_proc::RectifyNode',
            name='rectify_right',
            remappings=[
                ('image', '/uav1/camera_right/image'),
                ('camera_info', '/uav1/camera_right/camera_info'),
                ('image_rect', '/uav1/camera_right/image_rect')
            ],
            parameters=[
                {'approximate_sync': True}, # <--- THE KEY PARAMETER
                {'queue_size': 20}           # Higher queue helps with slow systems
            ]
        ),
        # --- Left Camera Rectification ---
        ComposableNode(
            package='image_proc',
            plugin='image_proc::RectifyNode',
            name='rectify_left',
            remappings=[
                ('image', '/uav1/camera_left/image'),
                ('camera_info', '/uav1/camera_left/camera_info'),
                ('image_rect', '/uav1/camera_left/image_rect')
            ],
            parameters=[
                {'approximate_sync': True},
                {'queue_size': 20}
            ]
        ),
        # # --- 3. Disparity (The Stereo Engine) ---
        # ComposableNode(
        #     package='stereo_image_proc',
        #     plugin='stereo_image_proc::DisparityNode',
        #     name='disparity_node',
        #     remappings=[
        #         ('left/image_rect', '/uav1/camera_left/image_rect'),
        #         ('left/camera_info', '/uav1/camera_left/camera_info'),
        #         ('right/image_rect', '/uav1/camera_right/image_rect'),
        #         ('right/camera_info', '/uav1/camera_right/camera_info'),
        #         ('disparity', 'camera/disparity')
        #     ],
        #     parameters=[
        #         {'approximate_sync': True},
        #         {'offset': 0},           # X-offset of right camera
        #         {'max_disparity': 64},   # How "close" it looks. Increase for closer objects.
        #         {'min_disparity': 0},
        #         {'stereo_algorithm': 0}  # 0 = Block Matching, 1 = Semi-Global Block Matching
        #     ]
        # ),
        # # --- 4. PointCloud (Disparity to 3D) ---
        # ComposableNode(
        #     package='stereo_image_proc',
        #     plugin='stereo_image_proc::PointCloudNode',
        #     name='point_cloud_node',
        #     remappings=[
        #         ('left/image_rect', '/uav1/camera_left/image_rect'),
        #         ('left/camera_info', '/uav1/camera_left/camera_info'),
        #         ('disparity', 'camera/disparity'),
        #         ('points2', 'camera/points2') # This is your PointCloud topic
        #     ],
        #     parameters=[
        #         {'approximate_sync': True},
        #         {'use_color': True}, # This will color the 3D points using the RGB image
        #         {'slop': 0.2},         # Increase this (0.2 seconds is generous)
        #         {'queue_size': 30}     # Buffer more messages
        #     ]
        # )
    ],
    output='screen',
)
    
	# --- image_proc node ---
    image_proc_node = Node(
        package='image_proc',
        executable='image_proc',
        name='image_proc',
        output='screen',
        remappings=[
            ('image', '/uav1/camera_right/image'),
            ('image_raw', '/uav1/camera_right/image'),
            ('image_mono', '/cam_right/image_raw'),
            ('camera_info','/uav1/camera_right/camera_info')
        ]
    )

    image_proc_node2 = Node(
        package='image_proc',
        executable='image_proc',
        name='image_proc2',
        output='screen',
        remappings=[
            ('image', '/uav1/camera_left/image'),
            ('image_raw', '/uav1/camera_left/image'),
            ('image_mono', '/cam_left/image_raw'),
            ('camera_info','/uav1/camera_left/camera_info')
        ]
    )

    

    return LaunchDescription([
        DeclareLaunchArgument('ns', default_value='uav1', description='namespace to push'),
        # image_proc_node,
        # image_proc_node2,
        image_processing_container,
        PushRosNamespace(ns),
        included
    ])
