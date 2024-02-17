from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

import medcoupling as mc
import os

from .mesh import *
from .param import *
from .field import *
from typing import List, Dict

class MEDFilePost():

    def __init__(self, file_name : str | None = None):
        file_data : mc.MEDFileData
        if file_name is not None:
            file_data = mc.MEDFileData.New(file_name)
        else:
            file_data = mc.MEDFileData.New()
        self.file_data = file_data

        self.meshes_by_name : Dict[str, MEDMesh] = {}
        if file_name is not None and self.file_data.getNumberOfMeshes() >= 1:
            for file_mesh in self.file_data.getMeshes():
                self.meshes_by_name[file_mesh.getName()] = MEDMesh(file_mesh)

        self.fieldevols_by_name : Dict[str, MEDFieldEvol] = {}
        if file_name is not None and self.file_data.getNumberOfFields() >= 1:
            for field_file in self.file_data.getFields():
                mesh = self.meshes_by_name[field_file.getMeshName()]
                self.fieldevols_by_name[field_file.getName()] = MEDFieldEvol(mesh, field_file)

        self.params_by_name : Dict[str, MEDParam] = {}
        if file_name is not None and self.file_data.getNumberOfParams() >= 1: # to avoid MEDLoader.InterpKernelException: MEDFileParameters::getParamAtPos : should be in [0,0)
            for param in self.file_data.getParams():
                self.params_by_name[param.getName()] = MEDParam(param)

    def add_fieldevol(self, field_evol) -> None:
        self.fieldevols_by_name[field_evol.name] = field_evol

    def write(self, output_file_name : str) -> None:
        for mesh_index, mesh in enumerate(self.meshes_by_name.values()):
            if mesh_index == 0:
                mesh.mesh_file.write(output_file_name, 2)
            else:
                mesh.mesh_file.write(output_file_name, 0)
        for fieldevol in self.fieldevols_by_name.values():
            fieldevol.file_field_multits.write(output_file_name, 0)
        for param in self.params_by_name.values():
            param.param.write(output_file_name,0)       
