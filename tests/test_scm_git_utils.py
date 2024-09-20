from contextlib import contextmanager

import pytest

from testbrain.contrib.scm.git import utils as git_utils
from testbrain.contrib.scm.git import patterns as git_patterns


def test_parse_commits():
    commit_raw = (
        "COMMIT:\t5355a13f5ba44d23de9a3090ad976d63d1a60e3e\n"
        "TREE:\ta2bd09a6cc8a36da7fd43a3b8445967584873e5e\n"
        "DATE:\t2023-09-29T16:13:45+03:00\n"
        "AUTHOR:\tArtem Demidenko\tar.demidenko@gmail.com\t2023-09-29T16:13:45+03:00\n"
        "COMMITTER:\tArtem Demidenko\tar.demidenko@gmail.com"
        "\t2023-09-29T16:13:45+03:00\n"
        "MESSAGE:\tMerge branch 'dev'\n"
        "PARENTS:\t27d9aaff69ac8db9d19918c4d5efb6b3ed2c3210 "
        "0cd26c4deaebd98ff26b8cf20bda15553ef5bdcd\n"
        "\n\n"
        "COMMIT:\t39c54991d3cd7f4bae68d6b58549e7e2ab084a23\n"
        "TREE:\t5c86012497523e000b3ddfd9a95967da58d77fe9\n"
        "DATE:\t2023-10-02T13:23:02+03:00\n"
        "AUTHOR:\tArtem Demidenko\tar.demidenko@gmail.com\t2023-10-02T13:23:02+03:00\n"
        "COMMITTER:\tArtem Demidenko\tar.demidenko@gmail.com"
        "\t2023-10-02T13:23:02+03:00\n"
        "MESSAGE:\tRenamed files\n"
        "PARENTS:\t5355a13f5ba44d23de9a3090ad976d63d1a60e3e\n\n"
        "1\t1\tCONTRIB.txt\n"
        "1\t0\tREADME.md\n"
        "0\t1\tREADME.txt"
        "\n\n"
        "diff --git a/CONTRIB.txt b/CONTRIB.txt\n"
        "index 01ea8a03269d7d23931cd2a7aa8940b14f850257.."
        "7cb38a976dd950aef3eee5e8a63c334100d7044b 100644\n"
        "--- a/CONTRIB.txt\n+++ b/CONTRIB.txt\n"
        "@@ -1 +1 @@\n-Other\n+-- empty --\n\\ No newline at end of file\n"
        "diff --git a/README.md b/README.md\n"
        "new file mode 100644\n"
        "index 0000000000000000000000000000000000000000.."
        "52da238091fabcd84e921bb6029d9addf9afd02f\n"
        "--- /dev/null\n+++ b/README.md\n"
        "@@ -0,0 +1 @@\n+# README\n\\ No newline at end of file\n"
        "diff --git a/README.txt b/README.txt\n"
        "deleted file mode 100644\n"
        "index 8038dd2b0751f5c895754871bdc6daa400008c08.."
        "0000000000000000000000000000000000000000\n"
        "--- a/README.txt\n+++ /dev/null\n@@ -1 +0,0 @@\n-QA works\n"
        "\\ No newline at end of file\n"
        "\n\n"
        "COMMIT:\tceff1b9d2d403e83b9c7c39e5baa47eff61a3524\n"
        "TREE:\tb6f23611cb888a619940c71582de2dad6e04cd42\n"
        "DATE:\t2023-10-02T13:44:07+03:00\n"
        "AUTHOR:\tArtem Demidenko\tar.demidenko@gmail.com\t2023-10-02T13:44:07+03:00\n"
        "COMMITTER:\tArtem Demidenko\tar.demidenko@gmail.com"
        "\t2023-10-02T13:44:07+03:00\n"
        "MESSAGE:\tCONTRIB rename\nPARENTS:\t"
        "39c54991d3cd7f4bae68d6b58549e7e2ab084a23\n\n"
        "0\t0\tCONTRIB.txt => CONTRIB.md"
        "\n\n"
        "diff --git a/CONTRIB.txt b/CONTRIB.md\n"
        "similarity index 100%\nrename from CONTRIB.txt\nrename to CONTRIB.md"
        "\n\n\n"
        "COMMIT:\t2c5ebc4c21b8db4917c9a30173e3f5307f8552f9\n"
        "TREE:\t60fc93ce6ab91eb56d3f3f06a3abb77b1e5b3e22\n"
        "DATE:\t2023-10-02T20:01:48+03:00\n"
        "AUTHOR:\tArtem Demidenko\tar.demidenko@gmail.com\t2023-10-02T20:01:48+03:00\n"
        "COMMITTER:\tArtem Demidenko\tar.demidenko@gmail.com"
        "\t2023-10-02T20:01:48+03:00\n"
        "MESSAGE:\tChanges\nPARENTS:\tceff1b9d2d403e83b9c7c39e5baa47eff61a3524"
        "\n\n"
        "2\t1\tCONTRIB.md\n"
        "2\t1\tREADME.md"
        "\n\n"
        "diff --git a/CONTRIB.md b/CONTRIB.md\n"
        "index 7cb38a976dd950aef3eee5e8a63c334100d7044b.."
        "7b2014660cadcd1abd84890b72177c7a35402b11 100644\n"
        "--- a/CONTRIB.md\n+++ b/CONTRIB.md\n"
        "@@ -1 +1,2 @@\n--- empty --\n\\ No newline at end of file\n"
        "+-- empty --\n+Another one\n\\ No newline at end of file\n"
        "diff --git a/README.md b/README.md\n"
        "index 52da238091fabcd84e921bb6029d9addf9afd02f.."
        "78f497a48b0b909b166245a15c8d8e8ccacc9914 100644\n"
        "--- a/README.md\n+++ b/README.md\n"
        "@@ -1 +1,2 @@\n-# README\n\\ No newline at end of file\n"
        "+# README\n+## New headline\n\\ No newline at end of file\n"
        "\n\n"
    )

    result = git_utils.parse_commits_from_text(text=commit_raw)

    assert len(result) == 4


