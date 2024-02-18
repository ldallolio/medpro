import medpro
import tempfile, os

def test_read_write():

    fp = medpro.MEDFilePost("./tests/examples/box_with_depl.rmed")
    with tempfile.TemporaryDirectory() as tempdir:
        tmpfilepath = os.path.join(tempdir, "output.rmed")
        fp.write(tmpfilepath)

def test_new_write():

    with tempfile.TemporaryDirectory() as tempdir:
        tmpfilepath = os.path.join(tempdir, "new.rmed")
        fp = medpro.MEDFilePost()
        fp.write(tmpfilepath)

def test_extract_group():

    fp = medpro.MEDFilePost("./tests/examples/box_with_depl.rmed")
    assert "reslin__DEPL" in fp.fieldevols_by_name

    depl_evol = fp.fieldevols_by_name["reslin__DEPL"]
    depl_g1 = depl_evol.extract_group("G1")
    fpnew = medpro.MEDFilePost()
    fpnew.add_mesh(fp.meshes_by_name["mesh"])
    fpnew.add_fieldevol(depl_g1)    

    with tempfile.TemporaryDirectory() as tempdir:
        tmpfilepath = os.path.join(tempdir, "output.rmed")
        fpnew.write(tmpfilepath)