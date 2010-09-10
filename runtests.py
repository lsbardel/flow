
if __name__ == '__main__':
    import sys
    packages = None
    if len(sys.argv)>1:
        packages = sys.argv[1]
    from examples.jfsite.test import run
    run(packages)