def test_parse_single_commit():
    commit1_raw = (
        "COMMIT:\t5355a13f5ba44d23de9a3090ad976d63d1a60e3e\n"
        "TREE:\ta2bd09a6cc8a36da7fd43a3b8445967584873e5e\n"
        "DATE:\t2023-09-29T16:13:45+03:00\n"
        "AUTHOR:\tArtem Demidenko\tar.demidenko@gmail.com\t2023-09-29T16:13:45+03:00\n"
        "COMMITTER:\tArtem Demidenko\tar.demidenko@gmail.com"
        "\t2023-09-29T16:13:45+03:00\n"
        "MESSAGE:\tMerge branch 'dev'\n"
        "PARENTS:\t27d9aaff69ac8db9d19918c4d5efb6b3ed2c3210 "
        "0cd26c4deaebd98ff26b8cf20bda15553ef5bdcd\n"
        "\n\n"
    )
    commit2_raw = (
        "COMMIT:\t39c54991d3cd7f4bae68d6b58549e7e2ab084a23\n"
        "TREE:\t5c86012497523e000b3ddfd9a95967da58d77fe9\n"
        "DATE:\t2023-10-02T13:23:02+03:00\n"
        "AUTHOR:\tArtem Demidenko\tar.demidenko@gmail.com\t2023-10-02T13:23:02+03:00\n"
        "COMMITTER:\tArtem Demidenko\tar.demidenko@gmail.com\t2023-10-02T13:23:02+03:00\n"
        "MESSAGE:\tRenamed files\n"
        "PARENTS:\t5355a13f5ba44d23de9a3090ad976d63d1a60e3e\n\n"
        "1\t1\tCONTRIB.txt\n"
        "1\t0\tREADME.md\n"
        "0\t1\tREADME.txt"
        "\n\n"
        "diff --git a/CONTRIB.txt b/CONTRIB.txt\n"
        "index 01ea8a03269d7d23931cd2a7aa8940b14f850257..7cb38a976dd950aef3eee5e8a63c334100d7044b 100644\n"
        "--- a/CONTRIB.txt\n+++ b/CONTRIB.txt\n"
        "@@ -1 +1 @@\n-Other\n+-- empty --\n\\ No newline at end of file\n\n"
        "diff --git a/README.md b/README.md\n"
        "new file mode 100644\n"
        "index 0000000000000000000000000000000000000000..52da238091fabcd84e921bb6029d9addf9afd02f\n"
        "--- /dev/null\n+++ b/README.md\n"
        "@@ -0,0 +1 @@\n+# README\n\\ No newline at end of file\n\n"
        "diff --git a/README.txt b/README.txt\n"
        "deleted file mode 100644\n"
        "index 8038dd2b0751f5c895754871bdc6daa400008c08..0000000000000000000000000000000000000000\n"
        "--- a/README.txt\n+++ /dev/null\n@@ -1 +0,0 @@\n-QA works\n\\ No newline at end of file\n"
        "\n"
    )

    for commit1_match in git_patterns.RE_COMMIT_LIST.finditer(commit1_raw):
        commit1 = git_utils.parse_single_commit(commit1_match)
        assert commit1 is not None
        assert commit1["sha"] == "5355a13f5ba44d23de9a3090ad976d63d1a60e3e"
        assert commit1["tree"] == "a2bd09a6cc8a36da7fd43a3b8445967584873e5e"
        assert commit1["date"] == "2023-09-29T16:13:45+03:00"
        assert commit1["author"] == {
            "name": "Artem Demidenko",
            "email": "ar.demidenko@gmail.com",
            "date": "2023-09-29T16:13:45+03:00",
        }
        assert commit1["parents"] == [
            {"sha": "27d9aaff69ac8db9d19918c4d5efb6b3ed2c3210"},
            {"sha": "0cd26c4deaebd98ff26b8cf20bda15553ef5bdcd"},
        ]

    for commit2_match in git_patterns.RE_COMMIT_LIST.finditer(commit2_raw):
        commit2 = git_utils.parse_single_commit(commit2_match)
        assert commit2 is not None
        assert commit2["sha"] == "39c54991d3cd7f4bae68d6b58549e7e2ab084a23"
        assert commit2["tree"] == "5c86012497523e000b3ddfd9a95967da58d77fe9"
        assert commit2["date"] == "2023-10-02T13:23:02+03:00"
        assert commit2["author"] == {
            "name": "Artem Demidenko",
            "email": "ar.demidenko@gmail.com",
            "date": "2023-10-02T13:23:02+03:00",
        }
        assert commit2["parents"] == [
            {"sha": "5355a13f5ba44d23de9a3090ad976d63d1a60e3e"}
        ]
    #     assert commit2["files"] == [
    #         {
    #             "filename": "CONTRIB.txt",
    #             "sha": "7cb38a976dd950aef3eee5e8a63c334100d7044b",
    #             "additions": 1,
    #             "insertions": 1,
    #             "deletions": 1,
    #             "changes": 2,
    #             "lines": 2,
    #             "status": "modified",
    #             "previous_filename": "",
    #             "patch": (
    #                 "@@ -1 +1 @@\n-Other\n+-- empty --\n\\ No newline at end of file\n"
    #             ),
    #             "blame": "",
    #         },
    #         {
    #             "filename": "README.md",
    #             "sha": "52da238091fabcd84e921bb6029d9addf9afd02f",
    #             "additions": 1,
    #             "insertions": 1,
    #             "deletions": 0,
    #             "changes": 1,
    #             "lines": 1,
    #             "status": "added",
    #             "previous_filename": "",
    #             "patch": "@@ -0,0 +1 @@\n+# README\n\\ No newline at end of file\n",
    #             "blame": "",
    #         },
    #         {
    #             "filename": "README.txt",
    #             "sha": "0000000000000000000000000000000000000000",
    #             "additions": 0,
    #             "insertions": 0,
    #             "deletions": 1,
    #             "changes": 1,
    #             "lines": 1,
    #             "status": "deleted",
    #             "previous_filename": "",
    #             "patch": "@@ -1 +0,0 @@\n-QA works\n\\ No newline at end of file\n",
    #             "blame": "",
    #         },
    #     ]


