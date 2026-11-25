import sys
from .core import verify_all, to_markdown, to_html


def main(argv=None):
    a = sys.argv[1:] if argv is None else argv
    if a and a[0] == "verify":
        bad = verify_all()
        print("All cards verified." if not bad else "FAILED: " + ", ".join(bad))
        return 1 if bad else 0
    print(to_html() if a and a[0] == "html" else to_markdown())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
