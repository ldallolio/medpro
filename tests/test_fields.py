import medpro
import numpy as np


def test_field_evol():
    fp = medpro.MEDFilePost("./tests/examples/box_with_depl.rmed")

    assert len(fp.fieldevols_by_name) == 2
    assert "reslin__DEPL" in fp.fieldevols_by_name

    depl_evol = fp.fieldevols_by_name["reslin__DEPL"]
    assert depl_evol.name == "reslin__DEPL"
    assert len(depl_evol.components) == 3
    assert "DX" in depl_evol.components
    assert "DY" in depl_evol.components
    assert "DZ" in depl_evol.components
    assert len(depl_evol.profile_by_name) == 0
    assert len(depl_evol.timesteps) == 1
    assert len(depl_evol.fields_by_timestep) == 1
    assert depl_evol.timesteps[0].iteration == 1
    assert depl_evol.timesteps[0].order == 1
    assert depl_evol.timesteps[0].time == 0.0


def test_field():
    fp = medpro.MEDFilePost("./tests/examples/box_with_depl.rmed")
    assert "reslin__DEPL" in fp.fieldevols_by_name

    depl_evol = fp.fieldevols_by_name["reslin__DEPL"]

    depl = depl_evol.get_field_at_timestep(1, 1)
    assert depl.name == "reslin__DEPL"
    assert depl.on_nodes
    assert depl.timestamp.iteration == 1
    assert depl.timestamp.order == 1
    assert depl.timestamp.time == 0.0
    assert len(depl.components) == 3
    assert "DX" in depl.components
    assert "DY" in depl.components
    assert "DZ" in depl.components
    assert depl.to_numpy().size == depl.mesh.num_nodes * len(depl.components)
    depl.set_timestamp(2, 2, 0.0)
    depl_evol.add_field(depl)
    assert len(depl_evol.fields_by_timestep) == 2
    assert np.array_equal(depl.to_numpy() + depl.to_numpy(), (depl + depl).to_numpy())
    assert np.array_equal(depl.to_numpy() * 3.15, (depl * 3.15).to_numpy())


def test_extract_group():
    fp = medpro.MEDFilePost("./tests/examples/box_with_depl.rmed")
    assert "reslin__DEPL" in fp.fieldevols_by_name

    depl_evol = fp.fieldevols_by_name["reslin__DEPL"]
    depl_g1 = depl_evol.extract_group("G1")
    depl = depl_g1.get_field_at_timestep(1, 1)
    assert depl.name == "reslin__DEPL"
    assert depl.on_nodes
    assert depl.timestamp.iteration == 1
    assert depl.timestamp.order == 1
    assert depl.timestamp.time == 0.0
    assert len(depl.components) == 3
    assert "DX" in depl.components
    assert "DY" in depl.components
    assert "DZ" in depl.components
    assert depl.to_numpy().size == 15 * len(depl.components)
