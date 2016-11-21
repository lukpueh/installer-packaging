#!/bin/bash


# echo "RUN clone-packager in $PWD"
# toto-run.py --step-name clone-packager --key lukas \
#   --products installer-packaging/ \
#   --record-byproducts \
#   -- git clone https://github.com/SeattleTestbed/installer-packaging

cd installer-packaging/scripts

# echo "RUN clone-dependencies in $PWD"
# toto-run.py --step-name clone-dependencies --key ../../lukas \
#   --materials ../../installer-packaging/ \
#   --products ../../installer-packaging/ \
#   --record-byproducts \
#   -- python initialize.py


echo "RUN clone-dependencies in $PWD"
toto-run.py --step-name clone-dependencies --key ../../lukas \
  --products ../../installer-packaging/DEPENDENCIES \
  --record-byproducts \
  -- python initialize.py

echo "RUN build-runnable in $PWD"
toto-run.py --step-name build-runnable --key ../../lukas \
  --materials ../../installer-packaging/DEPENDENCIES \
  --products ../../installer-packaging/RUNNABLE \
  --record-byproducts \
  -- python build.py

cd ../RUNNABLE

echo "RUN pre-build-file-edit in $PWD"
toto-run.py --step-name pre-build-file-edit --key ../../lukas \
  --materials ../../installer-packaging/RUNNABLE \
  --products ../../installer-packaging/RUNNABLE \
  -- ./pre-build-file-edit.sh

# echo "RUN edit-parameters in $PWD"
# toto-run.py --step-name edit-parameters --key ../../lukas \
#   --materials ../../installer-packaging/RUNNABLE \
#   --products ../../installer-packaging/RUNNABLE \
#   -- vi rebuild_base_installers.py seattle_repy/nmmain.py seattle_repy/softwareupdater.py
  # change version in nmmain.py to 1.0

echo "RUN build-base-installers in $PWD"
toto-run.py --step-name build-base-installers --key ../../lukas \
  --materials ../../installer-packaging/RUNNABLE \
  --products ../../custominstallerbuilder/html/static/installers/base/ \
  --record-byproducts \
  -- python rebuild_base_installers.py 1.0

cd ../..
echo "RUN dummy-untar-linux-base-installer in $PWD"
toto-run.py --step-name dummy-untar-linux-base-installer --key lukas \
  --materials custominstallerbuilder/html/static/installers/base/seattle_linux.tgz \
  --products custominstallerbuilder/html/static/installers/base/seattle/ \
  --record-byproducts \
  -- tar xf custominstallerbuilder/html/static/installers/base/seattle_linux.tgz \
    -C custominstallerbuilder/html/static/installers/base/


# toto-verify.py --layout linux_root.layout --layout-keys albert.pub

