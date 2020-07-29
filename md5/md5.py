import hashlib


def md5(filename) -> str:
    """Generates the md5 sum of a target file.
    The github-actions Ubuntu image does not contain md5 binary."""

    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', required=True, help='target file')
    args = parser.parse_args()

    print(md5(args.f))
