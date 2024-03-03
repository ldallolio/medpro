import medpro
import numpy as np


def test_field_evol():
    fp = medpro.MEDFilePost("./tests/examples/box_with_deplevol.rmed")

    assert len(fp.fieldevols_by_name) == 2
    assert "reslin__DEPL" in fp.fieldevols_by_name

    depl_evol = fp.fieldevols_by_name["reslin__DEPL"]
    assert depl_evol.name == "reslin__DEPL"
    assert len(depl_evol.components) == 3
    assert "DX" in depl_evol.components
    assert "DY" in depl_evol.components
    assert "DZ" in depl_evol.components
    assert len(depl_evol.profile_by_name) == 0
    assert len(depl_evol.timesteps) == 3
    assert len(depl_evol.field_by_timestep) == 3
    assert depl_evol.timesteps[0].iteration == 1
    assert depl_evol.timesteps[0].order == 1
    assert depl_evol.timesteps[0].time == 999.999

    # depl_evol.name = "reslin2__DEPL"
    # assert depl_evol.name == "reslin2__DEPL"
    # assert "reslin2__DEPL" in fp.fieldevols_by_name
    # assert "reslin__DEPL" not in fp.fieldevols_by_name    


def test_field():
    fp = medpro.MEDFilePost("./tests/examples/box_with_deplevol.rmed")
    assert "reslin__DEPL" in fp.fieldevols_by_name

    depl_evol = fp.fieldevols_by_name["reslin__DEPL"]

    depl = depl_evol.get_field_at_timestep(1, 1)
    assert depl.name == "reslin__DEPL"
    assert depl.on_nodes
    assert not depl.on_cells
    assert not depl.on_gauss_points
    assert not depl.on_nodes_per_element
    assert depl.timestamp.iteration == 1
    assert depl.timestamp.order == 1
    assert depl.timestamp.time == 999.999
    assert len(depl.components) == 3
    assert "DX" in depl.components
    assert "DY" in depl.components
    assert "DZ" in depl.components
    assert depl.to_numpy().size == depl.mesh.num_nodes * len(depl.components)
    assert depl.to_numpy_structured().size == depl.mesh.num_nodes
    depl.set_timestamp(4, 4, 999.999)
    depl_evol.add_field(depl)
    assert len(depl_evol.field_by_timestep) == 4

    # depl.name = "reslin2__DEPL"
    # assert depl.name == "reslin2__DEPL"
    # depl2 = depl_evol.get_field_at_timestep(1, 1)
    # assert depl2.name == "reslin2__DEPL" 

def test_field_add():
    fp = medpro.MEDFilePost("./tests/examples/box_with_deplevol.rmed")
    assert "reslin__DEPL" in fp.fieldevols_by_name

    depl_evol = fp.fieldevols_by_name["reslin__DEPL"]

    depl = depl_evol.get_field_at_timestep(1, 1)
    depl2 = 3.15 + depl
    print(f"{depl2=}")

    assert np.array_equal(depl.to_numpy() + depl.to_numpy(), (depl + depl).to_numpy())
    assert np.array_equal(depl2.to_numpy(), (depl + 3.15).to_numpy())
    assert np.array_equal(depl.to_numpy() - 3.15, (depl - 3.15).to_numpy())
    assert np.array_equal(3.15 - depl.to_numpy(), (3.15 - depl).to_numpy())
    assert np.array_equal(depl.to_numpy() * 3.15, (depl * 3.15).to_numpy())
    assert np.array_equal(3.15 * depl.to_numpy(), (depl * 3.15).to_numpy())

    depl += 3.15
    assert np.array_equal(depl2.to_numpy(), depl.to_numpy())
    depl -= 3.15
    assert np.array_equal(depl2.to_numpy(), (depl + 3.15).to_numpy())

def test_field_add_timesteps():
    fp = medpro.MEDFilePost("./tests/examples/box_with_deplevol.rmed")
    assert "reslin__DEPL" in fp.fieldevols_by_name

    depl_evol = fp.fieldevols_by_name["reslin__DEPL"]

    depl = depl_evol.get_field_at_timestep(1, 1)
    depl2 = depl_evol.get_field_at_timestep(2, 2)

    assert np.array_equal(depl.to_numpy() + depl2.to_numpy(), (depl + depl2).to_numpy())

def test_extract_group():
    fp = medpro.MEDFilePost("./tests/examples/box_with_deplevol.rmed")
    assert "reslin__DEPL" in fp.fieldevols_by_name

    depl_evol = fp.fieldevols_by_name["reslin__DEPL"]
    depl_g1 = depl_evol.extract_group("G1")
    depl = depl_g1.get_field_at_timestep(1, 1)
    assert depl.name == "reslin__DEPL"
    assert depl.on_nodes
    assert depl.timestamp.iteration == 1
    assert depl.timestamp.order == 1
    assert depl.timestamp.time == 999.999
    assert len(depl.components) == 3
    assert "DX" in depl.components
    assert "DY" in depl.components
    assert "DZ" in depl.components
    assert depl.to_numpy().size == 15 * len(depl.components)
