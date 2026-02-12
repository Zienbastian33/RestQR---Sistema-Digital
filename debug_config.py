import os
import sys

print(f"Current working directory: {os.getcwd()}")
try:
    print(f"__file__: {__file__}")
except NameError:
    print("__file__ is not defined")

try:
    import config
    print(f"Config basedir: {config.basedir}")
    print("Config imported successfully")
except Exception as e:
    print(f"Error importing config: {e}")
