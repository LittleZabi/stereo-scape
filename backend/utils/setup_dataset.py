import os
import numpy as np
import imghdr
from PIL import Image
from scipy.spatial.transform import Rotation

class setupDataset:
    def __init__(self, images_dir, use_colmap_output, emit):
        self.emit = emit
        self.cameras = f"{os.getenv('colmap')}\\cameras.txt"
        self.images = f"{os.getenv('colmap')}\\images.txt"
        self.output_npz = os.path.join(images_dir,  'dataset.npz')
        self.output_size = 0
        self.images_dir = images_dir 
        self.total_tasks = 0
        self.obtain_tasks = 0
        self.def_pose = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        self.def_focal = np.array(800, dtype=np.float32)
        if use_colmap_output:
            self.create_npz_using_colmap(self.cameras, self.images, self.images_dir, self.output_npz)
        else:
            self.generate()
    
    def isDatasetCreated(self):
        return os.path.exists(self.output_npz)
    
    def read_cameras(self, cameras_txt_path):
        cameras = {}
        with open(cameras_txt_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line[0] == '#':
                    continue 
                data = line.strip().split()
                if len(data) < 5:
                    continue 
                camera_id = int(data[0])
                focal_length = float(data[4])
                cameras[camera_id] = focal_length
        return cameras

    def read_poses(self, images_txt_path):
        poses = {}
        with open(images_txt_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if '.jpg' not in line:
                    continue
                if line[0] == '#':
                    continue  
                data = line.strip().split()
                if len(data) < 10:
                    continue  
                if '.' in data[0]:
                    image_id = float(data[0])
                else:
                    image_id = int(data[0])
                qw, qx, qy, qz = map(float, data[1:5])
                tx, ty, tz = map(float, data[5:8])
                image_name = data[9]
                rotation_matrix = Rotation.from_quat(np.array([qw, qx, qy, qz])).as_matrix()
                pose_matrix = np.eye(4)
                pose_matrix[:3, :3] = rotation_matrix
                pose_matrix[:, 3] = [tx, ty, tz, 1]
                poses[image_id] = {
                    'quaternion': pose_matrix,
                    'image_name': image_name
                }
        return poses

    def load_images(self, image_dir):
        images = []
        i = 0
        for root, dirs, files in os.walk(image_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if imghdr.what(file_path) is not None:
                    image = np.array(Image.open(file_path).convert('RGB'), dtype=np.float32) / 255.0
                    images.append([files[i], image])
                i = i + 1
        return images

    def create_npz_using_colmap(self, cameras_txt_path, images_txt_path, image_dir, output_npz_path):
        self.emit('progress', {'progress': 0, 'process': 'generating_npz', 'title': "Creating dataset..."})
        cameras = self.read_cameras(cameras_txt_path)
        poses = self.read_poses(images_txt_path)
        nposes = []
        images = self.load_images(self.images_dir)
        nimages = [image[1] for image in images]
        focal_lengths = np.mean([cameras[cam_id] for cam_id in sorted(cameras.keys())])
        for image in images:
            n = image[0]
            if poses.get(n):
                nposes.append(poses[n]['quaternion'])
            else:
                nposes.append(self.def_pose)
        np.savez(output_npz_path, focal=np.array(focal_lengths, dtype=np.float32), poses=np.array(nposes, dtype=np.float32), images=nimages)
        self.emit('progress', {'progress': 100, 'process': 'generating_npz', 'title': "Creating dataset..."})
        self.output_size = os.path.getsize(output_npz_path)

    def generate(self):
        percent = 0
        files = [file[1] for file in self.load_images(self.images_dir)]
        poses = [self.def_pose] * (len(files) - 1)
        np.savez(self.output_npz, focal=self.def_focal, poses=np.array(poses, dtype=np.float32), images=np.array(files, dtype=np.float32))
        self.emit('progress', {'progress': 100, 'process': 'generating_npz', 'title': "Creating dataset with default poses"})

     