import numpy as np
from .fun__ import randomString
import time
import os
import matplotlib.pyplot as plt

import tensorflow as tf
tf.compat.v1.enable_eager_execution()


class NeRF:
    "FastNeRF class"
    def __init__(self, emit, checkProcessExecution, config, media_path, save_modal=True):
        self.save_modal= save_modal 
        self.media_path = media_path
        self.checkProcessExecution = checkProcessExecution
        self.emit = emit
        self.N_samples = 64
        self.L_embed = 6
        self.number_of_iterations = 1000 # more than 1000 is for best results
        self.embed_fn = self.posenc
        self.images = []
        self.poses = []
        self.focal = 0
        self.H = 0
        self.W = 0
        self.modalDepth = 8
        self.modalWidth = 256
        self.images_len = 0
        self.testpose = []
        self.testimg = []
        self.output_video = f'/videos/vid-{randomString(8)}.mp4'
        self.video_size = 0
        self.generate_video = True 
        self.psnrs = []
        if config.get('n_iterations'):
            self.number_of_iterations = config.get('n_iterations')
        if config.get('modal_depth'):
            self.modalDepth = config.get('modal_depth')
        if config.get('modal_width'):
            self.modalWidth = config.get('modal_width')
        if config.get('n_samples'):
            self.N_samples = config.get('n_samples')
        self.model = self.init_model(D=self.modalDepth, W=self.modalWidth)
        # self.model = tf.keras.models.load_model('./models/mode.h5', compile=False)
        self.clearResultsDir()

    def saveModel(self, path):
        p = f"{path}{os.sep}saved_model"
        os.mkdir(p)
        tf.keras.models.save_model(self.model, p, save_format='tf')
        np.savez(f"{path}{os.sep}saved_model{os.sep}config.npz", H=self.H, W=self.W, focal=self.focal, testpose=self.testpose, N_samples=self.N_samples)
        return path

    def clearResultsDir(self):
        if os.path.exists('./results') and os.path.isdir('./results'):
            try:
                for root, dirs, files in os.walk('./results'):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            os.remove(file_path)
                        except OSError as e:
                            continue
            except OSError as e:
               pass 
        else:
            print(f"Directory not found")

    def loadDataset(self, path):
        data = np.load(path)
        images = data['images']
        poses = data['poses']
        self.focal = data['focal']
        self.H, self.W = images.shape[1:3]
        self.images_len= len(images)
        self.testimg = images[self.images_len - 2]
        self.testpose = poses[self.images_len - 2]
        self.images = images[:self.images_len - 3,...,:3]
        self.poses = poses[:self.images_len - 3]
   
    def pose_spherical(self, theta, phi, radius):
        trans_t = lambda t : tf.convert_to_tensor([
            [1,0,0,0],
            [0,1,0,0],
            [0,0,1,t],
            [0,0,0,1],
        ], dtype=tf.float32)

        rot_phi = lambda phi : tf.convert_to_tensor([
            [1,0,0,0],
            [0,tf.cos(phi),-tf.sin(phi),0],
            [0,tf.sin(phi), tf.cos(phi),0],
            [0,0,0,1],
        ], dtype=tf.float32)

        rot_theta = lambda th : tf.convert_to_tensor([
            [tf.cos(th),0,-tf.sin(th),0],
            [0,1,0,0],
            [tf.sin(th),0, tf.cos(th),0],
            [0,0,0,1],
        ], dtype=tf.float32)
        c2w = trans_t(radius)
        c2w = rot_phi(phi/180.*np.pi) @ c2w
        c2w = rot_theta(theta/180.*np.pi) @ c2w
        c2w = np.array([[-1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]]) @ c2w
        return c2w

    def Run(self):
        self.emit('progress', {'process': 'nerf', 'title': 'NeRF Model Processing...', 'progress': 0, 'psnr': 0})
        optimizer = tf.keras.optimizers.Adam(5e-4)
        N_iters = self.number_of_iterations 
        iternums = []
        i_plot =  1
        start_time = time.time()
        resultImagePrev = None
        for i in range(N_iters+1):
            if self.checkProcessExecution():
                break
            img_i = np.random.randint(self.images.shape[0])
            target = self.images[img_i]
            pose = self.poses[img_i]
            rays_o, rays_d = self.get_rays(self.H, self.W, self.focal, pose)
            with tf.GradientTape() as tape:
                rgb, depth, acc = self.render_rays(self.model, rays_o, rays_d, near=2., far=6., N_samples=self.N_samples, rand=True)
                loss = tf.reduce_mean(tf.square(rgb - target))
            gradients = tape.gradient(loss, self.model.trainable_variables)
            optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))
            if self.checkProcessExecution():
                break
            if i%i_plot==0:
                current_time = time.time()
                elapsed_time = current_time - start_time
                estimate_time = elapsed_time / (i + 1)
                estimate_total = estimate_time * self.number_of_iterations
                estimate_ramain_time = estimate_total - elapsed_time

                rays_o, rays_d = self.get_rays(self.H, self.W, self.focal, self.testpose)
                rgb, depth, acc = self.render_rays(self.model, rays_o, rays_d, near=2., far=6., N_samples=self.N_samples)
                loss = tf.reduce_mean(tf.square(rgb - self.testimg))
                psnr = -10. * tf.math.log(loss) / tf.math.log(10.)
                self.psnrs.append([1 + i, float(psnr.numpy())])
                iternums.append(i)
                percent = i / self.number_of_iterations * 100
                if estimate_ramain_time > 0:
                    self.emit('progress', {'estimate_time': estimate_ramain_time, 'process': 'nerf', 'title': 'Model Training (this process can take long)', 'progress': percent, 'training': {'psnr': str(psnr.numpy()), 'iteration': str(i)}})
                img = f'/results/rgb-{randomString(5)}.jpg'
                plt.imsave('.' + img, rgb.numpy())
                self.emit('result', {'iteration': i, 'image': img})
                if resultImagePrev:
                    try:
                        os.remove(resultImagePrev)
                    except Exception as _:
                        pass
                resultImagePrev = '.' + img

        self.emit('progress', {'process': 'nerf', 'title': 'Model Training (this process can take long)', 'progress': 100, 'training': {'psnr': str(psnr.numpy()), 'iteration': str(i)}})
        if self.checkProcessExecution():
            return None 
        
        if self.save_modal:
            self.saveModel(self.media_path)
        
    def posenc(self, x):
        rets = [x]
        for i in range(self.L_embed):
            for fn in [tf.sin, tf.cos]:
                rets.append(fn(2.**i * x))
        return tf.concat(rets, -1) 

    def init_model(self, D=8, W=256):
        relu = tf.keras.layers.ReLU()
        dense = lambda W=W, act=relu : tf.keras.layers.Dense(W, activation=act)

        inputs = tf.keras.Input(shape=(3 + 3 * 2 * self.L_embed))
        outputs = inputs
        for i in range(D):
            outputs = dense()(outputs)
            if i%4==0 and i>0:
                outputs = tf.concat([outputs, inputs], -1)
        outputs = dense(4, act=None)(outputs)

        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        return model

    def get_rays(self, H, W, focal, c2w):
        i, j = tf.meshgrid(tf.range(W, dtype=tf.float32), tf.range(H, dtype=tf.float32), indexing='xy')
        dirs = tf.stack([(i-W*.5)/focal, -(j-H*.5)/focal, -tf.ones_like(i)], -1)
        rays_d = tf.reduce_sum(dirs[..., np.newaxis, :] * c2w[:3,:3], -1)
        rays_o = tf.broadcast_to(c2w[:3,-1], tf.shape(rays_d))
        return rays_o, rays_d

    def render_rays(self, network_fn, rays_o, rays_d, near, far, N_samples, rand=False):
        def batchify(fn, chunk=1024*32):
            return lambda inputs : tf.concat([fn(inputs[i:i+chunk]) for i in range(0, inputs.shape[0], chunk)], 0)

        # Compute 3D query points
        z_vals = tf.linspace(near, far, N_samples)
        if rand:
            z_vals += tf.random.uniform(list(rays_o.shape[:-1]) + [N_samples]) * (far-near)/N_samples
        pts = rays_o[...,None,:] + rays_d[...,None,:] * z_vals[...,:,None]

        # Run network
        pts_flat = tf.reshape(pts, [-1,3])
        # pts_flat = self.embed_fn(pts_flat)
        pts_flat = self.posenc(pts_flat)
        raw = batchify(network_fn)(pts_flat)
        raw = tf.reshape(raw, list(pts.shape[:-1]) + [4])
        # Compute opacities and colors
        sigma_a = tf.nn.relu(raw[...,3])
        rgb = tf.math.sigmoid(raw[...,:3])
        # Do volume rendering
        dists = tf.concat([z_vals[..., 1:] - z_vals[..., :-1], tf.broadcast_to([1e10], z_vals[...,:1].shape)], -1)
        alpha = 1.-tf.exp(-sigma_a * dists)
        weights = alpha * tf.math.cumprod(1.-alpha + 1e-10, -1, exclusive=True)

        rgb_map = tf.reduce_sum(weights[...,None] * rgb, -2)
        depth_map = tf.reduce_sum(weights * z_vals, -1)
        acc_map = tf.reduce_sum(weights, -1)

        return rgb_map, depth_map, acc_map