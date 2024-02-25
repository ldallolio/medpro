from dataclasses import dataclass

import medcoupling as mc

from typing import List, Dict, Any
from numpy.lib import recfunctions as rfn
import numpy.typing

from .mesh import MEDMesh, MEDProfile


@dataclass(frozen=True)
class TimeStamp:
    iteration: int
    order: int
    time: float


class MEDField:
    """Wrapper around MEDCoupling::MEDCouplingFieldDouble
    https://docs.salome-platform.org/latest/dev/MEDCoupling/developer/classMEDCoupling_1_1MEDCouplingFieldDouble.html
    """

    def __init__(
        self,
        mesh: MEDMesh,
        field_double: mc.MEDCouplingFieldDouble,
        profile: MEDProfile,
    ):
        self.mesh = mesh
        self.field_double = field_double
        self.profile = profile

    @property
    def name(self) -> str:
        return self.field_double.getName()

    @name.setter
    def name(self, value: str) -> None:
        self.field_double.setName(value)

    @property
    def on_nodes(self) -> bool:
        return self.field_double.getTypeOfField() == mc.ON_NODES

    @property
    def on_cells(self) -> bool:
        return self.field_double.getTypeOfField() == mc.ON_CELLS

    @property
    def on_gauss_points(self) -> bool:
        return self.field_double.getTypeOfField() == mc.ON_GAUSS_PT

    @property
    def on_nodes_per_element(self) -> bool:
        return self.field_double.getTypeOfField() == mc.ON_GAUSS_NE

    @property
    def timestamp(self) -> TimeStamp:
        time, iteration, order = self.field_double.getTime()
        return TimeStamp(iteration, order, time)

    def set_timestamp(self, iteration: int, order: int, time: float) -> None:
        self.field_double.setTime(time, iteration, order)

    @property
    def components(self) -> List[str]:
        return self.field_double.getArray().getInfoOnComponents()

    @property
    def units(self) -> List[str]:
        return self.field_double.getArray().getUnitsOnComponents()

    def to_numpy(self) -> numpy.typing.NDArray:
        return self.field_double.getArray().toNumPyArray()

    def to_numpy_structured(self) -> numpy.typing.NDArray:
        values = self.to_numpy()
        return rfn.unstructured_to_structured(values, names=self.components, copy=False)

    def __neg__(self):
        return MEDField(self.mesh, self.field_double.negate(), self.profile)

    def __add__(self, other: Any):
        field_sum: mc.MEDCouplingFieldDouble
        if isinstance(other, self.__class__):
            if self.mesh != other.mesh:
                raise ValueError("Cannot add two fields on different meshes.")
            if any(p is None for p in (self.profile, other.profile)) and any(p is not None for p in (self.profile, other.profile)):
                raise ValueError("Cannot add two fields if one has a profile and the other does not.") 
            if self.profile is not None and other.profile is not None:
                if self.profile.node_ids_array.getName() != other.profile.node_ids_array.getName():
                    raise ValueError(
                        f"Cannot add two fields on different profiles : {self.profile.node_ids_array.getName()=} {other.profile.node_ids_array.getName()=}."
                    )
            field_sum = self.field_double + other.field_double
            field_sum.setName(f"{self.name}_plus_{other.name}")
        elif isinstance(other, (int, float)):
            field_sum = self.field_double + other
        else:
            raise TypeError(
                "unsupported operand type(s) for +: '{}' and '{}'".format(
                    self.__class__, type(other)
                )
            )
        return MEDField(self.mesh, field_sum, self.profile)

    __radd__ = __add__

    def __iadd__(self, other: Any):
        if isinstance(other, self.__class__):
            if self.mesh != other.mesh:
                raise ValueError("Cannot add two fields on different meshes.")
            if self.profile != other.profile:
                raise ValueError("Cannot add two fields on different profiles.")
            self.field_double += other.field_double
        elif isinstance(other, (int, float)):
            self.field_double += other
        else:
            raise TypeError(
                "unsupported operand type(s) for +=: '{}' and '{}'".format(
                    self.__class__, type(other)
                )
            )
        return self

    def __sub__(self, other: Any):
        field_sub: mc.MEDCouplingFieldDouble
        if isinstance(other, self.__class__):
            if self.mesh != other.mesh:
                raise ValueError("Cannot subtract two fields on different meshes.")
            if self.profile != other.profile:
                raise ValueError("Cannot subtract two fields on different profiles.")
            field_sub = self.field_double - other.field_double
            field_sub.setName(f"{self.name}_minus_{other.name}")
        elif isinstance(other, (int, float)):
            field_sum = self.field_double - other
        else:
            raise TypeError(
                "unsupported operand type(s) for -: '{}' and '{}'".format(
                    self.__class__, type(other)
                )
            )
        return MEDField(self.mesh, field_sum, self.profile)

    def __rsub__(self, other: Any):
        field_sub: mc.MEDCouplingFieldDouble
        if isinstance(other, self.__class__):
            if self.mesh != other.mesh:
                raise ValueError("Cannot subtract two fields on different meshes.")
            if self.profile != other.profile:
                raise ValueError("Cannot subtract two fields on different profiles.")
            field_sub = other.field_double - self.field_double
            field_sub.setName(f"{self.name}_minus_{other.name}")
        elif isinstance(other, (int, float)):
            field_sum = self.field_double.negate() + other
        else:
            raise TypeError(
                "unsupported operand type(s) for -: '{}' and '{}'".format(
                    self.__class__, type(other)
                )
            )
        return MEDField(self.mesh, field_sum, self.profile)

    def __isub__(self, other: Any):
        if isinstance(other, self.__class__):
            if self.mesh != other.mesh:
                raise ValueError("Cannot subtract two fields on different meshes.")
            if self.profile != other.profile:
                raise ValueError("Cannot subtract two fields on different profiles.")
            self.field_double -= other.field_double
        elif isinstance(other, (int, float)):
            self.field_double -= other
        else:
            raise TypeError(
                "unsupported operand type(s) for -=: '{}' and '{}'".format(
                    self.__class__, type(other)
                )
            )
        return self

    def __mul__(self, other: Any):
        field_mul: mc.MEDCouplingFieldDouble
        if isinstance(other, self.__class__):
            if self.mesh != other.mesh:
                raise ValueError("Cannot multiply two fields on different meshes.")
            if self.profile != other.profile:
                raise ValueError("Cannot multiply two fields on different profiles.")
            field_mul = self.field_double * other.field_double
            field_mul.setName(f"{self.name}_mul_{other.name}")
        elif isinstance(other, (int, float)):
            field_mul = self.field_double * other
        else:
            raise TypeError(
                "unsupported operand type(s) for *: '{}' and '{}'".format(
                    self.__class__, type(other)
                )
            )
        return MEDField(self.mesh, field_mul, self.profile)

    __rmul__ = __mul__

    def __imul__(self, other: Any):
        if isinstance(other, self.__class__):
            if self.mesh != other.mesh:
                raise ValueError("Cannot multiply two fields on different meshes.")
            if self.profile != other.profile:
                raise ValueError("Cannot multiply two fields on different profiles.")
            self.field_double *= other.field_double
        elif isinstance(other, (int, float)):
            self.field_double *= other
        else:
            raise TypeError(
                "unsupported operand type(s) for *: '{}' and '{}'".format(
                    self.__class__, type(other)
                )
            )
        return self

    def extract_group(self, group_name: str):
        group = self.mesh.get_group_by_name(group_name)
        # https://docs.salome-platform.org/latest/dev/MEDCoupling/tutorial/medcoupling_fielddouble1_en.html#builing-of-a-subpart-of-a-field
        # TODO : Should distiguish on node or cell field ?
        subfield = None
        profile_nodeids_array = None
        print(f"{self.profile=}")
        print(f"{group.to_profile().node_ids_array=}")
        print(f"{self.field_double.getMesh()=}")
        print(f"{self.field_double=}")
        profile_nodeids_array = group.to_profile().node_ids_array
        print(f"{profile_nodeids_array=}")
        try:
            subfield = self.field_double.buildSubPart(group.cell_ids_array)
        except:
            subfield = self.field_double
        # profile_cell_ids = self.field_double.getMesh().getCellIdsLyingOnNodes(self.profile.node_ids_array, fullyIn=True)
        # print(f"{profile_cell_ids=}")
        # for i in range(22):
        #     try:
        #         print(f"testing {i=}")
        #         subfield2 = self.field_double.buildSubPart([i]) # group.cell_ids_array
        #         print(f"passed {i=}")
        #     except:
        #         pass
        # print(f"{profile_nodeids_array=}")
        # print(f"{subfield=}")
            

        
        #else:
        #    whole_mesh: mc.MEDCouplingMesh = self.mesh.mesh_file.getMeshAtLevel(0)            
        #    profile_cell_ids = whole_mesh.getCellIdsLyingOnNodes(self.profile.node_ids_array, fullyIn=True)
        #    group_cellids_in_profile: mc.DataArrayInt
        #    group_cellids_in_profile = group.cell_ids_array.buildIntersection(profile_cell_ids)
        #    cell_ids_array = group_cellids_in_profile
        #    subfield = self.field_double # not using buildSubPart because it does not work yet
        #    self.field_double[group_cellids_in_profile]

            #profile_mesh = whole_mesh[group_cellids_in_profile]
            #print(f"{profile_mesh=}")
            #subfield=mc.MEDCouplingFieldDouble.New(mc.ON_NODES,mc.ONE_TIME)
            #subfield.setName(self.name)
            #subfield.setMesh(profile_mesh)
            #subfield.setArray(self.field_double.getArray())
            #subfield.setTime(self.timestamp.time, self.timestamp.iteration, self.timestamp.order)

            #print(f"{group_cellids_in_profile=}")
            #subfield = fieldFromSecondApproach.buildSubPart(group_cellids_in_profile)
        # subfieldCpy=subfield.deepCopy()
        # o2n=subfieldCpy.getMesh().sortCellsInMEDFileFrmt()
        # subfieldCpy.getArray().renumberInPlace(o2n)
        return MEDField(self.mesh, subfield, MEDProfile(self.mesh, profile_nodeids_array))

    def apply_expression(self, expr: str):
        field_expr = self.field_double.applyFuncCompo(expr)
        return MEDField(self.mesh, field_expr, self.profile)