def test_parse_foreach_submodules_commits():
    submodules_commits = (
        "Entering 'deps/sub_test_repo'\n\n"
        "COMMIT:\t2167055f7bdc664f70111c47119ecf7dbdf3157f\n"
        "TREE:\t1c84b685f62a42c86881139912090c2e1e5ab645\n"
        "DATE:\t2024-09-15T10:03:23+03:00\n"
        "AUTHOR:\tArtem Demidenko\twhenessel@icloud.com\t2024-09-15T10:03:23+03:00\n"
        "COMMITTER:\tGitHub\tnoreply@github.com\t2024-09-15T10:03:23+03:00\n"
        "MESSAGE:\tInitial commit\nPARENTS:\t\n\n"
        ":000000 100644 0000000000000000000000000000000000000000 82f927558a3dff0ea8c20858856e70779fd02c93 A\t.gitignore\n"
        ":000000 100644 0000000000000000000000000000000000000000 261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64 A\tLICENSE\n"
        ":000000 100644 0000000000000000000000000000000000000000 3bf040133e335ced65d3b4d53a36608c7a6697fc A\tREADME.md\n"
        "162\t0\t.gitignore\n"
        "201\t0\tLICENSE\n"
        "1\t0\tREADME.md\n\n"
        "diff --git a/.gitignore b/.gitignore\n"
        "new file mode 100644\n"
        "index 0000000000000000000000000000000000000000..82f927558a3dff0ea8c20858856e70779fd02c93\n"
        '--- /dev/null\n+++ b/.gitignore\n@@ -0,0 +1,162 @@\n+# Byte-compiled / optimized / DLL files\n+__pycache__/\n+*.py[cod]\n+*$py.class\n+\n+# C extensions\n+*.so\n+\n+# Distribution / packaging\n+.Python\n+build/\n+develop-eggs/\n+dist/\n+downloads/\n+eggs/\n+.eggs/\n+lib/\n+lib64/\n+parts/\n+sdist/\n+var/\n+wheels/\n+share/python-wheels/\n+*.egg-info/\n+.installed.cfg\n+*.egg\n+MANIFEST\n+\n+# PyInstaller\n+#  Usually these files are written by a python script from a template\n+#  before PyInstaller builds the exe, so as to inject date/other infos into it.\n+*.manifest\n+*.spec\n+\n+# Installer logs\n+pip-log.txt\n+pip-delete-this-directory.txt\n+\n+# Unit test / coverage reports\n+htmlcov/\n+.tox/\n+.nox/\n+.coverage\n+.coverage.*\n+.cache\n+nosetests.xml\n+coverage.xml\n+*.cover\n+*.py,cover\n+.hypothesis/\n+.pytest_cache/\n+cover/\n+\n+# Translations\n+*.mo\n+*.pot\n+\n+# Django stuff:\n+*.log\n+local_settings.py\n+db.sqlite3\n+db.sqlite3-journal\n+\n+# Flask stuff:\n+instance/\n+.webassets-cache\n+\n+# Scrapy stuff:\n+.scrapy\n+\n+# Sphinx documentation\n+docs/_build/\n+\n+# PyBuilder\n+.pybuilder/\n+target/\n+\n+# Jupyter Notebook\n+.ipynb_checkpoints\n+\n+# IPython\n+profile_default/\n+ipython_config.py\n+\n+# pyenv\n+#   For a library or package, you might want to ignore these files since the code is\n+#   intended to run in multiple environments; otherwise, check them in:\n+# .python-version\n+\n+# pipenv\n+#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.\n+#   However, in case of collaboration, if having platform-specific dependencies or dependencies\n+#   having no cross-platform support, pipenv may install dependencies that don\'t work, or not\n+#   install all needed dependencies.\n+#Pipfile.lock\n+\n+# poetry\n+#   Similar to Pipfile.lock, it is generally recommended to include poetry.lock in version control.\n+#   This is especially recommended for binary packages to ensure reproducibility, and is more\n+#   commonly ignored for libraries.\n+#   https://python-poetry.org/docs/basic-usage/#commit-your-poetrylock-file-to-version-control\n+#poetry.lock\n+\n+# pdm\n+#   Similar to Pipfile.lock, it is generally recommended to include pdm.lock in version control.\n+#pdm.lock\n+#   pdm stores project-wide configurations in .pdm.toml, but it is recommended to not include it\n+#   in version control.\n+#   https://pdm.fming.dev/latest/usage/project/#working-with-version-control\n+.pdm.toml\n+.pdm-python\n+.pdm-build/\n+\n+# PEP 582; used by e.g. github.com/David-OConnor/pyflow and github.com/pdm-project/pdm\n+__pypackages__/\n+\n+# Celery stuff\n+celerybeat-schedule\n+celerybeat.pid\n+\n+# SageMath parsed files\n+*.sage.py\n+\n+# Environments\n+.env\n+.venv\n+env/\n+venv/\n+ENV/\n+env.bak/\n+venv.bak/\n+\n+# Spyder project settings\n+.spyderproject\n+.spyproject\n+\n+# Rope project settings\n+.ropeproject\n+\n+# mkdocs documentation\n+/site\n+\n+# mypy\n+.mypy_cache/\n+.dmypy.json\n+dmypy.json\n+\n+# Pyre type checker\n+.pyre/\n+\n+# pytype static type analyzer\n+.pytype/\n+\n+# Cython debug symbols\n+cython_debug/\n+\n+# PyCharm\n+#  JetBrains specific template is maintained in a separate JetBrains.gitignore that can\n+#  be found at https://github.com/github/gitignore/blob/main/Global/JetBrains.gitignore\n+#  and can be added to the global gitignore or merged into this file.  For a more nuclear\n+#  option (not recommended) you can uncomment the following to ignore the entire idea folder.\n+#.idea/\ndiff --git a/LICENSE b/LICENSE\nnew file mode 100644\nindex 0000000000000000000000000000000000000000..261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64\n--- /dev/null\n+++ b/LICENSE\n@@ -0,0 +1,201 @@\n+                                 Apache License\n+                           Version 2.0, January 2004\n+                        http://www.apache.org/licenses/\n+\n+   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION\n+\n+   1. Definitions.\n+\n+      ")License" shall mean the terms and conditions for use, reproduction,\n+      and distribution as defined by Sections 1 through 9 of this document.\n+\n+      "Licensor" shall mean the copyright owner or entity authorized by\n+      the copyright owner that is granting the License.\n+\n+      "Legal Entity" shall mean the union of the acting entity and all\n+      other entities that control, are controlled by, or are under common\n+      control with that entity. For the purposes of this definition,\n+      "control" means (i) the power, direct or indirect, to cause the\n+      direction or management of such entity, whether by contract or\n+      otherwise, or (ii) ownership of fifty percent (50%) or more of the\n+      outstanding shares, or (iii) beneficial ownership of such entity.\n+\n+      "You" (or "Your") shall mean an individual or Legal Entity\n+      exercising permissions granted by this License.\n+\n+      "Source" form shall mean the preferred form for making modifications,\n+      including but not limited to software source code, documentation\n+      source, and configuration files.\n+\n+      "Object" form shall mean any form resulting from mechanical\n+      transformation or translation of a Source form, including but\n+      not limited to compiled object code, generated documentation,\n+      and conversions to other media types.\n+\n+      "Work" shall mean the work of authorship, whether in Source or\n+      Object form, made available under the License, as indicated by a\n+      copyright notice that is included in or attached to the work\n+      (an example is provided in the Appendix below).\n+\n+      "Derivative Works" shall mean any work, whether in Source or Object\n+      form, that is based on (or derived from) the Work and for which the\n+      editorial revisions, annotations, elaborations, or other modifications\n+      represent, as a whole, an original work of authorship. For the purposes\n+      of this License, Derivative Works shall not include works that remain\n+      separable from, or merely link (or bind by name) to the interfaces of,\n+      the Work and Derivative Works thereof.\n+\n+      "Contribution" shall mean any work of authorship, including\n+      the original version of the Work and any modifications or additions\n+      to that Work or Derivative Works thereof, that is intentionally\n+      submitted to Licensor for inclusion in the Work by the copyright owner\n+      or by an individual or Legal Entity authorized to submit on behalf of\n+      the copyright owner. For the purposes of this definition, "submitted"\n+      means any form of electronic, verbal, or written communication sent\n+      to the Licensor or its representatives, including but not limited to\n+      communication on electronic mailing lists, source code control systems,\n+      and issue tracking systems that are managed by, or on behalf of, the\n+      Licensor for the purpose of discussing and improving the Work, but\n+      excluding communication that is conspicuously marked or otherwise\n+      designated in writing by the copyright owner as "Not a Contribution."\n+\n+      "Contributor" shall mean Licensor and any individual or Legal Entity\n+      on behalf of whom a Contribution has been received by Licensor and\n+      subsequently incorporated within the Work.\n+\n+   2. Grant of Copyright License. Subject to the terms and conditions of\n+      this License, each Contributor hereby grants to You a perpetual,\n+      worldwide, non-exclusive, no-charge, royalty-free, irrevocable\n+      copyright license to reproduce, prepare Derivative Works of,\n+      publicly display, publicly perform, sublicense, and distribute the\n+      Work and such Derivative Works in Source or Object form.\n+\n+   3. Grant of Patent License. Subject to the terms and conditions of\n+      this License, each Contributor hereby grants to You a perpetual,\n+      worldwide, non-exclusive, no-charge, royalty-free, irrevocable\n+      (except as stated in this section) patent license to make, have made,\n+      use, offer to sell, sell, import, and otherwise transfer the Work,\n+      where such license applies only to those patent claims licensable\n+      by such Contributor that are necessarily infringed by their\n+      Contribution(s) alone or by combination of their Contribution(s)\n+      with the Work to which such Contribution(s) was submitted. If You\n+      institute patent litigation against any entity (including a\n+      cross-claim or counterclaim in a lawsuit) alleging that the Work\n+      or a Contribution incorporated within the Work constitutes direct\n+      or contributory patent infringement, then any patent licenses\n+      granted to You under this License for that Work shall terminate\n+      as of the date such litigation is filed.\n+\n+   4. Redistribution. You may reproduce and distribute copies of the\n+      Work or Derivative Works thereof in any medium, with or without\n+      modifications, and in Source or Object form, provided that You\n+      meet the following conditions:\n+\n+      (a) You must give any other recipients of the Work or\n+          Derivative Works a copy of this License; and\n+\n+      (b) You must cause any modified files to carry prominent notices\n+          stating that You changed the files; and\n+\n+      (c) You must retain, in the Source form of any Derivative Works\n+          that You distribute, all copyright, patent, trademark, and\n+          attribution notices from the Source form of the Work,\n+          excluding those notices that do not pertain to any part of\n+          the Derivative Works; and\n+\n+      (d) If the Work includes a "NOTICE" text file as part of its\n+          distribution, then any Derivative Works that You distribute must\n+          include a readable copy of the attribution notices contained\n+          within such NOTICE file, excluding those notices that do not\n+          pertain to any part of the Derivative Works, in at least one\n+          of the following places: within a NOTICE text file distributed\n+          as part of the Derivative Works; within the Source form or\n+          documentation, if provided along with the Derivative Works; or,\n+          within a display generated by the Derivative Works, if and\n+          wherever such third-party notices normally appear. The contents\n+          of the NOTICE file are for informational purposes only and\n+          do not modify the License. You may add Your own attribution\n+          notices within Derivative Works that You distribute, alongside\n+          or as an addendum to the NOTICE text from the Work, provided\n+          that such additional attribution notices cannot be construed\n+          as modifying the License.\n+\n+      You may add Your own copyright statement to Your modifications and\n+      may provide additional or different license terms and conditions\n+      for use, reproduction, or distribution of Your modifications, or\n+      for any such Derivative Works as a whole, provided Your use,\n+      reproduction, and distribution of the Work otherwise complies with\n+      the conditions stated in this License.\n+\n+   5. Submission of Contributions. Unless You explicitly state otherwise,\n+      any Contribution intentionally submitted for inclusion in the Work\n+      by You to the Licensor shall be under the terms and conditions of\n+      this License, without any additional terms or conditions.\n+      Notwithstanding the above, nothing herein shall supersede or modify\n+      the terms of any separate license agreement you may have executed\n+      with Licensor regarding such Contributions.\n+\n+   6. Trademarks. This License does not grant permission to use the trade\n+      names, trademarks, service marks, or product names of the Licensor,\n+      except as required for reasonable and customary use in describing the\n+      origin of the Work and reproducing the content of the NOTICE file.\n+\n+   7. Disclaimer of Warranty. Unless required by applicable law or\n+      agreed to in writing, Licensor provides the Work (and each\n+      Contributor provides its Contributions) on an "AS IS" BASIS,\n+      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or\n+      implied, including, without limitation, any warranties or conditions\n+      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A\n+      PARTICULAR PURPOSE. You are solely responsible for determining the\n+      appropriateness of using or redistributing the Work and assume any\n+      risks associated with Your exercise of permissions under this License.\n+\n+   8. Limitation of Liability. In no event and under no legal theory,\n+      whether in tort (including negligence), contract, or otherwise,\n+      unless required by applicable law (such as deliberate and grossly\n+      negligent acts) or agreed to in writing, shall any Contributor be\n+      liable to You for damages, including any direct, indirect, special,\n+      incidental, or consequential damages of any character arising as a\n+      result of this License or out of the use or inability to use the\n+      Work (including but not limited to damages for loss of goodwill,\n+      work stoppage, computer failure or malfunction, or any and all\n+      other commercial damages or losses), even if such Contributor\n+      has been advised of the possibility of such damages.\n+\n+   9. Accepting Warranty or Additional Liability. While redistributing\n+      the Work or Derivative Works thereof, You may choose to offer,\n+      and charge a fee for, acceptance of support, warranty, indemnity,\n+      or other liability obligations and/or rights consistent with this\n+      License. However, in accepting such obligations, You may act only\n+      on Your own behalf and on Your sole responsibility, not on behalf\n+      of any other Contributor, and only if You agree to indemnify,\n+      defend, and hold each Contributor harmless for any liability\n+      incurred by, or claims asserted against, such Contributor by reason\n+      of your accepting any such warranty or additional liability.\n+\n+   END OF TERMS AND CONDITIONS\n+\n+   APPENDIX: How to apply the Apache License to your work.\n+\n+      To apply the Apache License to your work, attach the following\n+      boilerplate notice, with the fields enclosed by brackets "[]"\n+      replaced with your own identifying information. (Don\'t include\n+      the brackets!)  The text should be enclosed in the appropriate\n+      comment syntax for the file format. We also recommend that a\n+      file or class name and description of purpose be included on the\n+      same "printed page" as the copyright notice for easier\n+      identification within third-party archives.\n+\n+   Copyright [yyyy] [name of copyright owner]\n+\n+   Licensed under the Apache License, Version 2.0 (the "License");\n+   you may not use this file except in compliance with the License.\n+   You may obtain a copy of the License at\n+\n+       http://www.apache.org/licenses/LICENSE-2.0\n+\n+   Unless required by applicable law or agreed to in writing, software\n+   distributed under the License is distributed on an "AS IS" BASIS,\n+   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n+   See the License for the specific language governing permissions and\n+   limitations under the License.\ndiff --git a/README.md b/README.md\nnew file mode 100644\nindex 0000000000000000000000000000000000000000..3bf040133e335ced65d3b4d53a36608c7a6697fc\n--- /dev/null\n+++ b/README.md\n@@ -0,0 +1 @@\n+# sub-test-repo\n\\ No newline at end of file\n\n\nCOMMIT:\t0ece4564ab5466ad2493718bdc4a75c02f666f15\nTREE:\tbe45f01cb60bcb59db6d4e14e22e8a798144da37\nDATE:\t2024-09-15T10:07:36+03:00\nAUTHOR:\tArtem Demidenko\twhenessel@icloud.com\t2024-09-15T10:07:36+03:00\nCOMMITTER:\tGitHub\tnoreply@github.com\t2024-09-15T10:07:36+03:00\nMESSAGE:\tUpdate README.md\nPARENTS:\t2167055f7bdc664f70111c47119ecf7dbdf3157f\n\n:100644 100644 3bf040133e335ced65d3b4d53a36608c7a6697fc 6bf4afb0a3f36a132a46dd615303d21b14923edf M\tREADME.md\n3\t1\tREADME.md\n\ndiff --git a/README.md b/README.md\nindex 3bf040133e335ced65d3b4d53a36608c7a6697fc..6bf4afb0a3f36a132a46dd615303d21b14923edf 100644\n--- a/README.md\n+++ b/README.md\n@@ -1 +1,3 @@\n-# sub-test-repo\n\\ No newline at end of file\n+# sub-test-repo\n+\n+## Edit One\nEntering \'deps/sub_test_repo_2\'\n\nCOMMIT:\t936bb692fd9f836242440f7f380feb09d69c0f2d\nTREE:\t84a108d8b8f9f745ccedaff4f1f13409ea3671f3\nDATE:\t2024-09-15T10:52:22+03:00\nAUTHOR:\tArtem Demidenko\twhenessel@icloud.com\t2024-09-15T10:52:22+03:00\nCOMMITTER:\tGitHub\tnoreply@github.com\t2024-09-15T10:52:22+03:00\nMESSAGE:\tInitial commit\nPARENTS:\t\n\n:000000 100644 0000000000000000000000000000000000000000 8ca399b2d7b52247b27b581b3dd4e80a89ac5f50 A\tREADME.md\n1\t0\tREADME.md\n\ndiff --git a/README.md b/README.md\nnew file mode 100644\nindex 0000000000000000000000000000000000000000..8ca399b2d7b52247b27b581b3dd4e80a89ac5f50\n--- /dev/null\n+++ b/README.md\n@@ -0,0 +1 @@\n+# sub-test-repo-2\n\\ No newline at end of file'
    )

    result = git_utils.parse_commits_from_text(text=submodules_commits)

    assert len(result) == 3


def test_parse_foreach_submodules_file_list():
    output = (
        "Entering 'deps/sub_test_repo'\n"
        ".gitignore\n"
        "LICENSE\n"
        "README.md\n"
        "Entering 'deps/sub_test_repo_2'\n"
        "README.md\n"
        "FILE NAME.txt"
    )
    result = git_utils.parse_files_foreach_submodules(output)
    assert len(result) == 5
