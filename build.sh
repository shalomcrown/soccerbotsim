#!/bin/bash

protoc --python_out=src/main/python/soccer   --proto_path=src/main/protobuf/  src/main/protobuf/soccer.proto
