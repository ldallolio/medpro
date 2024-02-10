from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from dataclasses import dataclass

import medcoupling as mc
import MEDLoader as ml

from medcoupling import ON_CELLS, ON_NODES, ON_GAUSS_PT, ON_GAUSS_NE, ON_NODES_KR, ON_NODES_FE

class MEDMesh():
    def __init__(self, file_mesh):
        self.file_mesh = file_mesh

    @property
    def name(self):
        return self.file_mesh.getName()
    
    @property
    def group_names(self):
        return self.file_mesh.getGroupsNames()
    
    @property
    def num_nodes(self):
        return self.file_mesh.getNumberOfNodes()
    
    @property
    def mesh_dim(self):
        return self.file_mesh.getMeshDimension()
    
    @property
    def space_dim(self):
        return self.file_mesh.getSpaceDimension()    

@dataclass(frozen=True)
class TimeStamp():
    iteration: int
    order: int
    time: float

class MEDField():
    def __init__(self, field):
        self.field = field

    @property
    def name(self):
        return self.field.getName()

    @property
    def on_nodes(self):
        return any(t == mc.ON_NODES for t in self.field.getTypesOfFieldAvailable())

    @property
    def on_cells(self):
        return any(t == mc.ON_CELLS for t in self.field.getTypesOfFieldAvailable())

    @property
    def on_gauss_points(self):
        return any(t == mc.ON_GAUSS_PT for t in self.field.getTypesOfFieldAvailable())

    @property
    def on_nodes_per_element(self):
        return any(t == mc.ON_GAUSS_NE for t in self.field.getTypesOfFieldAvailable())

    @property
    def timestamp(self):
        iteration, order, time = self.field.getTime()
        return TimeStamp(iteration, order, time)
    
    @property
    def components(self):
        return self.field.getInfo()    

class MEDFieldEvol():
    def __init__(self, file_field):
        self.file_field = file_field

    @property
    def name(self):
        return self.file_field.getName()

    @property
    def components(self):
        return self.file_field.getInfo()
    
    @property
    def profile_names(self):
        return self.file_field.getPfls()
    
    @property
    def profiles(self):
        return [self.getProfile(profile_name) for profile_name in self.profile_names]
    
    @property
    def timesteps(self):
        return [TimeStamp(iteration, order, time) for iteration, order, time in self.file_field.getTimeSteps()]
       
    def get_field_at_timestep(self, iteration, order):
        return MEDField(self.file_field.getTimeStep(iteration, order))
    
    @property
    def fields_by_timestep(self):
        return {TimeStamp(*field.getTime()): MEDField(field) for field in self.file_field}

    def extract_group(self, group_name: str):
        pass

class MEDParam():
    def __init__(self, param):
        self.param = param

class MEDFilePost():

    def __init__(self, file_name):
        self.file_data = mc.MEDFileData.New(file_name)

        self.meshes_by_name = {}
        if self.file_data.getNumberOfMeshes() >= 1:
            for mesh_file in self.file_data.getMeshes():
                self.meshes_by_name[mesh_file.getName()] = MEDMesh(mesh_file)

        self.fieldevols_by_name = {}
        if self.file_data.getNumberOfFields() >= 1:
            for field_file in self.file_data.getFields():
                self.fieldevols_by_name[field_file.getName()] = MEDFieldEvol(field_file)

        self.params_by_name = {}
        if self.file_data.getNumberOfParams() >= 1: # to avoid MEDLoader.InterpKernelException: MEDFileParameters::getParamAtPos : should be in [0,0)
            for param in self.file_data.getParams():
                self.fields_by_name[param.getName()] = MEDParam(param)            
