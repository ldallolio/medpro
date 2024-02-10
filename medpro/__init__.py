from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from dataclasses import dataclass

import medcoupling as mc
import MEDLoader as ml

from medcoupling import ON_CELLS, ON_NODES, ON_GAUSS_PT, ON_GAUSS_NE, ON_NODES_KR, ON_NODES_FE

class MEDMesh():
    def __init__(self, mesh_file):
        self.mesh_file = mesh_file

    @property
    def name(self):
        return self.mesh_file.getName()
    
    @property
    def group_names(self):
        return self.mesh_file.getGroupsNames()
    
    @property
    def num_nodes(self):
        return self.mesh_file.getNumberOfNodes()
    
    @property
    def mesh_dim(self):
        return self.mesh_file.getMeshDimension()
    
    @property
    def space_dim(self):
        return self.mesh_file.getSpaceDimension()

    @property
    def coordinates(self):
        return self.mesh_file.getCoords().toNumPyArray()   

@dataclass(frozen=True)
class TimeStamp():
    iteration: int
    order: int
    time: float

class MEDField():
    def __init__(self, field, mesh_file):
        self.field = field
        self.mesh = mesh_file

    @property
    def name(self):
        return self.field.getName()

    @property
    def on_nodes(self):
        return self.field.getTypeOfField() == mc.ON_NODES

    @property
    def on_cells(self):
        return self.field.getTypeOfField() == mc.ON_CELLS

    @property
    def on_gauss_points(self):
        return self.field.getTypeOfField() == mc.ON_GAUSS_PT

    @property
    def on_nodes_per_element(self):
        return self.field.getTypeOfField() == mc.ON_GAUSS_NE

    @property
    def timestamp(self):
        time, iteration, order = self.field.getTime()
        return TimeStamp(iteration, order, time)
    
    @property
    def components(self):
        return self.field.getArray().getInfoOnComponents()    

    @property
    def units(self):
        return self.field.getArray().getUnitsOnComponents()
    
    @property
    def to_numpy(self):
        return self.field.getArray().toNumPyArray()

class MEDFieldEvol():
    def __init__(self, file_field, mesh):
        self.file_field = file_field
        self.mesh = mesh

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
    
    def __build_field(self, field_1ts):
        assert len(self.file_field.getTypesOfFieldAvailable()) == 1
        assert len(self.file_field.getTypesOfFieldAvailable()[0]) == 1
        field_type = self.file_field.getTypesOfFieldAvailable()[0][0] # TODO understand this and make it more general
        field_vals, depl_prf = field_1ts.getFieldWithProfile(field_type, 0, self.mesh.mesh_file)

        whole_mesh = self.mesh.mesh_file.getMeshAtLevel(0)
        double_field = mc.MEDCouplingFieldDouble.New(field_type, mc.ONE_TIME)
        double_field.setName(field_1ts.getName())
        double_field.setMesh(whole_mesh)
        double_field.setArray(field_vals)
        
        iteration, order, time = field_1ts.getTime()
        double_field.setTime(time, iteration, order)
        return MEDField(double_field, self.mesh)
       
    def get_field_at_timestep(self, iteration, order):
        return self.__build_field(self.file_field.getTimeStep(iteration, order))
    
    @property
    def fields_by_timestep(self):
        return {TimeStamp(*field.getTime()): self.__build_field(field) for field in self.file_field}

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
            for file_mesh in self.file_data.getMeshes():
                self.meshes_by_name[file_mesh.getName()] = MEDMesh(file_mesh)

        self.fieldevols_by_name = {}
        if self.file_data.getNumberOfFields() >= 1:
            for field_file in self.file_data.getFields():
                mesh = self.meshes_by_name[field_file.getMeshName()]
                self.fieldevols_by_name[field_file.getName()] = MEDFieldEvol(field_file, mesh)

        self.params_by_name = {}
        if self.file_data.getNumberOfParams() >= 1: # to avoid MEDLoader.InterpKernelException: MEDFileParameters::getParamAtPos : should be in [0,0)
            for param in self.file_data.getParams():
                self.fields_by_name[param.getName()] = MEDParam(param)            
