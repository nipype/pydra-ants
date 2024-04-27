import logging
import os
from packaging.version import Version, parse


logger = logging.getLogger(__name__)


class Info(PackageInfo):
    version_cmd = (
        os.path.join(os.getenv("ANTSPATH", ""), "antsRegistration") + " --version"
    )

    @staticmethod
    def parse_version(raw_info):
        for line in raw_info.splitlines():
            if line.startswith("ANTs Version: "):
                v_string = line.split()[2]
                break
        else:
            return None

        # -githash may or may not be appended
        v_string = v_string.split("-")[0]

        version = parse(v_string)

        # Known mislabeled versions
        if version.is_postrelease:
            if version.base_version == "2.1.0" and version.post >= 789:
                return "2.2.0"

        # Unless we know of a specific reason to re-version, we will
        # treat the base version (before pre/post/dev) as authoritative
        return version.base_version
