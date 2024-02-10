===============================
medpro
===============================


.. image:: https://img.shields.io/travis/ldallolio/medpro.svg
        :target: https://travis-ci.org/ldallolio/medpro
.. image:: https://circleci.com/gh/ldallolio/medpro.svg?style=svg
    :target: https://circleci.com/gh/ldallolio/medpro
.. image:: https://codecov.io/gh/ldallolio/medpro/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/ldallolio/medpro


Medcoupling based post processing tools

This project has been created to simplify the manipulation of `MED <https://docs.salome-platform.org/latest/dev/MEDCoupling/developer/med-file.html>`_ files.

Code examples::

   # Read a med file, extract mesh, field, group information
   fp = medpro.MEDFilePost("./tests/examples/box_with_depl.rmed")
   mesh = fp.meshes_by_name["mesh"]
   g1 = mesh.get_group_by_name("G1")
   depl_evol = fp.fieldevols_by_name["reslin__DEPL"]

   # Extract a subpart of a field based on a group 
   depl_g1 = depl_evol.extract_group("G1")

   # Create a new MED file, write it back
   fpnew = medpro.MEDFilePost()
   fpnew.add_fieldevol(depl_g1)
   fpnew.write("/tmp/output.rmed")

