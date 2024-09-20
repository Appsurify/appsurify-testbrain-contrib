import re

RE_OCTAL_BYTE = re.compile(r"\\\\([0-9]{3})")


RE_COMMIT_DIFF = re.compile(
    r"^diff[ ]--git    [ ](?P<a_path_fallback>\"?[ab]/.+?\"?)[ ]"
    r"(?P<b_path_fallback>\"?[ab]/.+?\"?)\n(?:^old[ ]mode[ ]"
    r"(?P<old_mode>\\d+)\n   ^new[ ]mode[ ](?P<new_mode>\\d+)(?:\n|$))?"
    r"(?:^similarity[ ]index[ ]\\d+%\n   ^rename[ ]from[ ]"
    r"(?P<rename_from>.*)\n   ^rename[ ]to[ ](?P<rename_to>.*)"
    r"(?:\n|$))?(?:^new[ ]file[ ]mode[ ]"
    r"(?P<new_file_mode>.+)(?:\n|$))?(?:^deleted[ ]file[ ]mode[ ]"
    r"(?P<deleted_file_mode>.+)(?:\n|$))?"
    r"(?:^similarity[ ]index[ ]\\d+%\n   ^copy[ ]from[ ].*\n   ^copy[ ]to[ ]"
    r"(?P<copied_file_name>.*)(?:\n|$))?(?:^index[ ]"
    r"(?P<a_blob_id>[0-9A-Fa-f]+)    \.\.(?P<b_blob_id>[0-9A-Fa-f]+)[ ]?"
    r"(?P<b_mode>.+)?(?:\n|$))?(?:^---[ ]"
    r"(?P<a_path>[^\t\n\r\f\v]*)[\t\r\f\v]*(?:\n|$))?(?:^\+\+\+[ ]"
    r"(?P<b_path>[^\t\n\r\f\v]*)[\t\r\f\v]*(?:\n|$))?",
    re.VERBOSE | re.MULTILINE,
)


# RE_COMMIT_LIST = re.compile(
#     r"COMMIT:\t(?P<sha>[0-9A-Fa-f]+)\n"
#     r"TREE:\t(?P<tree>[0-9A-Fa-f]+)\n"
#     r"DATE:\t(?P<date>.*)\n"
#     r"AUTHOR:\t(?P<author>.+\t.+\t.*)\n"
#     r"COMMITTER:\t(?P<committer>.+\t.+\t.*)\n"
#     r"MESSAGE:\t(?P<message>.*)\n"
#     r"PARENTS:\t(?P<parents>.*)(\n{0,2})?"
#     r"(?P<raw>(?:^:.+\n)+)?"
#     r"(?P<numstats>(?:\d\t\d\t.+\n)+)?(\n{1,2})?"
#     r"(?P<patch>(?:diff[ ]--git(?:.+\n?)+)+)?",
#     re.MULTILINE | re.VERBOSE,
# )
# RE_COMMIT_LIST = re.compile(
#     r"^COMMIT:\t(?P<sha>[0-9A-Fa-f]{40})\n"
#     r"TREE:\t(?P<tree>[0-9A-Fa-f]{40})\n"
#     r"DATE:\t(?P<date>.+)\n"
#     r"AUTHOR:\t(?P<author>.+?\t.+?\t.+?)\n"
#     r"COMMITTER:\t(?P<committer>.+?\t.+?\t.+?)\n"
#     r"MESSAGE:\t(?P<message>.+)\n"
#     r"PARENTS:\t?(?P<parents>[0-9A-Fa-f]+(?:\s[0-9A-Fa-f]+)*)?\n"
#     r"(?P<raw>(?:^:.+\n)+)?"
#     r"(?P<numstats>(?:\d+\t\d+\t.+\n)+)?(?:\n{1,2})?"
#     r"(?P<patch>(?:(?!^COMMIT:).*\n?)+)?",
#     re.MULTILINE,
# )
RE_COMMIT_LIST = re.compile(
    r"^COMMIT:\s(?P<sha>[0-9A-Fa-f]{40})\n"
    r"TREE:\s(?P<tree>[0-9A-Fa-f]{40})\n"
    r"DATE:\s(?P<date>.+)\n"
    r"AUTHOR:\s(?P<author>.+?\t.+?\t.+?)\n"
    r"COMMITTER:\s(?P<committer>.+?\t.+?\t.+?)\n"
    r"MESSAGE:\s(?P<message>.+)\n"
    r"PARENTS:\s?(?P<parents>[0-9A-Fa-f]+(?:\s[0-9A-Fa-f]+)*)?\n{1,2}"
    r"(?P<raw>(?:^:.+\n)+)?"
    r"(?P<numstats>(?:\d+\t\d+\t.+\n)+)?(?:\n{1,2})?"
    r"(?P<patch>(?:(?!^COMMIT:).*\n?)+)?",
    re.MULTILINE,
)

RE_REPO_NAME_PATTERN = re.compile(r".*/([^/]+)/?")

RE_SUBMODULE_HEADER = re.compile(r"^Entering\s'([^']+)'\n", re.MULTILINE)

RE_SUBMODULE_FILES_PATTERN = re.compile(
    r"^Entering\s'(?P<path>[^']+)'\n(?P<files>(?:(?!^Entering).*\n?)*)",
    re.MULTILINE,
)
