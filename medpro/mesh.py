import medcoupling as mc

class MEDProfile:
    def __init__(self, mesh, node_ids_array):
        self.mesh = mesh
        self.node_ids_array = node_ids_array

    @property
    def node_ids(self):
        return self.node_ids_array.toNumPyArray()        

class MEDGroup:
    def __init__(self, mesh, cell_ids_array, cell_numbers_array):
        self.mesh = mesh
        self.cell_ids_array = cell_ids_array
        self.cell_numbers_array = cell_numbers_array

    @property
    def name(self):
        return self.cell_ids_array.getName()

    @property
    def cell_ids(self):
        return self.cell_ids_array.toNumPyArray()

    @property
    def cell_numbers(self):
        return self.cell_numbers_array.toNumPyArray()
    
    def to_profile(self):
        whole_mesh = self.mesh.mesh_file.getMeshAtLevel(0)
        submesh_group = whole_mesh[self.cell_ids_array]
        group_ids_new, new_num_group_ids = submesh_group.getNodeIdsInUse()
        profile_array = group_ids_new.invertArrayO2N2N2O(new_num_group_ids)
        profile_array.setName(self.name)
        return MEDProfile(self.mesh, profile_array)


class MEDMesh:
    def __init__(self, mesh_file):
        self.mesh_file = mesh_file

    @property
    def name(self):
        return self.mesh_file.getName()

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

    def get_group_by_name(self, group_name: str):
        ids = self.mesh_file.getGroupArr(0, group_name, False)
        labels = self.mesh_file.getGroupArr(0, group_name, True)
        return MEDGroup(self, ids, labels)

    @property
    def group_by_name(self):
        return {
            group_name: self.get_group_by_name(group_name)
            for group_name in self.mesh_file.getGroupsNames()
        }