class MEDFieldEvol:
    """Wrapper around MEDCoupling::MEDFileFieldMultiTS
    https://docs.salome-platform.org/latest/dev/MEDCoupling/developer/classMEDCoupling_1_1MEDFileFieldMultiTS.html
    """

    def __init__(
        self,
        mesh: MEDMesh,
        file_field_multits: mc.MEDFileFieldMultiTS,
        profile: MEDProfile | None = None,
    ):
        self.mesh = mesh
        self.file_field_multits = file_field_multits
        self.profile = profile

    @property
    def name(self) -> str:
        return self.file_field_multits.getName()

    @name.setter
    def name(self, value: str) -> None:
        self.file_field_multits.setName(value)

    @property
    def components(self) -> List[str]:
        return self.file_field_multits.getInfo()

    @property
    def profile_by_name(self):
        return {
            self.file_field_multits.getProfile(profile_name)
            for profile_name in self.file_field_multits.getPfls()
        }

    @property
    def timesteps(self) -> List[TimeStamp]:
        return [
            TimeStamp(iteration, order, time)
            for iteration, order, time in self.file_field_multits.getTimeSteps()
        ]

    def __build_field(self, field_1ts: mc.MEDFileAnyTypeField1TS):
        field_type: int = self.file_field_multits.getTypesOfFieldAvailable()[0][
            0
        ]  # TODO understand this and make it more general
        # probably it is mc.ON_CELLS etc
        field_vals: mc.DataArrayDouble
        field_prf: mc.DataArrayInt
        field_vals, field_prf = field_1ts.getFieldWithProfile(
            field_type, 0, self.mesh.mesh_file
        )
        double_field: mc.MEDCouplingFieldDouble = mc.MEDCouplingFieldDouble.New(
            field_type, mc.ONE_TIME
        )
        double_field.setName(field_1ts.getName())
        whole_mesh: mc.MEDCouplingMesh = self.mesh.mesh_file.getMeshAtLevel(0)
        profile_cell_ids = whole_mesh.getCellIdsLyingOnNodes(field_prf, fullyIn=True)
        computed_mesh=whole_mesh[profile_cell_ids]
        computed_mesh.setName(self.mesh.mesh_file.getName())
        profile_names = field_1ts.getPflsReallyUsed()
        if len(profile_names) == 1:
            field_prf.setName(profile_names[0])
        elif len(profile_names) >= 2:
            raise ValueError(
                f"Found multiple ({profile_names=}) profiles for field {field_1ts.getName()=}"
            )
        else:
            profile_name = f"PFL{field_1ts.getName()}"
            field_prf.setName(profile_name)
        double_field.setMesh(computed_mesh)
        double_field.setArray(field_vals)

        iteration, order, time = field_1ts.getTime()
        double_field.setTime(time, iteration, order)
        return MEDField(self.mesh, double_field, MEDProfile(self.mesh, field_prf))

    def get_field_at_timestep(self, iteration: int, order: int):
        return self.__build_field(self.file_field_multits.getTimeStep(iteration, order))

    def extract_group(self, group_name: str):
        group = self.mesh.get_group_by_name(group_name)
        extracted_fieldevol: mc.MEDFileFieldMultiTS = mc.MEDFileFieldMultiTS.New()
        extracted_fieldevol.setName(f"{self.name}_{group_name}")
        for _, field in self.field_by_timestep.items():
            subfield: MEDField = field.extract_group(group_name)
            extracted_fieldevol.appendFieldProfile(
                subfield.field_double,
                self.mesh.mesh_file,
                0,
                subfield.profile.node_ids_array,
            )
        return MEDFieldEvol(self.mesh, extracted_fieldevol, subfield.profile)

    def add_field(self, med_field: MEDField):
        if med_field.timestamp in self.field_by_timestep:
            raise ValueError(
                f"Timestamp {med_field.timestamp} already present in field_evol"
            )

        self.file_field_multits.appendFieldProfile(
            med_field.field_double,
            self.mesh.mesh_file,
            0,
            med_field.profile.node_ids_array,
        )

    @property
    def field_by_timestep(self) -> Dict[TimeStamp, MEDField]:
        return {
            TimeStamp(*field_1ts.getTime()): self.__build_field(field_1ts)
            for field_1ts in self.file_field_multits
        }
