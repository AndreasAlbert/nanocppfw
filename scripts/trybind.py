#!/usr/bin/env python
import sys
import PyBindings

def get_input_files():
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = []
        files.append("/home/albert/repos/nanocppfw/data/007E0986-34E9-9741-A447-957FF2F1982C.root");
        files.append("/home/albert/repos/nanocppfw/data/78341E3C-F2BD-A64E-95D6-550FCA8DDAD4.root");
        files.append("/home/albert/repos/nanocppfw/data/E4D76467-890E-E811-8523-FA163E3D9AF7.root");
    return files

def main():
    files = get_input_files()
    ana = PyBindings.HInvAnalyzer(files)
    ana.run()

if __name__ == "__main__":
    main()