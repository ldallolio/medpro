from dataclasses import dataclass

import medcoupling as mc

from typing import List, Dict
import numpy.typing

from .mesh import MEDMesh, MEDProfile


@dataclass(frozen=True)
class TimeStamp:
    iteration: int
    order: int
    time: float


class MEDField:
    def __init__(
        self,
        mesh_file: mc.MEDFileMesh,
        field_double: mc.MEDCouplingFieldDouble,
        profile: MEDProfile | None = None,
    ):
        self.mesh = mesh_file
        self.field_double = field_double
        self.profile = profile

    @property
    def name(self) -> str:
        return self.field_double.getName()

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
    
    def __add__(self, other):
        field_sum: mc.MEDCouplingFieldDouble
        if isinstance(other, self.__class__):
            if self.mesh != other.mesh:
                raise ValueError("Cannot add two fields on different meshes.")
            if self.profile != other.profile:
                raise ValueError("Cannot add two fields on different profiles.")        
            field_sum = self.field_double + other.field_double
            field_sum.setName(f"{self.name}_plus_{other.name}")
        elif isinstance(other, (int, float)):
            field_sum = self.field_double + other
        else:
            raise TypeError("unsupported operand type(s) for +: '{}' and '{}'").format(self.__class__, type(other))        
        return MEDField(self.mesh, field_sum, self.profile)
    
    __radd__ = __add__
    
    def __mul__(self, other):
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
            raise TypeError("unsupported operand type(s) for *: '{}' and '{}'").format(self.__class__, type(other))        
        return MEDField(self.mesh, field_mul, self.profile)
    
    __rmul__ = __mul__

    def __imul__(self, val: float):
        self.field_double *= val

    def extract_group(self, group_name):
        group = self.mesh.get_group_by_name(group_name)
        subfield = self.field_double.buildSubPart(group.cell_ids_array)
        return MEDField(self.mesh, subfield)


class MEDFieldEvol:
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

    @property
    def components(self) -> List[str]:
        return self.file_field_multits.getInfo()

    @property
    def profile_by_name(self):
        return {
            self.getProfile(profile_name) for profile_name in self.file_field_multits.getPfls()
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
        field_vals: mc.DataArrayDouble
        depl_prf: mc.DataArrayInt
        field_vals, depl_prf = field_1ts.getFieldWithProfile(
            field_type, 0, self.mesh.mesh_file
        )

        whole_mesh: mc.MEDCouplingMesh = self.mesh.mesh_file.getMeshAtLevel(0)
        double_field: mc.MEDCouplingFieldDouble = mc.MEDCouplingFieldDouble.New(
            field_type, mc.ONE_TIME
        )
        double_field.setName(field_1ts.getName())
        double_field.setMesh(whole_mesh)
        double_field.setArray(field_vals)

        iteration, order, time = field_1ts.getTime()
        double_field.setTime(time, iteration, order)
        return MEDField(self.mesh, double_field)

    def get_field_at_timestep(self, iteration: int, order: int):
        return self.__build_field(self.file_field_multits.getTimeStep(iteration, order))

    def extract_group(self, group_name: str):
        group = self.mesh.get_group_by_name(group_name)
        extracted_fieldevol: mc.MEDFileFieldMultiTS = mc.MEDFileFieldMultiTS.New()
        extracted_fieldevol.setName(f"{self.name}_{group_name}")
        for _, field_double in self.fields_by_timestep.items():
            subfield: MEDField = field_double.extract_group(group_name)
            extracted_fieldevol.appendFieldProfile(
                subfield.field_double,
                self.mesh.mesh_file,
                0,
                group.to_profile().node_ids_array,
            )
        return MEDFieldEvol(self.mesh, extracted_fieldevol, group.to_profile())

    def add_field(self, med_field: MEDField):
        print(self.file_field_multits.getIterations())
        print(type(med_field.field_double))
        if med_field.timestamp in self.fields_by_timestep:
            raise ValueError(
                f"Timestamp {med_field.timestamp} already present in field_evol"
            )
        if med_field.profile is None:
            field_1ts: mc.MEDFileField1TS = mc.MEDFileField1TS.New()
            field_1ts.setFieldNoProfileSBT(med_field.field_double)
            self.file_field_multits.pushBackTimeStep(field_1ts)
        else:
            self.file_field_multits.appendFieldProfile(
                med_field.field_double,
                self.mesh.mesh_file,
                0,
                med_field.profile.node_ids_array,
            )
        print(self.file_field_multits.getIterations())

    @property
    def fields_by_timestep(self) -> Dict[TimeStamp, MEDField]:
        return {
            TimeStamp(*field_double.getTime()): self.__build_field(field_double)
            for field_double in self.file_field_multits
        }
