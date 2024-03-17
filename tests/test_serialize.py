import pathlib
import sys

import medpro
import tempfile, os

def test_read_write(ex_dir):

    fp = medpro.MEDFilePost(ex_dir / "box_with_depl.rmed")
    with tempfile.TemporaryDirectory() as tempdir:
        tmpfilepath = os.path.join(tempdir, "output.rmed")
        fp.write(tmpfilepath)

def test_new_write():

    with tempfile.TemporaryDirectory() as tempdir:
        tmpfilepath = os.path.join(tempdir, "new.rmed")
        fp = medpro.MEDFilePost()
        fp.write(tmpfilepath)

def test_extract_group(ex_dir):

    fp = medpro.MEDFilePost(ex_dir / "box_with_depl.rmed")
    assert "reslin__DEPL" in fp.fieldevols_by_name

    depl_evol = fp.fieldevols_by_name["reslin__DEPL"]
    depl_g1 = depl_evol.extract_group("G1")
    fpnew = medpro.MEDFilePost()
    fpnew.add_mesh(fp.meshes_by_name["mesh"])
    fpnew.add_fieldevol(depl_g1)    

    with tempfile.TemporaryDirectory() as tempdir:
        tmpfilepath = os.path.join(tempdir, "output.rmed")
        fpnew.write(tmpfilepath)

def test_add_field_write(ex_dir):

    fp = medpro.MEDFilePost(ex_dir / "box_with_depl.rmed")
    assert "reslin__DEPL" in fp.fieldevols_by_name

    depl_evol = fp.fieldevols_by_name["reslin__DEPL"]
    depl = depl_evol.get_field_at_timestep(1, 1)
    depl2 = depl * 2
    depl2.set_timestamp(2, 2, depl.timestamp.time)
    depl_evol.add_field(depl2)

    with tempfile.TemporaryDirectory() as tempdir:
        tmpfilepath = os.path.join(tempdir, "output.rmed")
        fp.write(tmpfilepath)

def test_add_field_new_write(ex_dir):
    fp = medpro.MEDFilePost(ex_dir / "box_with_depl.rmed")

    depl_evol = fp.fieldevols_by_name["reslin__DEPL"]

    fpnew = medpro.MEDFilePost()
    mesh = next(iter(fp.meshes_by_name.values()))
    fpnew.add_mesh(mesh)

    fields_data = fp.file_data.getFields()
    print(f"{fields_data.getPfls()=}")
    print(f"{fields_data.getPflsReallyUsed()=}")
    print(f"{fields_data.getPflsReallyUsedMulti()=}")

    depl = depl_evol.get_field_at_timestep(1, 1)
    depl2 = depl * 2
    depl2.set_timestamp(2, 2, depl.timestamp.time)
    depl_evol.add_field(depl2)
    fpnew.add_fieldevol(depl_evol)

    print(f"{fields_data.getPfls()=}")
    print(f"{fields_data.getPflsReallyUsed()=}")
    print(f"{fields_data.getPflsReallyUsedMulti()=}")    

    with tempfile.TemporaryDirectory() as tempdir:
        tmpfilepath = os.path.join(tempdir, "new.rmed")
        
        fpnew.write(tmpfilepath)

def test_beam_floor(ex_dir):
    fp = medpro.MEDFilePost(ex_dir / "structure_beams_floor.rmed")

    depl_evol = fp.fieldevols_by_name["resuelemDEPL"]

    fpnew = medpro.MEDFilePost()
    mesh = next(iter(fp.meshes_by_name.values()))
    fpnew.add_mesh(mesh)

    depl1 = depl_evol.get_field_at_timestep(5, 5)
    depl2 = depl_evol.get_field_at_timestep(9, 9)
    deplsum = depl1+depl2
    deplsum.name = depl1.name
    deplsum.set_timestamp(12, 12, depl1.timestamp.time)    
    depl_evol.add_field(deplsum)
    fpnew.add_fieldevol(depl_evol)

    with tempfile.TemporaryDirectory() as tempdir:
        tmpfilepath = os.path.join(tempdir, "new.rmed")
        
        fpnew.write(tmpfilepath)