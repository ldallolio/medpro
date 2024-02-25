import medcoupling as mc

import numpy.typing
from numpy.lib import recfunctions as rfn
from typing import Dict, List, TypeVar

TMEDMesh = TypeVar("TMEDMesh", bound="MEDMesh")


class MEDProfile:
    def __init__(self, mesh: TMEDMesh, node_ids_array: mc.DataArrayInt):
        self.mesh = mesh
        self.node_ids_array = node_ids_array

    @property
    def node_ids(self) -> numpy.typing.NDArray:
        return self.node_ids_array.toNumPyArray()
    
    @property
    def cell_ids_fully_in(self) -> numpy.typing.NDArray:
        whole_mesh: mc.MEDCouplingMesh = self.mesh.mesh_file.getMeshAtLevel(0)
        return whole_mesh.getCellIdsLyingOnNodes(self.node_ids_array, fullyIn=True).toNumPyArray()
    
    @property
    def cell_ids_not_fully_in(self) -> numpy.typing.NDArray:
        whole_mesh: mc.MEDCouplingMesh = self.mesh.mesh_file.getMeshAtLevel(0)
        return whole_mesh.getCellIdsLyingOnNodes(self.node_ids_array, fullyIn=False).toNumPyArray()


class MEDGroup:
    def __init__(
        self,
        mesh: TMEDMesh,
        cell_ids_array: mc.DataArrayInt,
        cell_numbers_array: mc.DataArrayInt,
    ):
        self.mesh = mesh
        self.cell_ids_array = cell_ids_array
        self.cell_numbers_array = cell_numbers_array

    @property
    def name(self) -> str:
        return self.cell_ids_array.getName()
    
    @name.setter
    def name(self, value: str) -> None:
        self.cell_ids_array.setName(value)       

    @property
    def cell_ids(self) -> numpy.typing.NDArray:
        return self.cell_ids_array.toNumPyArray()
    
    @property
    def node_ids(self) -> numpy.typing.NDArray:
        return self.to_profile().node_ids_array.toNumPyArray()

    @property
    def cell_numbers(self) -> numpy.typing.NDArray:
        return self.cell_numbers_array.toNumPyArray()

    def to_profile(self) -> MEDProfile:
        whole_mesh: mc.MEDCouplingUMesh = self.mesh.mesh_file.getMeshAtLevel(0)
        submesh_group: mc.MEDCouplingUMesh = whole_mesh[self.cell_ids_array]
        group_ids_new: mc.DataArrayInt
        new_num_group_ids: int
        group_ids_new, new_num_group_ids = submesh_group.getNodeIdsInUse()
        profile_array: mc.DataArrayInt = group_ids_new.invertArrayO2N2N2O(
            new_num_group_ids
        )
        profile_array.setName(self.name)
        return MEDProfile(self.mesh, profile_array)


class MEDMesh:
    """Wrapper around MEDCoupling::MEDCouplingUMesh
    https://docs.salome-platform.org/latest/dev/MEDCoupling/developer/classMEDCoupling_1_1MEDFileUMesh.html
    """

    def __init__(self, mesh_file: mc.MEDFileUMesh):
        self.mesh_file = mesh_file

    @property
    def name(self) -> str:
        return self.mesh_file.getName()
    
    @name.setter
    def name(self, value: str) -> None:
        self.mesh_file.setName(value)    

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
    def components(self) -> List[str]:
        return self.mesh_file.getCoords().getVarsOnComponent()

    @property
    def coordinates(self) -> numpy.typing.NDArray:
        coords = self.mesh_file.getCoords().toNumPyArray()
        return rfn.unstructured_to_structured(coords, names = self.components, copy = False)

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
        wholemesh: mc.MEDCouplingUMesh = self.mesh_file.getMeshAtLevel(0)
        ids: mc.DataArrayInt = wholemesh.getCellsInBoundingBox(
            [x1, x2, y1, y2, z1, z2], tolerance
        )
        return ids.toNumPyArray()

    def get_cell_id_containing_point(self, x, y, z, tolerance=1e-10) -> int:
        wholemesh: mc.MEDCouplingUMesh = self.mesh_file.getMeshAtLevel(0)
        return wholemesh.getCellContainingPoint([x, y, z], tolerance)

    def get_node_ids_of_cell(self, cell_id) -> List[int]:
        wholemesh: mc.MEDCouplingUMesh = self.mesh_file.getMeshAtLevel(0)
        return wholemesh.getNodeIdsOfCell(cell_id)

    @property
    def group_by_name(self) -> Dict[str, MEDGroup]:
        return {
            group_name: self.get_group_by_name(group_name)
            for group_name in self.mesh_file.getGroupsNames()
        }
    
    def check(self) -> None:
        wholemesh: mc.MEDCouplingUMesh = self.mesh_file.getMeshAtLevel(0)
        wholemesh.checkConsistency()
        wholemesh.checkGeomConsistency()
        wholemesh.checkConsecutiveCellTypes()
