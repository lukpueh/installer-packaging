import sys
from toto import util
from toto.models.layout import Step, Inspection, Layout

from datetime import datetime
from dateutil.relativedelta import relativedelta

# generate_and_write_rsa_keypair("albert")
# generate_and_write_rsa_keypair("lukas")

root_key = util.import_rsa_key_from_file("albert")
func_key = util.import_rsa_key_from_file("lukas")
func_pubkey = util.import_rsa_key_from_file("lukas.pub")
func_id = func_key["keyid"]

def create_common_steps():

  steps = [
    Step(
      name="clone-packager",
      expected_command=\
          "git clone https://github.com/SeattleTestbed/installer-packaging",
      product_matchrules=[
        "CREATE installer-packaging/*".split(),
      ],
      pubkeys=[func_id]
    ),
    Step(
      name="clone-dependencies",
      expected_command=\
          "python initialize.py",
      material_matchrules=[
          # "MATCH PRODUCT ../* from clone-packager".split(),
          "MATCH PRODUCT ../../installer-packaging/* AS installer-packaging FROM clone-packager".split(),
      ],
      product_matchrules=[
          # "CREATE ../DEPENDENCIES/*".split(),
          "CREATE installer-packaging/*".split(),
      ],
      pubkeys=[func_id]
    ),
    Step(
      name="build-runnable",
      expected_command=\
          "python build.py",
      material_matchrules=[
          # "MATCH PRODUCT ../* FROM clone-dependencies".split(),
          "MATCH PRODUCT installer-packaging/* FROM clone-dependencies".split(),
      ],
      product_matchrules=[
          # "CREATE ../RUNNABLE/*".split(),
          "CREATE installer-packaging/*".split(),
      ],
      pubkeys=[func_id]
    ),
    Step(
      name="edit-parameters",
      expected_command=\
          "vi",
      material_matchrules=[
          # "MATCH PRODUCT ../RUNNABLE/* FROM build-runnable".split(),
          "MATCH PRODUCT installer-packaging/RUNNABLE/* FROM build-runnable"
          .split(),
      ],
      product_matchrules=[
          # "CREATE ../RUNNABLE/*".split(),
          "CREATE installer-packaging/*".split(),
      ],
      pubkeys=[func_id]
    ),

    Step(
      name="build-base-installers",
      expected_command=\
          "python rebuild_base_installers.py",
      material_matchrules=[
          "MATCH PRODUCT installer-packaging/* FROM edit-parameters"
          .split(),
      ],
      product_matchrules=[
          "CREATE custominstallerbuilder/html/static/installers/base/*"
          .split(),
      ],
      pubkeys=[func_id]
    )]

  # TODO
  # the build-installer step is part of the Django app module build_manager
  # it would need to be modify to call into in-toto library
  # the "only" addition

  # step_build_installer = Step(
  #     name="build-installer",
  #     expected_command=\
  #         None
  #     material_matchrules=[
  #         "MATCH ../../custominstallerbuilder/html/static/installers/base/*"
  #         .split(),
  #     ],
  #     product_matchrules=[
  #         .split(),
  #     ],
  #     pubkeys=[func_id]
  #   )

  return steps

def create_layout(steps, inspects, name):
  layout = Layout(
      steps=steps,
      inspect=inspects,
      keys={
        func_id: func_pubkey
      },
      expires=((datetime.today() + relativedelta(months=1)).isoformat() + 'Z')
    )

  layout.sign(root_key)
  layout.dump(name)

def linux():
  common_steps = create_common_steps()
  # FIXME
  # build-base-installers is a complex compound step that
  # fetches files from different locations and places them directly into a tar
  #
  # Add this dummy step allow an untar Inspection to match all files from the
  # untared base installer using a wildcard
  step_untar_base_installer = Step(
      name="dummy-untar-linux-base-installer",
      material_matchrules=[
        ["MATCH", "PRODUCT",
        "custominstallerbuilder/html/static/installers/base/seattle_linux.tgz",
        "FROM",
        "build-base-installers"]
      ],
      product_matchrules=[
        "CREATE custominstallerbuilder/html/static/installers/base/seattle/*"
        .split()
      ],
      expected_command="tar xf",
      pubkeys=[func_id]

    )

  inspection_untar_linux = Inspection(
      name="untar-linux-installer",
      product_matchrules=[
        "MATCH PRODUCT * FROM dummy-untar-linux-base-installer".split(),
        "CREATE seattle/seattle_repy/vesselinfo".split()
      ],
      run="tar xf seattle_linux.tgz"
    )
  steps = common_steps + [step_untar_base_installer]
  inspects = [inspection_untar_linux]
  create_layout(steps, inspects, "linux_root.layout")


def android():
  pass

def mac():
  pass

def win():
  pass



def usage():
  print "Usage:", sys.argv[0], "(linux | mac | android | win)"

def main():

  if len(sys.argv) < 2:
    usage()
    sys.exit(1)

  if sys.argv[1] == "linux":
    linux()
  elif sys.argv[1] == "mac":
    mac()
  elif sys.argv[1] == "android":
    android()
  elif sys.argv[1] == "win":
    win()
  else:
    usage()
    sys.exit(1)

if __name__ == '__main__':
  main()