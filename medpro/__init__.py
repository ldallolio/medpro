from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

import medcoupling as mc
import os

from .mesh import *
from .param import *
from .field import *
from typing import List, Dict
import traceback


class MEDFilePost:
    """Wrapper around MEDCoupling::MEDFileData
    https://docs.salome-platform.org/latest/dev/MEDCoupling/developer/classMEDCoupling_1_1MEDFileData.html
    """

    def __init__(self, file_name: str | None = None):
        file_data: mc.MEDFileData
        if file_name is not None:
            file_data = mc.MEDFileData.New(file_name)
        else:
            file_data = mc.MEDFileData.New()
        self.file_data = file_data

    @property
    def meshes_by_name(self) -> Dict[str, MEDMesh]:
        try:
            return (
                {
                    file_mesh.getName(): MEDMesh(file_mesh)
                    for file_mesh in self.file_data.getMeshes()
                }
                if self.file_data.getNumberOfMeshes() >= 1
                else {}
            )
        except mc.InterpKernelException:
            return {}

    @property
    def params_by_name(self) -> Dict[str, MEDParam]:
        try:
            return (
                {
                    param.getName(): MEDParam(param)
                    for param in self.file_data.getParams()
                }
                if self.file_data.getNumberOfParams() >= 1
                else {}
            )
        except mc.InterpKernelException:
            return {}

    @property
    def fieldevols_by_name(self) -> Dict[str, MEDFieldEvol]:
        meshes_by_name = self.meshes_by_name
        try:
            return (
                {
                    field_file.getName(): MEDFieldEvol(
                        meshes_by_name[field_file.getMeshName()], field_file
                    )
                    for field_file in self.file_data.getFields()
                }
                if self.file_data.getNumberOfFields() >= 1
                else {}
            )
        except mc.InterpKernelException:
            return {}
        
    def add_mesh(self, mesh: MEDMesh) -> None:
        meshes: mc.MEDFileMeshes | None = self.file_data.getMeshes()
        if meshes is None:
            meshes = mc.MEDFileMeshes.New()
            self.file_data.setMeshes(meshes)
        meshes.pushMesh(mesh.mesh_file)        

    def add_fieldevol(self, field_evol: MEDFieldEvol) -> None:
        fields: mc.MEDFileFields | None = self.file_data.getFields()
        if fields is None:
            fields = mc.MEDFileFields.New()
            self.file_data.setFields(fields)
        fields.pushField(field_evol.file_field_multits)

    def check(self) -> None:
        meshes_by_name = self.meshes_by_name
        for mesh in meshes_by_name.values():
            mesh.check()
        for fieldevol in self.fieldevols_by_name.values():
            fieldevol.file_field_multits.checkGlobsCoherency()
            assert fieldevol.file_field_multits.getMeshName() in meshes_by_name

    def write(self, output_file_name: str) -> None:
        self.check()
        self.file_data.write33(output_file_name, 2)
