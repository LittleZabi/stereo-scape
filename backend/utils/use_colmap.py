import subprocess
import os
from .fun__ import deleteFilesAndFolder

class COLMAP:
    def __init__(self, images_path, emit, checkProcessExecution):
        self.images_path = images_path
        self.db_path = f"{os.getenv('colmap')}\\outputs\\database.db"
        self.sparse = f"{os.getenv('colmap')}\\outputs\\sparse\\"
        self.colmap = f"{os.getenv('colmap')}\\COLMAP.bat"
        self.output_txt = f"{os.getenv('colmap')}\\"
        self.emit = emit
        self.total_functions = 5
        self.error = False
        self.checkProcessExecution = checkProcessExecution
        self.startProcess()

    def startProcess(self) :
        pipe = [self.ExtractFeatures, self.ExhaustiveMatcher, self.Mapper, self.ConvertModel, self.delete_colmap_outputs]
        for _ in pipe:
            if self.checkProcessExecution():
                return None
            else:
                _()

    def ExtractFeatures(self):
        command = f'{self.colmap} feature_extractor --database_path {self.db_path} --image_path {self.images_path}'
        subprocess.run(['cmd', '/c', 
            [command]
        ])
        self.emit('progress', {'process': 'colmap', 'title': 'Extracting Features from images', 'progress': 1 / self.total_functions * 100})
        print('feature extracting done')

    def ExhaustiveMatcher(self):
        subprocess.run(['cmd', '/c', 
            f'{self.colmap} exhaustive_matcher --database_path {self.db_path}'
                    ])
        self.emit('progress', {'process': 'colmap', 'title': 'Colmap exhaustive matcher', 'progress': 2 / self.total_functions * 100})
        print('Mathcher done')
    
    def Mapper(self):
        command = f'{self.colmap} mapper --database_path {self.db_path} --image_path {self.images_path} --output_path {self.sparse}'
        subprocess.run(['cmd', '/c', command]) 
        self.emit('progress', {'process': 'colmap', 'title': 'Colmap mapper', 'progress': 3 / self.total_functions * 100})
        print('Mapper done!')

    def ConvertModel(self):
        if os.path.exists(self.sparse+'0/'):
            if not os.path.exists(self.sparse + '0/images.bin'):
                self.error = True
                self.emit('progress', {'message': 'Colmap is failed to extract features from image. but we can move forward with default data.', 'process': 'colmap', 'title': 'Extracting features failed ❌', 'progress': 4 / self.total_functions * 100})
                return 0
            subprocess.run(['cmd', '/c', 
            f'{self.colmap} model_converter --input_path {self.sparse}0/ --output_path {self.output_txt} --output_type TXT']) 
            self.emit('progress', {'process': 'colmap', 'title': 'Converting colmap models', 'progress': 4 / self.total_functions * 100})
            print('Converting model done')

        else:
            print("=> sparse folder not exist")
            self.error = True
            self.emit('progress', {'message': 'Colmap is failed to extract features from image. but we can move forward with default data.', 'process': 'colmap', 'title': 'Extracting features failed ❌', 'progress': 4 / self.total_functions * 100})

    

    def delete_colmap_outputs(self):
        db_path = f'{os.getcwd()}\\colmap\\outputs\\database.db'
        sparse_dir = f'{os.getcwd()}\\colmap\\outputs\\sparse\\0\\'
        if not self.error:
            self.emit('progress', {'process': 'colmap', 'title': 'Clearing up files', 'progress': 5 / self.total_functions * 100})
        deleteFilesAndFolder(db_path, deleteFolder=False, deleteFiles=True) 
        deleteFilesAndFolder(sparse_dir, deleteFiles=True) 