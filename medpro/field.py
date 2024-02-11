from dataclasses import dataclass

import medcoupling as mc


@dataclass(frozen=True)
class TimeStamp:
    iteration: int
    order: int
    time: float


class MEDField:
    def __init__(self, mesh_file, field):
        self.mesh = mesh_file
        self.field = field

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

    def extract_group(self, group_name):
        group = self.mesh.get_group_by_name(group_name)
        subfield = self.field.buildSubPart(group.cell_ids_array)
        return MEDField(self.mesh, subfield)


class MEDFieldEvol:
    def __init__(self, mesh, file_field):
        self.mesh = mesh
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
        return [
            TimeStamp(iteration, order, time)
            for iteration, order, time in self.file_field.getTimeSteps()
        ]

    def __build_field(self, field_1ts):
        assert len(self.file_field.getTypesOfFieldAvailable()) == 1
        assert len(self.file_field.getTypesOfFieldAvailable()[0]) == 1
        field_type = self.file_field.getTypesOfFieldAvailable()[0][
            0
        ]  # TODO understand this and make it more general
        field_vals, depl_prf = field_1ts.getFieldWithProfile(
            field_type, 0, self.mesh.mesh_file
        )

        whole_mesh = self.mesh.mesh_file.getMeshAtLevel(0)
        double_field = mc.MEDCouplingFieldDouble.New(field_type, mc.ONE_TIME)
        double_field.setName(field_1ts.getName())
        double_field.setMesh(whole_mesh)
        double_field.setArray(field_vals)

        iteration, order, time = field_1ts.getTime()
        double_field.setTime(time, iteration, order)
        return MEDField(self.mesh, double_field)

    def get_field_at_timestep(self, iteration, order):
        return self.__build_field(self.file_field.getTimeStep(iteration, order))

    def extract_group(self, group_name):
        group = self.mesh.get_group_by_name(group_name)
        extracted_fieldevol = mc.MEDFileFieldMultiTS.New()
        extracted_fieldevol.setName(f"{self.name}_{group_name}")
        for _, field in self.fields_by_timestep.items():
            subfield = field.extract_group(group_name)
            extracted_fieldevol.appendFieldProfile(
                subfield.field, self.mesh.mesh_file, 0, group.to_profile().node_ids_array
            )
        return MEDFieldEvol(self.mesh, extracted_fieldevol)

    @property
    def fields_by_timestep(self):
        return {
            TimeStamp(*field.getTime()): self.__build_field(field)
            for field in self.file_field
        }
