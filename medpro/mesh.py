import medcoupling as mc

import numpy.typing
from typing import Dict, List


class MEDProfile:
    def __init__(self, mesh, node_ids_array: mc.DataArrayInt):
        self.mesh = mesh
        self.node_ids_array = node_ids_array

    @property
    def node_ids(self) -> numpy.typing.NDArray:
        return self.node_ids_array.toNumPyArray()


class MEDGroup:
    def __init__(
        self, mesh, cell_ids_array: mc.DataArrayInt, cell_numbers_array: mc.DataArrayInt
    ):
        self.mesh = mesh
        self.cell_ids_array = cell_ids_array
        self.cell_numbers_array = cell_numbers_array

    @property
    def name(self) -> str:
        return self.cell_ids_array.getName()

    @property
    def cell_ids(self) -> numpy.typing.NDArray:
        return self.cell_ids_array.toNumPyArray()

    @property
    def cell_numbers(self) -> numpy.typing.NDArray:
        return self.cell_numbers_array.toNumPyArray()

    def to_profile(self) -> MEDProfile:
        whole_mesh: mc.MEDCouplingMesh = self.mesh.mesh_file.getMeshAtLevel(0)
        submesh_group: mc.MEDCouplingMesh = whole_mesh[self.cell_ids_array]
        group_ids_new: mc.DataArrayInt
        new_num_group_ids: int
        group_ids_new, new_num_group_ids = submesh_group.getNodeIdsInUse()
        profile_array: mc.DataArrayInt = group_ids_new.invertArrayO2N2N2O(new_num_group_ids)
        profile_array.setName(self.name)
        return MEDProfile(self.mesh, profile_array)


class MEDMesh:
    def __init__(self, mesh_file: mc.MEDFileMesh):
        self.mesh_file = mesh_file

    @property
    def name(self) -> str:
        return self.mesh_file.getName()

    @property
    def num_nodes(self) -> int:
        return self.mesh_file.getNumberOfNodes()

    @property
    def mesh_dim(self) -> int:
        return self.mesh_file.getMeshDimension()

    @property
    def space_dim(self) -> int:
        return self.mesh_file.getSpaceDimension()

    @property
    def coordinates(self) -> numpy.typing.NDArray:
        return self.mesh_file.getCoords().toNumPyArray()

    def get_group_by_name(self, group_name: str) -> MEDGroup:
        ids: mc.DataArrayInt = self.mesh_file.getGroupArr(0, group_name, False)
        labels: mc.DataArrayInt = self.mesh_file.getGroupArr(0, group_name, True)
        return MEDGroup(self, ids, labels)

    def get_cell_ids_in_boundingbox(
        self,
        x1: float,
        y1: float,
        z1: float,
        x2: float,
        y2: float,
        z2: float,
        tolerance: float = 1e-10,
    ) -> numpy.typing.NDArray:
        wholemesh: mc.MEDCouplingMesh = self.mesh_file.getMeshAtLevel(0)
        ids: mc.DataArrayInt = wholemesh.getCellsInBoundingBox(
            [x1, x2, y1, y2, z1, z2], tolerance
        )
        return ids.toNumPyArray()

    def get_cell_id_containing_point(self, x, y, z, tolerance=1e-10) -> int:
        wholemesh: mc.MEDCouplingMesh = self.mesh_file.getMeshAtLevel(0)
        return wholemesh.getCellContainingPoint([x, y, z], tolerance)

    def get_node_ids_of_cell(self, cell_id) -> List[int]:
        wholemesh: mc.MEDCouplingMesh = self.mesh_file.getMeshAtLevel(0)
        return wholemesh.getNodeIdsOfCell(cell_id)

    @property
    def group_by_name(self) -> Dict[str, MEDGroup]:
        return {
            group_name: self.get_group_by_name(group_name)
            for group_name in self.mesh_file.getGroupsNames()
        }
